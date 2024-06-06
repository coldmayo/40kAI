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
        Notebook tabControl;
        Frame tab1;
        Label labelPage1;
        Fixed fixedTabPage1;
        Frame tab2;
        Label labelPage2;
        Fixed fixedTabPage2;
        Frame tab3;
        Label labelPage3;
        Fixed fixedTabPage3;
        Frame tab4;
        Label labelPage4;
        Fixed fixedTabPage4;

};

#endif