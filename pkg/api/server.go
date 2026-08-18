package api

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"rapid-message-sender/pkg/engine"
	"rapid-message-sender/pkg/net"
	"rapid-message-sender/pkg/version"
)

type Server struct {
	embedFS embed.FS
	worker  *engine.Worker

	mu                  sync.RWMutex
	sseClients          map[chan string]bool
	lastHeartbeat       time.Time
	hasFirstHeartbeat   bool
	onShutdown          func()
}

func NewServer(embedFS embed.FS) *Server {
	s := &Server{
		embedFS:       embedFS,
		sseClients:    make(map[chan string]bool),
		lastHeartbeat: time.Now(),
	}
	s.worker = engine.NewWorker(s)
	s.startHeartbeatMonitor()
	return s
}

func (s *Server) SetOnShutdown(fn func()) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.onShutdown = fn
}

func (s *Server) triggerShutdown() {
	s.mu.RLock()
	fn := s.onShutdown
	s.mu.RUnlock()

	if fn != nil {
		fn()
	} else {
		go func() {
			time.Sleep(100 * time.Millisecond)
			os.Exit(0)
		}()
	}
}

func (s *Server) startHeartbeatMonitor() {
	go func() {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()

		for range ticker.C {
			s.mu.RLock()
			hasFirst := s.hasFirstHeartbeat
			last := s.lastHeartbeat
			s.mu.RUnlock()

			// If the frontend has connected and sent its first heartbeat, but hasn't sent any heartbeat for > 5 seconds, exit backend.
			if hasFirst && time.Since(last) > 5*time.Second {
				fmt.Println("[Backend] Frontend window closed (heartbeat timeout). Exiting process...")
				s.triggerShutdown()
				return
			}
		}
	}()
}

// Log satisfies engine.LogBroadcaster interface
func (s *Server) Log(level, message string) {
	ts := time.Now().Format("15:04:05")
	payload := fmt.Sprintf(`{"type":"log","level":%q,"message":%q,"timestamp":%q}`, level, message, ts)
	s.broadcastSSE(payload)
}

// UpdateStats satisfies engine.LogBroadcaster interface
func (s *Server) UpdateStats(stats engine.Stats) {
	statsBytes, _ := json.Marshal(stats)
	payload := fmt.Sprintf(`{"type":"stats","data":%s}`, string(statsBytes))
	s.broadcastSSE(payload)
}

func (s *Server) broadcastSSE(data string) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	sseMsg := fmt.Sprintf("data: %s\n\n", data)
	for clientChan := range s.sseClients {
		select {
		case clientChan <- sseMsg:
		default:
		}
	}
}

func (s *Server) SetupRoutes() *http.ServeMux {
	mux := http.NewServeMux()

	// Frontend root and dynamic template injection for index.html
	mux.HandleFunc("/", s.handleRoot)

	// API endpoints
	mux.HandleFunc("/api/version", s.handleVersion)
	mux.HandleFunc("/api/start", s.handleStart)
	mux.HandleFunc("/api/stop", s.handleStop)
	mux.HandleFunc("/api/events", s.handleEvents)
	mux.HandleFunc("/api/update", s.handleUpdate)
	mux.HandleFunc("/api/heartbeat", s.handleHeartbeat)
	mux.HandleFunc("/api/shutdown", s.handleShutdown)

	return mux
}

func (s *Server) handleRoot(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Path
	if path == "/" || path == "/index.html" {
		htmlBytes, err := fs.ReadFile(s.embedFS, "frontend/index.html")
		if err != nil {
			http.Error(w, "Failed to load index.html template", http.StatusInternalServerError)
			return
		}
		rendered := strings.ReplaceAll(string(htmlBytes), "{{VERSION}}", version.AppVersion)
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write([]byte(rendered))
		return
	}

	subFS, err := fs.Sub(s.embedFS, "frontend")
	if err != nil {
		http.NotFound(w, r)
		return
	}
	http.FileServer(http.FS(subFS)).ServeHTTP(w, r)
}

func (s *Server) handleVersion(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"version": version.AppVersion,
	})
}

func (s *Server) handleHeartbeat(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	s.lastHeartbeat = time.Now()
	s.hasFirstHeartbeat = true
	s.mu.Unlock()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func (s *Server) handleShutdown(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "shutting_down"})
	fmt.Println("[Backend] Immediate shutdown signal received from window.")
	s.triggerShutdown()
}

func (s *Server) handleStart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var cfg engine.Config
	if err := json.NewDecoder(r.Body).Decode(&cfg); err != nil {
		http.Error(w, fmt.Sprintf("Invalid request payload: %v", err), http.StatusBadRequest)
		return
	}

	if err := s.worker.Start(cfg); err != nil {
		http.Error(w, err.Error(), http.StatusConflict)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "started"})
}

func (s *Server) handleStop(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	s.worker.Stop()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "stopped"})
}

func (s *Server) handleEvents(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	clientChan := make(chan string, 50)

	s.mu.Lock()
	s.sseClients[clientChan] = true
	s.mu.Unlock()

	defer func() {
		s.mu.Lock()
		delete(s.sseClients, clientChan)
		s.mu.Unlock()
		close(clientChan)
	}()

	initLog := fmt.Sprintf(`data: {"type":"log","level":"INFO","message":"Connected to Server-Sent Events stream (%s).","timestamp":%q}`+"\n\n", version.AppVersion, time.Now().Format("15:04:05"))
	w.Write([]byte(initLog))
	if f, ok := w.(http.Flusher); ok {
		f.Flush()
	}

	ctx := r.Context()
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-clientChan:
			_, err := w.Write([]byte(msg))
			if err != nil {
				return
			}
			if f, ok := w.(http.Flusher); ok {
				f.Flush()
			}
		}
	}
}

func (s *Server) handleUpdate(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	info, err := net.CheckUpdate()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(info)
}

func (s *Server) Close() {
	s.worker.Close()
}
