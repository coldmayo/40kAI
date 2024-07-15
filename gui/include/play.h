#ifndef PLAY_H
#define PLAY_H

#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>

using namespace Glib;
using namespace Gtk;
using namespace std;

class Play : public Gtk::Window {
    public:
        Play();
        void update();
        void keepUpdating();
        void backgroundUpdate();
        void update_text_view();
        bool file_exists(char * fileName);
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
  		bool takeInput;
  		std::string response;
  		Dispatcher dispatcher;
};

#endif
