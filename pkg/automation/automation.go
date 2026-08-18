package automation

import "errors"

// Point represents screen coordinates.
type Point struct {
	X int
	Y int
}

// Driver defines the OS-level input and clipboard automation interface.
type Driver interface {
	SetClipboardText(text string) error
	GetClipboardText() (string, error)
	WipeClipboard() error
	Paste() error
	PressKey(triggerKey string) error
	GetCursorPos() (Point, error)
	RegisterHotkey(id int, mod uint32, vk uint32) error
	UnregisterHotkey(id int) error
	StartHotkeyListener(stopCh <-chan struct{}, onCtrlQ func())
}

var ErrNotImplemented = errors.New("automation feature not implemented on this OS")
