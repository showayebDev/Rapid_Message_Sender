#ifndef HOTKEY_LISTENER_H
#define HOTKEY_LISTENER_H

#include <QAbstractNativeEventFilter>
#include <QObject>
#include <windows.h>

class GlobalHotkeyFilter : public QObject, public QAbstractNativeEventFilter {
    Q_OBJECT
public:
    explicit GlobalHotkeyFilter(QObject *parent = nullptr);
    ~GlobalHotkeyFilter() override;

    bool registerCtrlQ(HWND hWnd);
    void unregisterCtrlQ();

    bool nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) override;

signals:
    void hotkeyPressed();

private:
    HWND m_hWnd = nullptr;
    int m_hotkeyId = 1001;
    bool m_registered = false;
};

#endif // HOTKEY_LISTENER_H
