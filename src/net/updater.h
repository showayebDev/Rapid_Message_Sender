#ifndef UPDATER_H
#define UPDATER_H

#include <QObject>
#include <QDialog>
#include <QLabel>
#include <QTextEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QProgressDialog>
#include <QMessageBox>
#include <QWidget>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QCoreApplication>
#include <QDir>
#include <QProcess>

class UpdateDialog : public QDialog {
    Q_OBJECT
public:
    UpdateDialog(QWidget *parent, const QString &latestTag, const QString &currentVersion, const QString &releaseNotes);
};

class AutoUpdater : public QObject {
    Q_OBJECT
public:
    explicit AutoUpdater(QWidget *parentWidget, const QString &currentVersion);
    void checkForUpdates(bool silentCheck = false);

signals:
    void checkFinished(bool hasUpdate, const QString &latestTag, const QString &releaseNotes);

private slots:
    void onReleaseInfoDownloaded();
    void onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal);
    void onDownloadFinished();

private:
    QWidget *m_parentWidget;
    QString m_currentVersion;
    bool m_silentCheck = false;
    QNetworkAccessManager m_netManager;
    QNetworkReply *m_releaseReply = nullptr;
    QNetworkReply *m_downloadReply = nullptr;
    QProgressDialog *m_progressDialog = nullptr;
    QFile *m_tempFile = nullptr;

    QString m_downloadUrl;
    QString m_latestTag;
    QString m_releaseNotes;
    QString m_tempExePath;

    bool isVersionNewer(const QString &latest, const QString &current);
    void downloadAndInstall();
    void createAndRunUpdateBatch(const QString &tempExePath);
};

#endif // UPDATER_H
