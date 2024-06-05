#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include "include/help.h"

using namespace Glib;
using namespace Gtk;

Help :: Help() {
    bar.set_show_close_button(true);
    set_titlebar(bar);

    add(scrolledWindow);
    scrolledWindow.add(fixed);

    bar.set_title("Warning Message");

    resize(500,600);
    show_all();
}