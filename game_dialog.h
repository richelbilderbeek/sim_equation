#ifndef GAME_DIALOG_H
#define GAME_DIALOG_H

#include <QDialog>

namespace Ui {
  class game_dialog;
}

class game_dialog : public QDialog
{
  Q_OBJECT

public:

  enum class beer_state { foam, no_foam };

  explicit game_dialog(QWidget *parent = 0);
  ~game_dialog();

private:
  Ui::game_dialog *ui;

  beer_state m_beer_state = beer_state::foam;

  void mousePressEvent(QMouseEvent *event);

  void timerEvent(QTimerEvent *event);
};

#endif // GAME_DIALOG_H
