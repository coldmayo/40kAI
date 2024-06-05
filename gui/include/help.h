#ifndef HELP_H
#define HELP_H

#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>

using namespace Glib;
using namespace Gtk;

class Help : public Gtk::Window {
    public:
        Help();
    private:
        Fixed fixed;
        ScrolledWindow scrolledWindow;
        HeaderBar bar;
};

#endif