#include "updater.h"
#include <QNetworkRequest>
#include <QUrl>
#include <QStandardPaths>
#include <QVersionNumber>
#include <QDebug>

UpdateDialog::UpdateDialog(QWidget *parent, const QString &latestTag, const QString &currentVersion, const QString &releaseNotes)
    : QDialog(parent)
{
    setWindowTitle("New Version Available!");
    setWindowFlags(windowFlags() | Qt::WindowMinMaxButtonsHint);
    setMinimumSize(560, 420);
    resize(640, 500);

    setStyleSheet(R"(
        QDialog {
            background-color: #0D1019;
            color: #E2E8F0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QLabel#lblHeader {
            font-size: 16px;
            font-weight: bold;
            color: #38BDF8;
        }
        QLabel#lblVersionInfo {
            font-size: 13px;
            color: #94A3B8;
        }
        QLabel#lblChangelogTitle {
            font-size: 13px;
            font-weight: bold;
            color: #E2E8F0;
        }
        QTextEdit#textChangelog {
            background-color: #131724;
            color: #F1F5F9;
            border: 1px solid #1E2638;
            border-radius: 8px;
            padding: 10px;
            font-size: 13px;
        }
        QPushButton#btnUpdate {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00B4DB, stop:1 #0083B0);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton#btnUpdate:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C6FF, stop:1 #0072FF);
        }
        QPushButton#btnLater {
            background-color: #1E2638;
            color: #E2E8F0;
            border: 1px solid #2D374D;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton#btnLater:hover {
            background-color: #28334A;
        }
    )");

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(18, 18, 18, 18);
    mainLayout->setSpacing(12);

    QLabel *lblHeader = new QLabel(QString("🚀 A new version (%1) of Rapid Message Sender is available!").arg(latestTag), this);
    lblHeader->setObjectName("lblHeader");

    QLabel *lblVersionInfo = new QLabel(QString("Installed Version: %1   →   Latest Version: %2").arg(currentVersion).arg(latestTag), this);
    lblVersionInfo->setObjectName("lblVersionInfo");

    QLabel *lblChangelogTitle = new QLabel("Changelog & Release Notes:", this);
    lblChangelogTitle->setObjectName("lblChangelogTitle");

    QTextEdit *textChangelog = new QTextEdit(this);
    textChangelog->setObjectName("textChangelog");
    textChangelog->setReadOnly(true);
    textChangelog->setMarkdown(releaseNotes);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    btnLayout->setSpacing(10);
    btnLayout->addStretch();

    QPushButton *btnLater = new QPushButton("Remind Me Later", this);
    btnLater->setObjectName("btnLater");

    QPushButton *btnUpdate = new QPushButton("⚡ Download & Update Now", this);
    btnUpdate->setObjectName("btnUpdate");

    btnLayout->addWidget(btnLater);
    btnLayout->addWidget(btnUpdate);

    mainLayout->addWidget(lblHeader);
    mainLayout->addWidget(lblVersionInfo);
    mainLayout->addWidget(lblChangelogTitle);
    mainLayout->addWidget(textChangelog, 1);
    mainLayout->addLayout(btnLayout);

    connect(btnUpdate, &QPushButton::clicked, this, &QDialog::accept);
    connect(btnLater, &QPushButton::clicked, this, &QDialog::reject);
}

AutoUpdater::AutoUpdater(QWidget *parentWidget, const QString &currentVersion)
    : QObject(parentWidget)
    , m_parentWidget(parentWidget)
    , m_currentVersion(currentVersion)
{
}

bool AutoUpdater::isVersionNewer(const QString &latest, const QString &current)
{
    QString cleanLatest = latest;
    if (cleanLatest.startsWith('v', Qt::CaseInsensitive)) {
        cleanLatest.remove(0, 1);
    }
    QString cleanCurrent = current;
    if (cleanCurrent.startsWith('v', Qt::CaseInsensitive)) {
        cleanCurrent.remove(0, 1);
    }

    QVersionNumber vLatest = QVersionNumber::fromString(cleanLatest);
    QVersionNumber vCurrent = QVersionNumber::fromString(cleanCurrent);

    return vLatest > vCurrent;
}

