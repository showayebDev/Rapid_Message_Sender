#include "worker.h"
#include <QDebug>

AutomationWorker::AutomationWorker(const AutomationConfig &config, QObject *parent)
    : QThread(parent)
    , m_config(config)
{
}

void AutomationWorker::requestStop()
{
    m_stopRequested.storeRelaxed(true);
}

bool AutomationWorker::isStopRequested() const
{
    return m_stopRequested.loadRelaxed();
}

bool AutomationWorker::checkFailSafe()
{
    POINT pt;
    if (GetCursorPos(&pt)) {
        if (pt.x <= 5 && pt.y <= 5) {
            return true;
        }
    }
    return false;
}

QString AutomationWorker::formatMessageWithCounter(int index)
{
    if (!m_config.appendCounter) {
        return m_config.baseMessage;
    }

    QString sepStr = " ";
    switch (m_config.separator) {
        case SeparatorType::Space: sepStr = " "; break;
        case SeparatorType::Semicolon: sepStr = " ; "; break;
        case SeparatorType::Dash: sepStr = " - "; break;
        case SeparatorType::Hash: sepStr = " #"; break;
    }

    if (m_config.counterAsPrefix) {
        return QString("#%1%2%3").arg(index).arg(sepStr).arg(m_config.baseMessage);
    } else {
        return QString("%1%2%3").arg(m_config.baseMessage).arg(sepStr).arg(index);
    }
}

void AutomationWorker::pressEnterKey()
{
    INPUT inputs[2] = {};
    inputs[0].type = INPUT_KEYBOARD;
    inputs[0].ki.wVk = VK_RETURN;

    inputs[1].type = INPUT_KEYBOARD;
    inputs[1].ki.wVk = VK_RETURN;
    inputs[1].ki.dwFlags = KEYEVENTF_KEYUP;

    SendInput(2, inputs, sizeof(INPUT));
}

bool AutomationWorker::sendDirectTyping(const QString &text)
{
    std::wstring wstr = text.toStdWString();
    for (wchar_t ch : wstr) {
        if (m_stopRequested.loadRelaxed() || checkFailSafe()) return false;

        if (ch == L'\r') continue;

        if (ch == L'\n') {
            pressEnterKey();
        } else {
            INPUT inputs[2] = {};
            inputs[0].type = INPUT_KEYBOARD;
            inputs[0].ki.wScan = ch;
            inputs[0].ki.dwFlags = KEYEVENTF_UNICODE;

            inputs[1].type = INPUT_KEYBOARD;
            inputs[1].ki.wScan = ch;
            inputs[1].ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP;

            SendInput(2, inputs, sizeof(INPUT));
        }
        QThread::msleep(5);
    }
    return true;
}

bool AutomationWorker::sendClipboardPaste(const QString &text)
{
    std::wstring wstr = text.toStdWString();
    size_t sizeInBytes = (wstr.length() + 1) * sizeof(wchar_t);

    bool opened = false;
    for (int retry = 0; retry < 5; ++retry) {
        if (OpenClipboard(nullptr)) {
            opened = true;
            break;
        }
        QThread::msleep(10);
    }
    if (!opened) {
        emit logMessage("Failed to open Windows Clipboard.", "ERROR");
        return false;
    }

    EmptyClipboard();

    HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, sizeInBytes);
    if (!hMem) {
        CloseClipboard();
        emit logMessage("Failed to allocate global memory for clipboard.", "ERROR");
        return false;
    }

    void *pMem = GlobalLock(hMem);
    if (!pMem) {
        GlobalFree(hMem);
        CloseClipboard();
        emit logMessage("Failed to lock global memory.", "ERROR");
        return false;
    }

    memcpy(pMem, wstr.c_str(), sizeInBytes);
    GlobalUnlock(hMem);

    if (!SetClipboardData(CF_UNICODETEXT, hMem)) {
        GlobalFree(hMem);
        CloseClipboard();
        emit logMessage("Failed to set clipboard data.", "ERROR");
        return false;
    }

    HANDLE hRead = GetClipboardData(CF_UNICODETEXT);
    bool verified = false;
    if (hRead) {
        wchar_t *pRead = static_cast<wchar_t*>(GlobalLock(hRead));
        if (pRead) {
            if (wcscmp(pRead, wstr.c_str()) == 0) {
                verified = true;
            }
            GlobalUnlock(hRead);
        }
    }
    CloseClipboard();

    if (!verified) {
        emit logMessage("Clipboard read-back verification failed!", "WARNING");
    }

    QThread::msleep(20);

    INPUT inputs[4] = {};
    inputs[0].type = INPUT_KEYBOARD;
    inputs[0].ki.wVk = VK_CONTROL;

    inputs[1].type = INPUT_KEYBOARD;
    inputs[1].ki.wVk = 'V';

    inputs[2].type = INPUT_KEYBOARD;
    inputs[2].ki.wVk = 'V';
    inputs[2].ki.dwFlags = KEYEVENTF_KEYUP;

    inputs[3].type = INPUT_KEYBOARD;
    inputs[3].ki.wVk = VK_CONTROL;
    inputs[3].ki.dwFlags = KEYEVENTF_KEYUP;

    SendInput(4, inputs, sizeof(INPUT));
    return true;
}

