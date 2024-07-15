#ifndef POPOP_H
#define POPOP_H

#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <string>
#include <stdlib.h>

using namespace Glib;
using namespace Gtk;

class PopUp : public Gtk::Window {
  public : 
    PopUp();
    std::string openFile(std::string board);
    bool isNum(char num);
    void update();
    void backgroundUpdate(bool textMode);
    void keepUpdating();
    void keepUpdatingElecBoogaloo();
    void updateImage();
  private:
    Label contents;
    Fixed fixed;
    ScrolledWindow scrolledWindow;
    HeaderBar bar;
    Button changeMode;
    Image pictureBox;
};

#endif
