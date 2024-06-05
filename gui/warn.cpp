#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include "include/warn.h"

using namespace Glib;
using namespace Gtk;

Warn :: Warn(std::string message, int comm) {
    bar.set_show_close_button(true);
    set_titlebar(bar);

    add(scrolledWindow);
    scrolledWindow.add(fixed);

    text.set_text(message);
    cancel.set_label("Cancel");
    cancel.signal_button_release_event().connect([&](GdkEventButton*) {
        this->hide();
        return true;
    });
    cont.set_label("Continue");
    cont.signal_button_release_event().connect([&](GdkEventButton*) {
        if (comm == 0) {
            system("cd .. ; rm -r models/*");
        }
        this->hide();
        return true;
    });

    fixed.add(text);
    fixed.move(text, 10, 10);
    fixed.add(cancel);
    fixed.move(cancel, 10, 40);
    fixed.add(cont);
    fixed.move(cont, 320, 40);

    bar.set_title("Warning Message");

    resize(400,200);
    show_all();
}