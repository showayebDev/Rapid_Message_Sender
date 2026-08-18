//go:build linux

package automation

import (
	"bytes"
	"os/exec"
)

type LinuxDriver struct{}

func NewDriver() Driver {
	return &LinuxDriver{}
}

func (d *LinuxDriver) SetClipboardText(text string) error {
	cmd := exec.Command("xclip", "-selection", "clipboard")
	cmd.Stdin = bytes.NewBufferString(text)
	return cmd.Run()
}

func (d *LinuxDriver) GetClipboardText() (string, error) {
	cmd := exec.Command("xclip", "-selection", "clipboard", "-o")
	out, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func (d *LinuxDriver) WipeClipboard() error {
	return d.SetClipboardText("")
}

func (d *LinuxDriver) Paste() error {
	return exec.Command("xdotool", "key", "ctrl+v").Run()
}

func (d *LinuxDriver) PressKey(triggerKey string) error {
	switch triggerKey {
	case "Enter":
		return exec.Command("xdotool", "key", "Return").Run()
	case "Ctrl+Enter":
		return exec.Command("xdotool", "key", "ctrl+Return").Run()
	case "Shift+Enter":
		return exec.Command("xdotool", "key", "shift+Return").Run()
	case "None":
		return nil
	default:
		return exec.Command("xdotool", "key", "Return").Run()
	}
}

func (d *LinuxDriver) GetCursorPos() (Point, error) {
	return Point{X: -1, Y: -1}, nil
}

func (d *LinuxDriver) RegisterHotkey(id int, mod uint32, vk uint32) error {
	return nil
}

func (d *LinuxDriver) UnregisterHotkey(id int) error {
	return nil
}

func (d *LinuxDriver) StartHotkeyListener(stopCh <-chan struct{}, onCtrlQ func()) {
	// Stub for Linux hotkey listener
	go func() {
		<-stopCh
	}()
}
