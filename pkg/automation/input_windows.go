//go:build windows

package automation

import "errors"
import (
	"runtime"
	"syscall"
	"time"
	"unsafe"
)

var (
	user32   = syscall.NewLazyDLL("user32.dll")
	kernel32 = syscall.NewLazyDLL("kernel32.dll")

	procOpenClipboard         = user32.NewProc("OpenClipboard")
	procCloseClipboard        = user32.NewProc("CloseClipboard")
	procEmptyClipboard        = user32.NewProc("EmptyClipboard")
	procSetClipboardData      = user32.NewProc("SetClipboardData")
	procGetClipboardData      = user32.NewProc("GetClipboardData")
	procSendInput             = user32.NewProc("SendInput")
	procGetCursorPos          = user32.NewProc("GetCursorPos")
	procRegisterHotKey        = user32.NewProc("RegisterHotKey")
	procUnregisterHotKey      = user32.NewProc("UnregisterHotKey")
	procGetMessageW           = user32.NewProc("GetMessageW")

	procGlobalAlloc           = kernel32.NewProc("GlobalAlloc")
	procGlobalLock            = kernel32.NewProc("GlobalLock")
	procGlobalUnlock          = kernel32.NewProc("GlobalUnlock")
	procGlobalFree            = kernel32.NewProc("GlobalFree")
)

const (
	CF_UNICODETEXT = 13
	GHND           = 0x0042

	INPUT_KEYBOARD = 1
	KEYEVENTF_KEYUP = 0x0002

	VK_SHIFT   = 0x10
	VK_CONTROL = 0x11
	VK_RETURN  = 0x0D
	VK_V       = 0x56
	VK_Q       = 0x51

	MOD_CONTROL = 0x0002
	WM_HOTKEY   = 0x0312
)

type KEYBDINPUT struct {
	WVk         uint16
	WScan       uint16
	DwFlags     uint32
	Time        uint32
	DwExtraInfo uintptr
}

type INPUT struct {
	Type uint32
	_    uint32
	Ki   KEYBDINPUT
	_    uint64
}

type POINT struct {
	X int32
	Y int32
}

type MSG struct {
	HWnd    uintptr
	Message uint32
	WParam  uintptr
	LParam  uintptr
	Time    uint32
	Pt      POINT
}

type WindowsDriver struct{}

func NewDriver() Driver {
	return &WindowsDriver{}
}

