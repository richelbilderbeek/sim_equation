#include "game_dialog.h"
#include <QApplication>

int main(int argc, char *argv[])
{
  QApplication a(argc, argv);
  game_dialog w;
#ifdef Q_OS_WASM
  // The web page is the window: no title bar, top-left of the canvas
  w.setWindowFlags(Qt::Window | Qt::FramelessWindowHint);
  w.move(0, 0);
#endif
  w.show();

  return a.exec();
}
