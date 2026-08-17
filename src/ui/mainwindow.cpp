#include "ui/mainwindow.h"
#include "ui_mainwindow.h"
#include <QMessageBox>
#include <QDateTime>
#include <QApplication>
#include <QScrollBar>
#include <QIcon>

#ifndef APP_VERSION_STRING
#define APP_VERSION_STRING "1.0.0"
#endif

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    // Dynamic Version Window Title
    setWindowTitle(QString("Rapid Message Sender (v%1)").arg(APP_VERSION_STRING));

    // Set Window Icon from assets resource
    setWindowIcon(QIcon(":/app_icon.png"));

    setupUiDefaults();
    setupDocumentationPage();
    applyDarkStyleSheet();

    // Auto updater initialized with dynamic version string
    m_updater = new AutoUpdater(this, QString("v%1").arg(APP_VERSION_STRING));

    // Global Hotkey Filter
    m_hotkeyFilter = new GlobalHotkeyFilter(this);
    qApp->installNativeEventFilter(m_hotkeyFilter);
    m_hotkeyFilter->registerCtrlQ(reinterpret_cast<HWND>(winId()));
    connect(m_hotkeyFilter, &GlobalHotkeyFilter::hotkeyPressed, this, &MainWindow::onGlobalHotkeyTriggered);

    // Button Signal Connections
    connect(ui->btnStart, &QPushButton::clicked, this, &MainWindow::onStartClicked);
    connect(ui->btnStop, &QPushButton::clicked, this, &MainWindow::onStopClicked);
    connect(ui->btnReset, &QPushButton::clicked, this, &MainWindow::onResetClicked);
    connect(ui->btnCheckUpdates, &QPushButton::clicked, this, &MainWindow::onCheckUpdatesClicked);
    connect(ui->btnNavDoc, &QPushButton::clicked, this, &MainWindow::onNavDocClicked);
    connect(ui->btnBackToApp, &QPushButton::clicked, this, &MainWindow::onNavWorkspaceClicked);

    connect(ui->comboTemplate, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &MainWindow::onTemplateChanged);

    // Initial silent update check
    m_updater->checkForUpdates(true);
}

MainWindow::~MainWindow()
{
    if (m_worker && m_worker->isRunning()) {
        m_worker->requestStop();
        m_worker->wait(2000);
    }
    delete ui;
}

void MainWindow::setupUiDefaults()
{
    // Preset Templates
    ui->comboTemplate->addItem("Select Template...", "");
    ui->comboTemplate->addItem("Standard Greeting", "Hello! This is a rapid automated message.");
    ui->comboTemplate->addItem("Account Status Notice", "Important Notice: Please review your recent account notifications.");
    ui->comboTemplate->addItem("High-Speed Payload", "Testing Rapid Message Sender performance and micro-pause accuracy.");
    ui->comboTemplate->addItem("Multi-Line Test", "Line 1: Automated Header\nLine 2: Data Payload\nLine 3: End of Message");

    // Engine Modes
    ui->comboEngineMode->addItem("💻 Direct Character Typing (Simulated Keyboard)", static_cast<int>(EngineMode::DirectTyping));
    ui->comboEngineMode->addItem("⚡ Clipboard Copy & Paste (Ultra-Fast)", static_cast<int>(EngineMode::ClipboardCopyPaste));

    // Trigger Key Options
    ui->comboTriggerKey->addItem("Enter (Standard Send)", true);
    ui->comboTriggerKey->addItem("Ctrl + Enter (Alternative Send)", true);
    ui->comboTriggerKey->addItem("Shift + Enter (Newline)", false);
    ui->comboTriggerKey->addItem("None (No Trigger Key)", false);

    // Message Counter Modes (Default: Disabled)
    ui->comboCounterMode->addItem("Disabled (No Counter)", false);
    ui->comboCounterMode->addItem("Show Counter after Message (Suffix)", true);
    ui->comboCounterMode->addItem("Show Counter before Message (Prefix)", true);

    // Separators
    ui->comboSeparator->addItem("Space ( )", static_cast<int>(SeparatorType::Space));
    ui->comboSeparator->addItem("Semicolon ( ; )", static_cast<int>(SeparatorType::Semicolon));
    ui->comboSeparator->addItem("Dash ( - )", static_cast<int>(SeparatorType::Dash));
    ui->comboSeparator->addItem("Hash ( # )", static_cast<int>(SeparatorType::Hash));

    ui->comboCounterMode->setCurrentIndex(0); // Disabled by default
    ui->comboSeparator->setCurrentIndex(0);   // Space default

    ui->textMessage->setPlainText("Hello! This is a rapid automated message.");
    ui->progressAutomation->setValue(0);
}

