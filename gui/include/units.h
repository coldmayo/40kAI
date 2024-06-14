#ifndef UNITS_H
#define UNITS_H

#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <thread>
#include <chrono>

using namespace Glib;
using namespace Gtk;

class Units : public Gtk::Window {
  public : 
    Units();
    std::string openFile(std::string);
    void update();
    void keepUpdating();
    void backgroudUpdate();
    void getAvailUnits();
    void addFact(std::vector<std::string> facts);
  private:
    Label contents;
    Label possible;
    Fixed fixed;
    ScrolledWindow scrolledWindow;
    HeaderBar bar;
    int lines;
    std::string output;
};

#endif
