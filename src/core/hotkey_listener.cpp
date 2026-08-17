#include "hotkey_listener.h"

GlobalHotkeyFilter::GlobalHotkeyFilter(QObject *parent)
    : QObject(parent)
{
}

GlobalHotkeyFilter::~GlobalHotkeyFilter()
{
    unregisterCtrlQ();
}

bool GlobalHotkeyFilter::registerCtrlQ(HWND hWnd)
{
    m_hWnd = hWnd;
    m_registered = RegisterHotKey(m_hWnd, m_hotkeyId, MOD_CONTROL, 'Q');
    return m_registered;
}

void GlobalHotkeyFilter::unregisterCtrlQ()
{
    if (m_registered && m_hWnd) {
        UnregisterHotKey(m_hWnd, m_hotkeyId);
        m_registered = false;
    }
}

bool GlobalHotkeyFilter::nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result)
{
    Q_UNUSED(result);
    if (eventType == "windows_generic_MSG") {
        MSG *msg = static_cast<MSG*>(message);
        if (msg->message == WM_HOTKEY) {
            if (msg->wParam == static_cast<WPARAM>(m_hotkeyId)) {
                emit hotkeyPressed();
                return true;
            }
        }
    }
    return false;
}
