#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include "include/help.h"

using namespace Glib;
using namespace Gtk;

std::string Help :: openFile(std::string name) {
    std::fstream file;
    file.open(name, std::ios::in);
    std::string fullFile;
    int num = 0;
    if (!file) {
        std::cout << "File does not exist";
        fullFile.append(":(");
    } else {
        char ch;
        while (1) {
        file >> std::noskipws >> ch;
        if (file.eof()) {
            break;
        }
        if (num >= 50 && ch == ' ') {
            fullFile += '\n';
            num = 0;
        } else if (ch == '\n') {
            num = 0;
            fullFile += '\n';
        } else {
            fullFile += ch;
            num += 1;
        }
    }
  }
  file.close();
  return fullFile;
}

Help :: Help() {
    bar.set_show_close_button(true);
    set_titlebar(bar);

    add(scrolledWindow);
    scrolledWindow.add(fixed);

    bar.set_title("Help/FAQ");

    fixed.add(tabControl);
    fixed.move(tabControl, 10, 10);

    tabControl.insert_page(tab1, "Getting Started", 0);
    tabControl.insert_page(tab2, "About", 1);
    tabControl.insert_page(tab3, "Contact", 3);

    labelPage1.set_label("Getting Started");
    tabControl.set_tab_label(tab1, labelPage1);
    tab1.add(fixedTabPage1);

    text.set_text(openFile("gettingStarted.txt"));
    fixedTabPage1.add(text);

    labelPage2.set_label("About");
    tabControl.set_tab_label(tab2, labelPage2);
    tab2.add(fixedTabPage2);

    aboutText.set_text(openFile("about.txt"));
    fixedTabPage2.add(aboutText);

    labelPage3.set_label("Contact");
    tabControl.set_tab_label(tab3, labelPage3);
    tab3.add(fixedTabPage3);

    contactText.set_text(openFile("contact.txt"));
    fixedTabPage3.add(contactText);

    resize(500,400);
    show_all();
}