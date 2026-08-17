#ifndef WORKER_H
#define WORKER_H

#include <QThread>
#include <QString>
#include <QAtomicInteger>
#include <QElapsedTimer>
#include <windows.h>

enum class EngineMode {
    DirectTyping = 0,
    ClipboardCopyPaste = 1
};

enum class SeparatorType {
    Space = 0,
    Semicolon = 1,
    Dash = 2,
    Hash = 3
};

struct AutomationConfig {
    QString baseMessage;
    EngineMode engineMode = EngineMode::DirectTyping;
    int intervalMs = 1000;
    int startDelaySec = 5;
    int repeatCount = 10;
    bool appendCounter = true;
    bool counterAsPrefix = false;
    SeparatorType separator = SeparatorType::Space;
    bool autoSendEnter = true;
};

class AutomationWorker : public QThread {
    Q_OBJECT
public:
    explicit AutomationWorker(const AutomationConfig &config, QObject *parent = nullptr);
    void requestStop();
    bool isStopRequested() const;

signals:
    void countdownTick(int secondsRemaining);
    void progressUpdated(int sentCount, int totalCount);
    void statsUpdated(int sentCount, double elapsedSec, double messagesPerSec);
    void logMessage(const QString &msg, const QString &level);
    void finishedAutomation(bool aborted, const QString &reason);

protected:
    void run() override;

private:
    AutomationConfig m_config;
    QAtomicInteger<bool> m_stopRequested{false};

    bool checkFailSafe();
    bool sendDirectTyping(const QString &text);
    bool sendClipboardPaste(const QString &text);
    void pressEnterKey();
    QString formatMessageWithCounter(int index);
};

#endif // WORKER_H
