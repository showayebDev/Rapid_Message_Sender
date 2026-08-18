package engine

import (
	"context"
	"fmt"
	"sync"
	"time"

	"rapid-message-sender/pkg/automation"
)

type Config struct {
	Message        string `json:"message"`
	RepeatCount    int    `json:"repeatCount"`
	IntervalMs     int    `json:"intervalMs"`
	StartDelaySec  int    `json:"startDelaySec"`
	TriggerKey     string `json:"triggerKey"`     // Enter, Ctrl+Enter, Shift+Enter, None
	AppendCounter  bool   `json:"appendCounter"`  // Enable counter
	CounterPosition string `json:"counterPosition"`// suffix or prefix
	CounterSeparator string `json:"counterSeparator"`// e.g. " ", "#", "_", "-", ":"
}

type Stats struct {
	Dispatched int     `json:"dispatched"`
	Total      int     `json:"total"`
	ElapsedSec float64 `json:"elapsedSec"`
	SpeedMsgSec float64 `json:"speedMsgSec"`
	Status     string  `json:"status"` // Idle, Counting Down, Running, Completed, Aborted
}

type LogBroadcaster interface {
	Log(level, message string)
	UpdateStats(stats Stats)
}

type Worker struct {
	mu          sync.Mutex
	running     bool
	cancel      context.CancelFunc
	driver      automation.Driver
	broadcaster LogBroadcaster
	stopHotkey  chan struct{}
}

func NewWorker(broadcaster LogBroadcaster) *Worker {
	d := automation.NewDriver()
	w := &Worker{
		driver:      d,
		broadcaster: broadcaster,
		stopHotkey:  make(chan struct{}),
	}
	// Start global Ctrl+Q listener
	w.driver.StartHotkeyListener(w.stopHotkey, func() {
		w.StopWithReason("Global hotkey Ctrl+Q emergency abort triggered!")
	})
	return w
}

func (w *Worker) IsRunning() bool {
	w.mu.Lock()
	defer w.mu.Unlock()
	return w.running
}

func (w *Worker) Stop() {
	w.StopWithReason("Stopped by user command.")
}

func (w *Worker) StopWithReason(reason string) {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.running && w.cancel != nil {
		w.cancel()
		w.running = false
		if w.broadcaster != nil {
			w.broadcaster.Log("WARNING", fmt.Sprintf("🛑 %s", reason))
		}
	}
}

func (w *Worker) Start(cfg Config) error {
	w.mu.Lock()
	if w.running {
		w.mu.Unlock()
		return fmt.Errorf("worker is already running")
	}

	ctx, cancel := context.WithCancel(context.Background())
	w.cancel = cancel
	w.running = true
	w.mu.Unlock()

	// Enforce 200 ms minimum safety floor
	if cfg.IntervalMs < 200 {
		cfg.IntervalMs = 200
		if w.broadcaster != nil {
			w.broadcaster.Log("WARNING", "Interval automatically locked to 200 ms safety floor.")
		}
	}
	if cfg.RepeatCount <= 0 {
		cfg.RepeatCount = 1
	}

	go w.runLoop(ctx, cfg)
	return nil
}