void MainWindow::setupDocumentationPage()
{
    QString docHtml = R"(
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: #E2E8F0;
            background-color: #0B0D14;
            margin: 0;
            padding: 10px;
        }
        .section-title {
            color: #38BDF8;
            font-size: 15px;
            font-weight: bold;
            padding: 6px 0px 8px 0px;
        }
        .badge-step {
            background-color: #0284C7;
            color: #FFFFFF;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .badge-feature {
            background-color: #4F46E5;
            color: #FFFFFF;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .badge-tip {
            background-color: #D97706;
            color: #FFFFFF;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        code {
            background-color: #1E293B;
            color: #38BDF8;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: Consolas, monospace;
            font-weight: bold;
        }
    </style>
    </head>
    <body>

    <!-- Section 1: Quick Start Tutorial -->
    <div class="section-title">🚀 Quick Start Tutorial</div>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-step">Step 1</span> &nbsp;<b style="color: #F1F5F9;">Message Content</b> — Enter your message text in the editor or choose a built-in template preset from the dropdown menu.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-step">Step 2</span> &nbsp;<b style="color: #F1F5F9;">Select Input Engine</b> — Choose <code>💻 Direct Character Typing</code> (hardware keyboard simulation without clipboard) or <code>⚡ Clipboard Copy &amp; Paste</code> (ultra-fast).
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-step">Step 3</span> &nbsp;<b style="color: #F1F5F9;">Configure Automation Parameters</b> — Set message repetition count (e.g. 10), wait delay between messages (default 100 ms), and start countdown (default 5 sec).
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-step">Step 4</span> &nbsp;<b style="color: #F1F5F9;">Counter &amp; Separator Options</b> — Enable automated message numbering (Suffix/Prefix) and pick a separator (Space, Semicolon, Dash, Hash).
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-step">Step 5</span> &nbsp;<b style="color: #F1F5F9;">Start &amp; Target Focus</b> — Click <code>🚀 Start Sending</code>, then immediately click inside your target chat box (WhatsApp, Telegram, Discord, Messenger, Notepad, etc.) during the 5s countdown.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 18px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-step">Step 6</span> &nbsp;<b style="color: #F1F5F9;">Emergency Abort</b> — Press <code>Ctrl + Q</code> globally from any window or flick your mouse cursor to the top-left screen corner (0,0) to stop automation instantly.
            </td>
        </tr>
    </table>

    <!-- Section 2: Safety & Reliability Features -->
    <div class="section-title">🛡️ Built-in Reliability &amp; Safety Features</div>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-feature">Engine</span> &nbsp;<b style="color: #F1F5F9;">Direct Character Typing</b> — Simulates direct hardware keyboard keystrokes via Windows OS <code>SendInput()</code> API without modifying clipboard contents.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-feature">Speed</span> &nbsp;<b style="color: #F1F5F9;">Clipboard Copy-Paste Engine</b> — Uses Win32 <code>Ctrl+V</code> with read-back memory verification for ultra-fast multi-line dispatches.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-feature">Network</span> &nbsp;<b style="color: #F1F5F9;">GitHub Release Auto-Updater</b> — Asynchronously queries GitHub REST API, displays changelogs, downloads new binaries, and replaces old EXEs upon restart.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-feature">Safety</span> &nbsp;<b style="color: #F1F5F9;">Dual Emergency Abort</b> — Global <code>Ctrl+Q</code> key combo and hardware mouse corner (0,0) fail-safe continuously monitor background operations.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-feature">UX Protection</span> &nbsp;<b style="color: #F1F5F9;">Mouse Scroll Lock</b> — Overrides wheel events on spinboxes and dropdowns to prevent accidental parameter mutations while scrolling.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 18px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #141A28; border: 1px solid #202A3F; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-feature">Reset</span> &nbsp;<b style="color: #F1F5F9;">Reset All Button</b> — Restores all application defaults, resets logs, stats dashboards, and wipes clipboard memory with a single click.
            </td>
        </tr>
    </table>

    <!-- Section 3: Pro-Tips & Troubleshooting -->
    <div class="section-title">💡 Pro-Tips &amp; Troubleshooting</div>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #1A1F30; border-left: 4px solid #F59E0B; border-top: 1px solid #252D42; border-right: 1px solid #252D42; border-bottom: 1px solid #252D42; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-tip">Tip 1</span> &nbsp;<b style="color: #FBBF24;">Multi-Line Text Behavior</b> — Use <code>⚡ Clipboard Copy &amp; Paste</code> to send multi-line text blocks as <b>a single combined message</b>. Use <code>💻 Direct Character Typing</code> to send each line individually as <b>separate sequential messages</b>.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #1A1F30; border-left: 4px solid #F59E0B; border-top: 1px solid #252D42; border-right: 1px solid #252D42; border-bottom: 1px solid #252D42; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-tip">Tip 2</span> &nbsp;<b style="color: #FBBF24;">Emoji &amp; Special Characters</b> — For messages containing emojis (⚡, 🔥, 🚀), select <code>⚡ Clipboard Copy &amp; Paste</code> mode. For plain text messages, use <code>💻 Direct Character Typing</code>.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #1A1F30; border-left: 4px solid #F59E0B; border-top: 1px solid #252D42; border-right: 1px solid #252D42; border-bottom: 1px solid #252D42; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-tip">Tip 3</span> &nbsp;<b style="color: #FBBF24;">Facebook, Instagram &amp; QA Web Testing</b> — Set interval delay to 400 ms – 500 ms when dispatching to web chat apps to avoid web-based rate limiting.
            </td>
        </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 18px; width: 100%;">
        <tr>
            <td width="100%" style="background-color: #1A1F30; border-left: 4px solid #F59E0B; border-top: 1px solid #252D42; border-right: 1px solid #252D42; border-bottom: 1px solid #252D42; padding: 12px 16px; border-radius: 8px;">
                <span class="badge-tip">Tip 4</span> &nbsp;<b style="color: #FBBF24;">Slow Web App Dispatch</b> — If WhatsApp Web or Discord receives written text without triggering the Enter send key, increase interval delay to 1000 ms (1 sec) to allow the target app to process inputs.
            </td>
        </tr>
    </table>

    <!-- Section 4: Shortcuts & Hotkey Reference -->
    <div class="section-title">💻 Shortcuts &amp; Hotkey Reference</div>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-top: 8px; width: 100%; border-collapse: collapse;">
        <thead>
            <tr>
                <th width="25%" style="background-color: #1E2638; color: #38BDF8; text-align: left; padding: 10px 14px; border: 1px solid #28324A;">Shortcut</th>
                <th width="75%" style="background-color: #1E2638; color: #38BDF8; text-align: left; padding: 10px 14px; border: 1px solid #28324A;">Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td width="25%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;"><code>Ctrl + Q</code></td>
                <td width="75%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;">Global Emergency Abort (Works across all Windows applications)</td>
            </tr>
            <tr>
                <td width="25%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;"><code>Mouse (0,0)</code></td>
                <td width="75%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;">Hardware Fail-Safe (Flick cursor to top-left screen corner to abort)</td>
            </tr>
            <tr>
                <td width="25%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;"><code>Enter</code></td>
                <td width="75%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;">Standard trigger key sent after typing or pasting message payload</td>
            </tr>
            <tr>
                <td width="25%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;"><code>Ctrl + Enter</code></td>
                <td width="75%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;">Alternative send trigger (ideal for Slack &amp; Discord multi-line modes)</td>
            </tr>
            <tr>
                <td width="25%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;"><code>Shift + Enter</code></td>
                <td width="75%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;">Newline insertion without triggering instant send</td>
            </tr>
            <tr>
                <td width="25%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;"><code>None</code></td>
                <td width="75%" style="background-color: #141A28; color: #E2E8F0; padding: 10px 14px; border: 1px solid #202A3F;">Type or paste message into target field without pressing any trigger key</td>
            </tr>
        </tbody>
    </table>

    </body>
    </html>
    )";

    ui->textDocContent->setHtml(docHtml);
}

