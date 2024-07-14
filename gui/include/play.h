#ifndef PLAY_H
#define PLAY_H

#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>

using namespace Glib;
using namespace Gtk;

class Play : public Gtk::Window {
    public:
        Play();
    private:
        Fixed fixed;
        ScrolledWindow scrolledWindow;
        ScrolledWindow innerWindow;
        HeaderBar bar;
		Button enter;
        Button plus;
        Button minus;
		RadioButtonGroup yesOrNoRadio;
  		RadioButton radioYes;
  		RadioButton radioNo;
  		Entry numBox;
  		Label text;
};

#endif