func (w *Worker) runLoop(ctx context.Context, cfg Config) {
	defer func() {
		w.mu.Lock()
		w.running = false
		w.mu.Unlock()
		_ = w.driver.WipeClipboard()
	}()

	// Start Delay Countdown
	if cfg.StartDelaySec > 0 {
		if w.broadcaster != nil {
			w.broadcaster.Log("INFO", fmt.Sprintf("⏳ Countdown started: %d seconds before dispatch...", cfg.StartDelaySec))
		}
		for i := cfg.StartDelaySec; i > 0; i-- {
			select {
			case <-ctx.Done():
				w.emitStats(0, cfg.RepeatCount, 0, 0, "Aborted")
				return
			default:
				w.emitStats(0, cfg.RepeatCount, 0, 0, fmt.Sprintf("Starting in %ds", i))
				time.Sleep(1 * time.Second)
			}
		}
	}

	if w.broadcaster != nil {
		w.broadcaster.Log("SUCCESS", "🚀 Dispatch sequence initiated!")
	}

	startTime := time.Now()
	dispatched := 0

	for i := 1; i <= cfg.RepeatCount; i++ {
		select {
		case <-ctx.Done():
			elapsed := time.Since(startTime).Seconds()
			speed := 0.0
			if elapsed > 0 {
				speed = float64(dispatched) / elapsed
			}
			w.emitStats(dispatched, cfg.RepeatCount, elapsed, speed, "Aborted")
			return
		default:
		}

		// Mouse Corner (0,0) Fail-Safe Check
		pt, err := w.driver.GetCursorPos()
		if err == nil && pt.X == 0 && pt.Y == 0 {
			if w.broadcaster != nil {
				w.broadcaster.Log("ERROR", "🚨 Emergency Fail-Safe: Mouse touched screen corner (0,0)! Aborting.")
			}
			w.StopWithReason("Hardware mouse corner fail-safe triggered.")
			w.emitStats(dispatched, cfg.RepeatCount, time.Since(startTime).Seconds(), 0, "Aborted")
			return
		}

		// Format message content with optional counter
		msgText := cfg.Message
		if cfg.AppendCounter {
			counterStr := fmt.Sprintf("%d", i)
			sep := cfg.CounterSeparator
			if cfg.CounterPosition == "prefix" {
				msgText = fmt.Sprintf("%s%s%s", counterStr, sep, cfg.Message)
			} else {
				msgText = fmt.Sprintf("%s%s%s", cfg.Message, sep, counterStr)
			}
		}

		// Set clipboard text
		if err := w.driver.SetClipboardText(msgText); err != nil {
			if w.broadcaster != nil {
				w.broadcaster.Log("ERROR", fmt.Sprintf("Failed to set clipboard: %v", err))
			}
		}

		// Read-back verification
		readBack, err := w.driver.GetClipboardText()
		if err != nil || readBack != msgText {
			if w.broadcaster != nil {
				w.broadcaster.Log("WARNING", fmt.Sprintf("[%d/%d] Clipboard verification mismatch, retrying write...", i, cfg.RepeatCount))
			}
			_ = w.driver.SetClipboardText(msgText)
		}

		// Paste & Trigger Key
		if err := w.driver.Paste(); err != nil {
			if w.broadcaster != nil {
				w.broadcaster.Log("ERROR", fmt.Sprintf("Paste failed: %v", err))
			}
		}

		time.Sleep(15 * time.Millisecond)

		if err := w.driver.PressKey(cfg.TriggerKey); err != nil {
			if w.broadcaster != nil {
				w.broadcaster.Log("ERROR", fmt.Sprintf("Trigger key failed: %v", err))
			}
		}

		dispatched++
		elapsed := time.Since(startTime).Seconds()
		speed := 0.0
		if elapsed > 0 {
			speed = float64(dispatched) / elapsed
		}

		w.emitStats(dispatched, cfg.RepeatCount, elapsed, speed, "Running")

		if w.broadcaster != nil && (dispatched%5 == 0 || dispatched == cfg.RepeatCount || dispatched == 1) {
			w.broadcaster.Log("INFO", fmt.Sprintf("Dispatched message [%d/%d] (Speed: %.1f msg/s)", dispatched, cfg.RepeatCount, speed))
		}

		// Sleep for interval with fine-grained abort checks
		sleepDuration := time.Duration(cfg.IntervalMs) * time.Millisecond
		intervalStart := time.Now()
		for time.Since(intervalStart) < sleepDuration {
			select {
			case <-ctx.Done():
				w.emitStats(dispatched, cfg.RepeatCount, time.Since(startTime).Seconds(), speed, "Aborted")
				return
			default:
				// Intermittent corner check during sleep
				if pt, err := w.driver.GetCursorPos(); err == nil && pt.X == 0 && pt.Y == 0 {
					if w.broadcaster != nil {
						w.broadcaster.Log("ERROR", "🚨 Emergency Fail-Safe: Mouse touched screen corner (0,0)! Aborting.")
					}
					w.StopWithReason("Hardware mouse corner fail-safe triggered.")
					w.emitStats(dispatched, cfg.RepeatCount, time.Since(startTime).Seconds(), speed, "Aborted")
					return
				}
				time.Sleep(20 * time.Millisecond)
			}
		}
	}

	finalElapsed := time.Since(startTime).Seconds()
	finalSpeed := 0.0
	if finalElapsed > 0 {
		finalSpeed = float64(dispatched) / finalElapsed
	}

	w.emitStats(dispatched, cfg.RepeatCount, finalElapsed, finalSpeed, "Completed")
	if w.broadcaster != nil {
		w.broadcaster.Log("SUCCESS", fmt.Sprintf("🎉 Automation Completed! Total Dispatched: %d messages in %.2f seconds.", dispatched, finalElapsed))
	}
}

func (w *Worker) emitStats(dispatched, total int, elapsedSec, speedMsgSec float64, status string) {
	if w.broadcaster != nil {
		w.broadcaster.UpdateStats(Stats{
			Dispatched:  dispatched,
			Total:       total,
			ElapsedSec:  elapsedSec,
			SpeedMsgSec: speedMsgSec,
			Status:      status,
		})
	}
}

func (w *Worker) Close() {
	close(w.stopHotkey)
}
