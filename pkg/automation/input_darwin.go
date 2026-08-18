//go:build darwin

package automation

import (
	"bytes"
	"os/exec"
)

type DarwinDriver struct{}

func NewDriver() Driver {
	return &DarwinDriver{}
}

func (d *DarwinDriver) SetClipboardText(text string) error {
	cmd := exec.Command("pbcopy")
	cmd.Stdin = bytes.NewBufferString(text)
	return cmd.Run()
}

func (d *DarwinDriver) GetClipboardText() (string, error) {
	cmd := exec.Command("pbpaste")
	out, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func (d *DarwinDriver) WipeClipboard() error {
	return d.SetClipboardText("")
}

func (d *DarwinDriver) Paste() error {
	script := `tell application "System Events" to keystroke "v" using command down`
	return exec.Command("osascript", "-e", script).Run()
}

func (d *DarwinDriver) PressKey(triggerKey string) error {
	switch triggerKey {
	case "Enter":
		script := `tell application "System Events" to key code 36`
		return exec.Command("osascript", "-e", script).Run()
	case "Ctrl+Enter":
		script := `tell application "System Events" to key code 36 using control down`
		return exec.Command("osascript", "-e", script).Run()
	case "Shift+Enter":
		script := `tell application "System Events" to key code 36 using shift down`
		return exec.Command("osascript", "-e", script).Run()
	case "None":
		return nil
	default:
		script := `tell application "System Events" to key code 36`
		return exec.Command("osascript", "-e", script).Run()
	}
}

func (d *DarwinDriver) GetCursorPos() (Point, error) {
	return Point{X: -1, Y: -1}, nil
}

func (d *DarwinDriver) RegisterHotkey(id int, mod uint32, vk uint32) error {
	return nil
}

func (d *DarwinDriver) UnregisterHotkey(id int) error {
	return nil
}

func (d *DarwinDriver) StartHotkeyListener(stopCh <-chan struct{}, onCtrlQ func()) {
	go func() {
		<-stopCh
	}()
}
