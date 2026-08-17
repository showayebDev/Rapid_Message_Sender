#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "core/worker.h"
#include "net/updater.h"
#include "core/hotkey_listener.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

private slots:
    void onStartClicked();
    void onStopClicked();
    void onResetClicked();
    void onTemplateChanged(int index);
    void onCheckUpdatesClicked();
    void onNavWorkspaceClicked();
    void onNavDocClicked();

    void onWorkerCountdown(int secondsRemaining);
    void onWorkerProgress(int sentCount, int totalCount);
    void onWorkerStats(int sentCount, double elapsedSec, double messagesPerSec);
    void onWorkerLog(const QString &msg, const QString &level);
    void onWorkerFinished(bool aborted, const QString &reason);
    void onGlobalHotkeyTriggered();

private:
    Ui::MainWindow *ui;
    AutomationWorker *m_worker = nullptr;
    AutoUpdater *m_updater = nullptr;
    GlobalHotkeyFilter *m_hotkeyFilter = nullptr;

    void setupUiDefaults();
    void setupDocumentationPage();
    void applyDarkStyleSheet();
    AutomationConfig buildConfigFromUi();
    void setControlsEnabled(bool enabled);
};

#endif // MAINWINDOW_H
