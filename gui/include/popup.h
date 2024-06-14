#ifndef POPOP_H
#define POPOP_H

using namespace Glib;
using namespace Gtk;

class PopUp : public Gtk::Window {
  public : 
    PopUp();
    std::string openFile(std::string board);
    bool isNum(char num);
    void update();
  private:
    Label contents;
    Fixed fixed;
    ScrolledWindow scrolledWindow;
    HeaderBar bar;
};

#endif