void MainWindow::applyDarkStyleSheet()
{
    QString qss = R"(
        QMainWindow, QWidget#centralwidget, QWidget#pageWorkspace, QWidget#pageDoc {
            background-color: #0B0D14;
            color: #E2E8F0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QLabel {
            background-color: transparent;
            color: #E2E8F0;
        }
        QFrame#headerFrame, QFrame#frameDocHeader {
            background-color: #121624;
            border: 1px solid #1E2638;
            border-radius: 8px;
        }
        QFrame#leftColumnFrame, QFrame#rightColumnFrame {
            background-color: transparent;
            border: none;
        }
        QGroupBox {
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #1E2638;
            border-radius: 8px;
            background-color: #121624;
            margin-top: 14px;
            padding-top: 18px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 3px 10px;
            background-color: #121624;
            color: #818CF8;
            border: 1px solid #1E2638;
            border-radius: 6px;
        }
        QTextEdit {
            background-color: #181D2C;
            color: #F1F5F9;
            border: 1px solid #28324A;
            border-radius: 8px;
            padding: 8px 10px;
        }
        QTextEdit:focus {
            border: 1px solid #38BDF8;
        }
        QTextEdit#textDocContent {
            background-color: #0B0D14;
            border: none;
            border-radius: 0px;
        }

        /* Modern Custom QComboBox Styling */
        QComboBox {
            background-color: #181D2C;
            color: #F1F5F9;
            border: 1px solid #28324A;
            border-radius: 8px;
            padding: 6px 12px;
            padding-right: 30px;
            font-size: 13px;
        }
        QComboBox:hover {
            border: 1px solid #38BDF8;
            background-color: #1E2538;
        }
        QComboBox:on {
            border: 1px solid #38BDF8;
            background-color: #1E2538;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 0px;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            background-color: transparent;
        }
        QComboBox::down-arrow {
            image: url(:/spin_down.png);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #181D2C;
            color: #F1F5F9;
            border: 1px solid #38BDF8;
            border-radius: 8px;
            selection-background-color: #28334A;
            selection-color: #38BDF8;
            padding: 4px;
            outline: 0px;
        }
        QComboBox QAbstractItemView::item {
            min-height: 28px;
            padding: 4px 10px;
            border-radius: 6px;
        }
        QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected {
            background-color: #28334A;
            color: #38BDF8;
        }

        /* Custom QSpinBox Styling */
        QSpinBox {
            background-color: #181D2C;
            color: #F1F5F9;
            border: 1px solid #28324A;
            border-radius: 8px;
            padding: 6px 10px;
            padding-right: 25px;
        }
        QSpinBox:hover {
            border: 1px solid #38BDF8;
            background-color: #1E2538;
        }
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #28324A;
            border-bottom: 1px solid #28324A;
            border-top-right-radius: 7px;
            background-color: #1E2538;
        }
        QSpinBox::up-button:hover {
            background-color: #28334A;
        }
        QSpinBox::up-arrow {
            image: url(:/spin_up.png);
            width: 10px;
            height: 10px;
        }
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #28324A;
            border-bottom-right-radius: 7px;
            background-color: #1E2538;
        }
        QSpinBox::down-button:hover {
            background-color: #28334A;
        }
        QSpinBox::down-arrow {
            image: url(:/spin_down.png);
            width: 10px;
            height: 10px;
        }

        QPushButton {
            background-color: #1E2638;
            color: #E2E8F0;
            border: 1px solid #2D374D;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #28334A;
            border-color: #38BDF8;
        }
        QPushButton#btnStart {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00B4DB, stop:1 #0083B0);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-size: 14px;
        }
        QPushButton#btnStart:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C6FF, stop:1 #0072FF);
        }
        QPushButton#btnStop {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF416C, stop:1 #FF4B2B);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-size: 14px;
        }
        QPushButton#btnStop:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF4B2B, stop:1 #FF416C);
        }
        QPushButton#btnReset {
            background-color: #1A2130;
            color: #60A5FA;
            border: 1px solid #28324A;
            border-radius: 8px;
        }
        QPushButton#btnReset:hover {
            background-color: #242E45;
            color: #93C5FD;
        }
        QPushButton#btnBackToApp {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-size: 13px;
        }
        QPushButton#btnEmergencyBadge {
            background-color: #261520;
            color: #FF6B6B;
            border: 1px solid #4A1E2F;
            border-radius: 8px;
            font-size: 12px;
        }
        QFrame#frameStatusBanner {
            background-color: #151C2E;
            border: 1px solid #2B3A60;
            border-radius: 8px;
        }
        QLabel#lblStatusState {
            color: #00F5D4;
            letter-spacing: 1px;
            background-color: transparent;
        }
        QLabel#lblStatusMessage {
            color: #00E5FF;
            background-color: transparent;
        }
        QFrame#cardSent, QFrame#cardElapsed {
            background-color: #141A29;
            border: 1px solid #222C42;
            border-radius: 8px;
        }
        QLabel#lblSentVal, QLabel#lblElapsedVal {
            color: #38BDF8;
            background-color: transparent;
        }
        QLabel#lblSentTitle, QLabel#lblElapsedTitle {
            color: #64748B;
            font-size: 12px;
            background-color: transparent;
        }
        QProgressBar {
            border: 1px solid #222C42;
            border-radius: 8px;
            text-align: center;
            background-color: #141A29;
            color: #F1F5F9;
            height: 22px;
        }
        QProgressBar::chunk {
            background-color: #00ADB5;
            border-radius: 6px;
        }
    )";

    setStyleSheet(qss);
}

