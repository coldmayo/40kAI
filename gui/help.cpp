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

    bar.set_title("Help/FAQ");

    fixed.add(tabControl);
    fixed.move(tabControl, 10, 10);

    tabControl.insert_page(tab1, "Getting Started", 0);
    tabControl.insert_page(tab2, "The Model", 1);
    tabControl.insert_page(tab3, "Troubleshooting", 2);
    tabControl.insert_page(tab4, "Contact", 3);

    labelPage1.set_label("Getting Started");
    tabControl.set_tab_label(tab1, labelPage1);
    tab1.add(fixedTabPage1);

    labelPage2.set_label("The Model");
    tabControl.set_tab_label(tab2, labelPage2);
    tab2.add(fixedTabPage2);

    labelPage3.set_label("Troubleshooting");
    tabControl.set_tab_label(tab3, labelPage3);
    tab3.add(fixedTabPage3);

    labelPage4.set_label("Contact");
    tabControl.set_tab_label(tab4, labelPage4);
    tab4.add(fixedTabPage4);

    resize(500,600);
    show_all();
}