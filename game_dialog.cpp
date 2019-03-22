#include "game_dialog.h"
#include "ui_game_dialog.h"

game_dialog::game_dialog(QWidget *parent) :
  QDialog(parent),
  ui(new Ui::game_dialog)
{
  ui->setupUi(this);
  this->startTimer(1000);
}

game_dialog::~game_dialog()
{
  delete ui;
}

void game_dialog::mousePressEvent(QMouseEvent *)
{
  m_beer_state = beer_state::foam;
  ui->label_beer->setPixmap(QPixmap(":/equation.png"));
  ui->label_text->setText("Yippee!\nAn equation!");
  ui->label_beer->setFrameStyle(QFrame::Box);
}

void game_dialog::timerEvent(QTimerEvent *)
{
  if (m_beer_state == beer_state::foam)
  {
    if (std::rand() % 10 == 0)
    {
      m_beer_state = beer_state::no_foam;
      ui->label_beer->setPixmap(QPixmap(":/no_equation.png"));
      ui->label_text->setText("Yuck! No\nequation!");
      ui->label_beer->setFrameStyle(QFrame::NoFrame);
    }
  }

}