func (d *WindowsDriver) SetClipboardText(text string) error {
	utf16, err := syscall.UTF16FromString(text)
	if err != nil {
		return err
	}
	bytesCount := uintptr(len(utf16) * 2)

	hMem, _, _ := procGlobalAlloc.Call(GHND, bytesCount)
	if hMem == 0 {
		return errors.New("GlobalAlloc failed")
	}

	ptr, _, _ := procGlobalLock.Call(hMem)
	if ptr == 0 {
		procGlobalFree.Call(hMem)
		return errors.New("GlobalLock failed")
	}

	copy((*[1 << 29]uint16)(unsafe.Pointer(ptr))[:len(utf16)], utf16)
	procGlobalUnlock.Call(hMem)

	var opened bool
	for i := 0; i < 10; i++ {
		r, _, _ := procOpenClipboard.Call(0)
		if r != 0 {
			opened = true
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if !opened {
		procGlobalFree.Call(hMem)
		return errors.New("OpenClipboard failed")
	}
	defer procCloseClipboard.Call()

	procEmptyClipboard.Call()
	r, _, _ := procSetClipboardData.Call(CF_UNICODETEXT, hMem)
	if r == 0 {
		procGlobalFree.Call(hMem)
		return errors.New("SetClipboardData failed")
	}
	return nil
}

func (d *WindowsDriver) GetClipboardText() (string, error) {
	var opened bool
	for i := 0; i < 10; i++ {
		r, _, _ := procOpenClipboard.Call(0)
		if r != 0 {
			opened = true
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if !opened {
		return "", errors.New("OpenClipboard failed")
	}
	defer procCloseClipboard.Call()

	hMem, _, _ := procGetClipboardData.Call(CF_UNICODETEXT)
	if hMem == 0 {
		return "", nil
	}

	ptr, _, _ := procGlobalLock.Call(hMem)
	if ptr == 0 {
		return "", errors.New("GlobalLock failed")
	}
	defer procGlobalUnlock.Call(hMem)

	u16ptr := (*[1 << 29]uint16)(unsafe.Pointer(ptr))
	var length int
	for u16ptr[length] != 0 {
		length++
	}
	return syscall.UTF16ToString(u16ptr[:length]), nil
}

func (d *WindowsDriver) WipeClipboard() error {
	var opened bool
	for i := 0; i < 10; i++ {
		r, _, _ := procOpenClipboard.Call(0)
		if r != 0 {
			opened = true
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if !opened {
		return errors.New("OpenClipboard failed")
	}
	defer procCloseClipboard.Call()
	procEmptyClipboard.Call()
	return nil
}

func sendKeyInputs(inputs []INPUT) error {
	if len(inputs) == 0 {
		return nil
	}
	r, _, _ := procSendInput.Call(
		uintptr(len(inputs)),
		uintptr(unsafe.Pointer(&inputs[0])),
		unsafe.Sizeof(inputs[0]),
	)
	if r != uintptr(len(inputs)) {
		return errors.New("SendInput incomplete")
	}
	return nil
}

func (d *WindowsDriver) Paste() error {
	// Send Ctrl+V
	inputs := []INPUT{
		{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_CONTROL}},
		{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_V}},
		{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_V, DwFlags: KEYEVENTF_KEYUP}},
		{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_CONTROL, DwFlags: KEYEVENTF_KEYUP}},
	}
	return sendKeyInputs(inputs)
}

func (d *WindowsDriver) PressKey(triggerKey string) error {
	switch triggerKey {
	case "Enter":
		inputs := []INPUT{
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN, DwFlags: KEYEVENTF_KEYUP}},
		}
		return sendKeyInputs(inputs)
	case "Ctrl+Enter":
		inputs := []INPUT{
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_CONTROL}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN, DwFlags: KEYEVENTF_KEYUP}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_CONTROL, DwFlags: KEYEVENTF_KEYUP}},
		}
		return sendKeyInputs(inputs)
	case "Shift+Enter":
		inputs := []INPUT{
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_SHIFT}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN, DwFlags: KEYEVENTF_KEYUP}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_SHIFT, DwFlags: KEYEVENTF_KEYUP}},
		}
		return sendKeyInputs(inputs)
	case "None":
		return nil
	default:
		inputs := []INPUT{
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN}},
			{Type: INPUT_KEYBOARD, Ki: KEYBDINPUT{WVk: VK_RETURN, DwFlags: KEYEVENTF_KEYUP}},
		}
		return sendKeyInputs(inputs)
	}
}

func (d *WindowsDriver) GetCursorPos() (Point, error) {
	var pt POINT
	r, _, _ := procGetCursorPos.Call(uintptr(unsafe.Pointer(&pt)))
	if r == 0 {
		return Point{}, errors.New("GetCursorPos failed")
	}
	return Point{X: int(pt.X), Y: int(pt.Y)}, nil
}

func (d *WindowsDriver) RegisterHotkey(id int, mod uint32, vk uint32) error {
	r, _, _ := procRegisterHotKey.Call(0, uintptr(id), uintptr(mod), uintptr(vk))
	if r == 0 {
		return errors.New("RegisterHotKey failed")
	}
	return nil
}

func (d *WindowsDriver) UnregisterHotkey(id int) error {
	r, _, _ := procUnregisterHotKey.Call(0, uintptr(id))
	if r == 0 {
		return errors.New("UnregisterHotKey failed")
	}
	return nil
}

func (d *WindowsDriver) StartHotkeyListener(stopCh <-chan struct{}, onCtrlQ func()) {
	go func() {
		runtime.LockOSThread()
		defer runtime.UnlockOSThread()

		hotkeyID := 1
		// Register Ctrl+Q (MOD_CONTROL=2, VK_Q=0x51)
		err := d.RegisterHotkey(hotkeyID, MOD_CONTROL, VK_Q)
		if err == nil {
			defer d.UnregisterHotkey(hotkeyID)
		}

		var msg MSG
		for {
			select {
			case <-stopCh:
				return
			default:
				// PeekMessage/GetMessage loop with non-blocking check
				r, _, _ := procGetMessageW.Call(uintptr(unsafe.Pointer(&msg)), 0, 0, 0)
				if int32(r) > 0 {
					if msg.Message == WM_HOTKEY && msg.WParam == uintptr(hotkeyID) {
						if onCtrlQ != nil {
							onCtrlQ()
						}
					}
				} else {
					time.Sleep(50 * time.Millisecond)
				}
			}
		}
	}()
}