AutomationConfig MainWindow::buildConfigFromUi()
{
    AutomationConfig config;
    config.baseMessage = ui->textMessage->toPlainText();
    config.engineMode = static_cast<EngineMode>(ui->comboEngineMode->currentData().toInt());
    config.intervalMs = ui->spinInterval->value();
    config.startDelaySec = ui->spinStartDelay->value();
    config.repeatCount = ui->spinRepetitions->value();

    bool hasCounter = ui->comboCounterMode->currentData().toBool();
    config.appendCounter = hasCounter;
    config.counterAsPrefix = (ui->comboCounterMode->currentIndex() == 2);
    config.separator = static_cast<SeparatorType>(ui->comboSeparator->currentData().toInt());
    config.autoSendEnter = (ui->comboTriggerKey->currentIndex() == 0 || ui->comboTriggerKey->currentIndex() == 1);

    return config;
}

void MainWindow::setControlsEnabled(bool enabled)
{
    ui->textMessage->setEnabled(enabled);
    ui->comboTemplate->setEnabled(enabled);
    ui->comboEngineMode->setEnabled(enabled);
    ui->spinInterval->setEnabled(enabled);
    ui->spinStartDelay->setEnabled(enabled);
    ui->spinRepetitions->setEnabled(enabled);
    ui->comboTriggerKey->setEnabled(enabled);
    ui->comboCounterMode->setEnabled(enabled);
    ui->comboSeparator->setEnabled(enabled);
    ui->btnReset->setEnabled(enabled);

    ui->btnStart->setEnabled(enabled);
    ui->btnStop->setEnabled(!enabled);
}