void AutomationWorker::run()
{
    emit logMessage(QString("Automation starting in %1 seconds...").arg(m_config.startDelaySec), "INFO");

    for (int sec = m_config.startDelaySec; sec > 0; --sec) {
        if (m_stopRequested.loadRelaxed()) {
            emit finishedAutomation(true, "Aborted during countdown delay.");
            return;
        }
        if (checkFailSafe()) {
            emit finishedAutomation(true, "Aborted: Mouse cursor moved to top-left fail-safe corner (0,0).");
            return;
        }
        emit countdownTick(sec);
        QThread::msleep(1000);
    }
    emit countdownTick(0);

    emit logMessage("Dispatching messages...", "SUCCESS");

    QElapsedTimer timer;
    timer.start();

    int sentCount = 0;
    int targetCount = m_config.repeatCount;
    int index = 1;

    int safeInterval = qMax(100, m_config.intervalMs);

    while (!m_stopRequested.loadRelaxed()) {
        if (targetCount > 0 && sentCount >= targetCount) {
            break;
        }

        if (checkFailSafe()) {
            emit logMessage("EMERGENCY ABORT TRIGGERED: Mouse at top-left (0,0)!", "ERROR");
            emit finishedAutomation(true, "Mouse hardware fail-safe activated.");
            return;
        }

        QString finalMsg = formatMessageWithCounter(index);

        bool success = false;
        if (m_config.engineMode == EngineMode::DirectTyping) {
            success = sendDirectTyping(finalMsg);
        } else {
            success = sendClipboardPaste(finalMsg);
        }

        if (!success && (m_stopRequested.loadRelaxed() || checkFailSafe())) {
            emit finishedAutomation(true, "Aborted by user or mouse fail-safe.");
            return;
        }

        if (m_config.autoSendEnter) {
            QThread::msleep(20);
            pressEnterKey();
        }

        sentCount++;
        index++;

        double elapsedSec = timer.elapsed() / 1000.0;
        double rate = (elapsedSec > 0) ? (sentCount / elapsedSec) : 0.0;

        emit progressUpdated(sentCount, targetCount);
        emit statsUpdated(sentCount, elapsedSec, rate);

        emit logMessage(QString("[%1/%2] Sent: %3")
                            .arg(sentCount)
                            .arg(targetCount > 0 ? QString::number(targetCount) : "∞")
                            .arg(finalMsg), "INFO");

        int waited = 0;
        while (waited < safeInterval) {
            if (m_stopRequested.loadRelaxed()) {
                emit finishedAutomation(true, "Stopped by user request.");
                return;
            }
            if (checkFailSafe()) {
                emit logMessage("EMERGENCY ABORT TRIGGERED: Mouse at top-left (0,0)!", "ERROR");
                emit finishedAutomation(true, "Mouse hardware fail-safe activated.");
                return;
            }
            int sleepChunk = qMin(50, safeInterval - waited);
            QThread::msleep(sleepChunk);
            waited += sleepChunk;
        }
    }

    double elapsedSec = timer.elapsed() / 1000.0;
    double rate = (elapsedSec > 0) ? (sentCount / elapsedSec) : 0.0;
    emit statsUpdated(sentCount, elapsedSec, rate);

    emit logMessage(QString("Automation completed! Total sent: %1 in %2 seconds.").arg(sentCount).arg(elapsedSec, 0, 'f', 1), "SUCCESS");
    emit finishedAutomation(false, "Completed successfully.");
}
