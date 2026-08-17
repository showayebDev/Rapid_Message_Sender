#include "custom_controls.h"

NoWheelSpinBox::NoWheelSpinBox(QWidget *parent)
    : QSpinBox(parent)
{
    setFocusPolicy(Qt::StrongFocus);
}

void NoWheelSpinBox::wheelEvent(QWheelEvent *event)
{
    event->ignore();
}

NoWheelComboBox::NoWheelComboBox(QWidget *parent)
    : QComboBox(parent)
{
    setFocusPolicy(Qt::StrongFocus);
}

void NoWheelComboBox::wheelEvent(QWheelEvent *event)
{
    event->ignore();
}
