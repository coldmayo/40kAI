#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include "include/play.h"

using namespace Glib;
using namespace Gtk;
using namespace std;

Play :: Play() {
	bar.set_show_close_button(true);
	set_titlebar(bar);

	add(scrolledWindow);
	scrolledWindow.add(fixed);

	bar.set_title("Playing Against the Model");

	numBox.set_text("Enter Response Here");

	enter.set_label("Enter");
	enter.signal_button_release_event().connect([&](GdkEventButton*) {
		system("touch response.txt");
		system("truncate -s 0 response.txt");

		fstream file;
		file.open("response.txt", ios::out);
		cout << file.is_open() << endl;
		file << numBox.get_text();
		file.close();

		return true;
	});

	text.set_text("When the game starts, text will appear here");
	innerWindow.add(text);
	innerWindow.set_size_request(300,100);
	
	
	fixed.add(numBox);
	fixed.add(enter);
	fixed.add(innerWindow);
	fixed.move(innerWindow, 10, 10);
	fixed.move(numBox, 10, 100);
	fixed.move(enter, 10, 150);

    resize(400,400);
    show_all();
}
