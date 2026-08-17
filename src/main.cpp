#include "ui/mainwindow.h"
#include <QApplication>
#include <QIcon>

#ifndef APP_VERSION_STRING
#define APP_VERSION_STRING "1.0.0"
#endif

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    QApplication::setOrganizationName("ShowayebDev");
    QApplication::setApplicationName("RapidMessageSender");
    QApplication::setApplicationVersion(APP_VERSION_STRING);

    MainWindow w;
    w.setWindowIcon(QIcon(":/app_icon.ico"));
    w.show();

    return a.exec();
}