void AutoUpdater::checkForUpdates(bool silentCheck)
{
    m_silentCheck = silentCheck;

    QUrl url("https://api.github.com/repos/showayebDev/Rapid_Message_Sender/releases/latest");
    QNetworkRequest request(url);
    request.setRawHeader("User-Agent", "RapidMessageSender-Updater/1.0");
    request.setRawHeader("Accept", "application/vnd.github.v3+json");
    request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);

    m_releaseReply = m_netManager.get(request);
    connect(m_releaseReply, &QNetworkReply::finished, this, &AutoUpdater::onReleaseInfoDownloaded);
}

void AutoUpdater::onReleaseInfoDownloaded()
{
    if (!m_releaseReply) return;

    int statusCode = m_releaseReply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
    QByteArray data = m_releaseReply->readAll();

    m_releaseReply->deleteLater();
    m_releaseReply = nullptr;

    if (statusCode != 200) {
        if (!m_silentCheck) {
            QString serverMsg;
            QJsonDocument errDoc = QJsonDocument::fromJson(data);
            if (errDoc.isObject() && errDoc.object().contains("message")) {
                serverMsg = errDoc.object()["message"].toString();
            }

            if (statusCode == 403 || serverMsg.contains("rate limit", Qt::CaseInsensitive)) {
                QMessageBox::information(
                    m_parentWidget,
                    "GitHub API Rate Limit",
                    "GitHub API rate limit temporarily reached for your IP address.\n\nGitHub allows up to 60 update checks per hour for public IP addresses. Please try checking again in a few minutes."
                );
            } else if (statusCode == 404) {
                QMessageBox::information(
                    m_parentWidget,
                    "No GitHub Release Found",
                    "No published release found on GitHub yet.\n\nOnce a release tag (e.g. v1.0.0) is published at:\nhttps://github.com/showayebDev/Rapid_Message_Sender/releases\n\nupdates will automatically download from here."
                );
            } else {
                QMessageBox::warning(
                    m_parentWidget,
                    "Update Check Status",
                    QString("Unable to check for updates (HTTP %1):\n%2")
                        .arg(statusCode > 0 ? QString::number(statusCode) : "Error")
                        .arg(serverMsg.isEmpty() ? "Please check back after creating a release on GitHub." : serverMsg)
                );
            }
        }
        emit checkFinished(false, "", "");
        return;
    }

    QJsonDocument doc = QJsonDocument::fromJson(data);
    if (!doc.isObject()) {
        if (!m_silentCheck) {
            QMessageBox::warning(m_parentWidget, "Update Check", "Received invalid release metadata format from GitHub.");
        }
        emit checkFinished(false, "", "");
        return;
    }

    QJsonObject obj = doc.object();
    m_latestTag = obj["tag_name"].toString();
    m_releaseNotes = obj["body"].toString();

    m_downloadUrl.clear();
    QJsonArray assets = obj["assets"].toArray();
    for (const QJsonValue &val : assets) {
        QJsonObject assetObj = val.toObject();
        QString name = assetObj["name"].toString();
        if (name.endsWith(".exe", Qt::CaseInsensitive)) {
            m_downloadUrl = assetObj["browser_download_url"].toString();
            break;
        }
    }

    bool hasUpdate = isVersionNewer(m_latestTag, m_currentVersion);

    if (hasUpdate) {
        UpdateDialog dlg(m_parentWidget, m_latestTag, m_currentVersion, m_releaseNotes);
        if (dlg.exec() == QDialog::Accepted) {
            downloadAndInstall();
        }
    } else {
        if (!m_silentCheck) {
            QMessageBox::information(m_parentWidget, "Up to Date",
                                     QString("You are using the latest version (%1).").arg(m_currentVersion));
        }
    }

    emit checkFinished(hasUpdate, m_latestTag, m_releaseNotes);
}