void MainWindow::onStartClicked()
{
    if (ui->textMessage->toPlainText().trimmed().isEmpty()) {
        QMessageBox::warning(this, "Empty Message", "Please enter a message to send before starting automation.");
        return;
    }

    setControlsEnabled(false);
    ui->textLog->clear();
    ui->progressAutomation->setValue(0);

    ui->lblStatusState->setText("AUTOMATION RUNNING");
    ui->lblStatusState->setStyleSheet("color: #FFD166; background-color: transparent;");
    ui->lblStatusMessage->setText("FOCUS YOUR TARGET WINDOW NOW!");

    AutomationConfig config = buildConfigFromUi();

    m_worker = new AutomationWorker(config, this);

    connect(m_worker, &AutomationWorker::countdownTick, this, &MainWindow::onWorkerCountdown);
    connect(m_worker, &AutomationWorker::progressUpdated, this, &MainWindow::onWorkerProgress);
    connect(m_worker, &AutomationWorker::statsUpdated, this, &MainWindow::onWorkerStats);
    connect(m_worker, &AutomationWorker::logMessage, this, &MainWindow::onWorkerLog);
    connect(m_worker, &AutomationWorker::finishedAutomation, this, &MainWindow::onWorkerFinished);

    m_worker->start();
}

void MainWindow::onStopClicked()
{
    if (m_worker && m_worker->isRunning()) {
        m_worker->requestStop();
        onWorkerLog("Stop request submitted...", "WARNING");
    }
}

void MainWindow::onGlobalHotkeyTriggered()
{
    if (m_worker && m_worker->isRunning()) {
        m_worker->requestStop();
        onWorkerLog("EMERGENCY ABORT: Global Ctrl+Q hotkey pressed!", "ERROR");
    }
}

