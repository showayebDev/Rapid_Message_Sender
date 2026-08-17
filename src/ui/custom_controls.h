#ifndef CUSTOM_CONTROLS_H
#define CUSTOM_CONTROLS_H

#include <QSpinBox>
#include <QComboBox>
#include <QWheelEvent>

class NoWheelSpinBox : public QSpinBox {
    Q_OBJECT
public:
    explicit NoWheelSpinBox(QWidget *parent = nullptr);
protected:
    void wheelEvent(QWheelEvent *event) override;
};

class NoWheelComboBox : public QComboBox {
    Q_OBJECT
public:
    explicit NoWheelComboBox(QWidget *parent = nullptr);
protected:
    void wheelEvent(QWheelEvent *event) override;
};

#endif // CUSTOM_CONTROLS_H