void AutoUpdater::downloadAndInstall()
{
    if (m_downloadUrl.isEmpty()) {
        QMessageBox::critical(m_parentWidget, "Update Failed", "No executable release asset found in the latest release.");
        return;
    }

    QString tempDir = QStandardPaths::writableLocation(QStandardPaths::TempLocation);
    m_tempExePath = QDir(tempDir).filePath("RapidMessageSender_new.exe");

    m_tempFile = new QFile(m_tempExePath, this);
    if (!m_tempFile->open(QIODevice::WriteOnly)) {
        QMessageBox::critical(m_parentWidget, "Update Failed", QString("Cannot create temporary update file:\n%1").arg(m_tempExePath));
        delete m_tempFile;
        m_tempFile = nullptr;
        return;
    }

    m_progressDialog = new QProgressDialog("Downloading update...", "Cancel", 0, 100, m_parentWidget);
    m_progressDialog->setWindowModality(Qt::WindowModal);
    m_progressDialog->setMinimumDuration(0);
    m_progressDialog->setValue(0);

    QNetworkRequest request((QUrl(m_downloadUrl)));
    request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);
    request.setRawHeader("User-Agent", "RapidMessageSender-Updater/1.0");

    m_downloadReply = m_netManager.get(request);

    connect(m_downloadReply, &QNetworkReply::downloadProgress, this, &AutoUpdater::onDownloadProgress);
    connect(m_downloadReply, &QNetworkReply::finished, this, &AutoUpdater::onDownloadFinished);
    connect(m_progressDialog, &QProgressDialog::canceled, m_downloadReply, &QNetworkReply::abort);
}

void AutoUpdater::onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal)
{
    if (bytesTotal > 0 && m_progressDialog) {
        int percent = static_cast<int>((bytesReceived * 100) / bytesTotal);
        m_progressDialog->setValue(percent);
    }
}

void AutoUpdater::onDownloadFinished()
{
    if (m_progressDialog) {
        m_progressDialog->close();
        m_progressDialog->deleteLater();
        m_progressDialog = nullptr;
    }

    if (!m_downloadReply) return;

    if (m_downloadReply->error() != QNetworkReply::NoError) {
        if (m_tempFile) {
            m_tempFile->close();
            m_tempFile->remove();
            delete m_tempFile;
            m_tempFile = nullptr;
        }
        QMessageBox::critical(m_parentWidget, "Download Error",
                              QString("Failed to download update executable:\n%1").arg(m_downloadReply->errorString()));
        m_downloadReply->deleteLater();
        m_downloadReply = nullptr;
        return;
    }

    m_tempFile->write(m_downloadReply->readAll());
    m_tempFile->flush();
    m_tempFile->close();

    m_downloadReply->deleteLater();
    m_downloadReply = nullptr;

    createAndRunUpdateBatch(m_tempExePath);
}

void AutoUpdater::createAndRunUpdateBatch(const QString &tempExePath)
{
    QString currentExePath = QCoreApplication::applicationFilePath();
    QString tempDir = QStandardPaths::writableLocation(QStandardPaths::TempLocation);
    QString batchPath = QDir(tempDir).filePath("rapid_sender_updater.bat");

    QFile batchFile(batchPath);
    if (!batchFile.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QMessageBox::critical(m_parentWidget, "Update Script Error", "Cannot create updater batch script.");
        return;
    }

    QTextStream out(&batchFile);
    out << "@echo off\n";
    out << "echo Updating Rapid Message Sender...\n";
    out << "timeout /t 2 /nobreak >NUL\n";
    out << "copy /y \"" << QDir::toNativeSeparators(tempExePath) << "\" \"" << QDir::toNativeSeparators(currentExePath) << "\"\n";
    out << "del \"" << QDir::toNativeSeparators(tempExePath) << "\"\n";
    out << "start \"\" \"" << QDir::toNativeSeparators(currentExePath) << "\"\n";
    out << "del \"%~f0\"\n";

    batchFile.close();

    QProcess::startDetached("cmd.exe", QStringList() << "/c" << QDir::toNativeSeparators(batchPath));
    QCoreApplication::quit();
}