void MainWindow::onResetClicked()
{
    ui->textMessage->clear();
    ui->comboTemplate->setCurrentIndex(0);
    ui->spinInterval->setValue(100);
    ui->spinStartDelay->setValue(5);
    ui->spinRepetitions->setValue(10);
    ui->comboEngineMode->setCurrentIndex(0);
    ui->comboTriggerKey->setCurrentIndex(0);
    ui->comboCounterMode->setCurrentIndex(0); // Disabled by default
    ui->comboSeparator->setCurrentIndex(0);

    ui->lblStatusState->setText("READY TO SEND");
    ui->lblStatusState->setStyleSheet("color: #00F5D4; background-color: transparent;");
    ui->lblStatusMessage->setText("Press 'Start Sending' to begin");

    ui->lblSentVal->setText("0 / 0");
    ui->lblElapsedVal->setText("0.0 s");
    ui->progressAutomation->setValue(0);
    ui->textLog->clear();
}

void MainWindow::onTemplateChanged(int index)
{
    if (index > 0) {
        QString text = ui->comboTemplate->currentData().toString();
        if (!text.isEmpty()) {
            ui->textMessage->setPlainText(text);
        }
    }
}

void MainWindow::onCheckUpdatesClicked()
{
    if (m_updater) {
        m_updater->checkForUpdates(false);
    }
}

void MainWindow::onNavWorkspaceClicked()
{
    ui->stackedWidget->setCurrentIndex(0);
}

void MainWindow::onNavDocClicked()
{
    ui->stackedWidget->setCurrentIndex(1);
}

void MainWindow::onWorkerCountdown(int secondsRemaining)
{
    if (secondsRemaining > 0) {
        ui->lblStatusMessage->setText(QString("Starting in %1s... FOCUS TARGET!").arg(secondsRemaining));
        onWorkerLog(QString("Countdown: %1 seconds remaining...").arg(secondsRemaining), "WARNING");
    }
}

void MainWindow::onWorkerProgress(int sentCount, int totalCount)
{
    ui->lblSentVal->setText(QString("%1 / %2").arg(sentCount).arg(totalCount > 0 ? QString::number(totalCount) : "∞"));
    if (totalCount > 0) {
        int percent = static_cast<int>((sentCount * 100.0) / totalCount);
        ui->progressAutomation->setValue(qMin(100, percent));
    } else {
        ui->progressAutomation->setMaximum(0);
    }
}

void MainWindow::onWorkerStats(int sentCount, double elapsedSec, double messagesPerSec)
{
    Q_UNUSED(messagesPerSec);
    ui->lblElapsedVal->setText(QString("%1 s").arg(elapsedSec, 0, 'f', 1));
}

void MainWindow::onWorkerLog(const QString &msg, const QString &level)
{
    QString timestamp = QDateTime::currentDateTime().toString("hh:mm:ss");
    QString color = "#38BDF8"; // Info
    if (level == "SUCCESS") color = "#00F5D4";
    else if (level == "WARNING") color = "#FBBF24";
    else if (level == "ERROR") color = "#FF5722";

    QString htmlLine = QString("<span style='color: #64748B;'>[%1]</span> <span style='color: %2; font-weight: bold;'>%3</span>")
                           .arg(timestamp).arg(color).arg(msg);

    ui->textLog->append(htmlLine);
    ui->textLog->verticalScrollBar()->setValue(ui->textLog->verticalScrollBar()->maximum());
}

void MainWindow::onWorkerFinished(bool aborted, const QString &reason)
{
    ui->progressAutomation->setMaximum(100);
    if (aborted) {
        ui->lblStatusState->setText("AUTOMATION ABORTED");
        ui->lblStatusState->setStyleSheet("color: #FF5722; background-color: transparent;");
        ui->lblStatusMessage->setText(reason);
        onWorkerLog(QString("Automation Aborted: %1").arg(reason), "ERROR");
    } else {
        ui->lblStatusState->setText("AUTOMATION COMPLETED");
        ui->lblStatusState->setStyleSheet("color: #00F5D4; background-color: transparent;");
        ui->lblStatusMessage->setText("All messages sent successfully!");
        ui->progressAutomation->setValue(100);
        onWorkerLog("Automation finished successfully.", "SUCCESS");
    }

    setControlsEnabled(true);

    if (m_worker) {
        m_worker->deleteLater();
        m_worker = nullptr;
    }
}
