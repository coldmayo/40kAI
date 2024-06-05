#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>

using namespace Glib;
using namespace Gtk;

class Warn : public Gtk::Window {
    public:
        Warn(std::string message, int comm);
    private:
        Fixed fixed;
        ScrolledWindow scrolledWindow;
        HeaderBar bar;
        Label text;
        Button cancel;
        Button cont;
};