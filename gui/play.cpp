#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <thread>
#include "include/play.h"

using namespace Glib;
using namespace Gtk;
using namespace std;

bool Play :: file_exists(char * fileName) {
	ifstream infile(fileName);
	return infile.good();
}

void Play :: update() {
	if (file_exists("response.txt")) {
		ifstream file("response.txt");
		string line;
		while(getline(file, line)) {
			for (int i = 0; line.length() > i; i++) {
				response += line[i];
			}
			response += "\n";
		}
		file.close();
		dispatcher.emit();
	}
}

void Play :: update_text_view() {
	text.set_text(response);
	system("rm response.txt");
}

void Play :: keepUpdating() {
	while (true) {
    	update();
    	std::this_thread::sleep_for(std::chrono::seconds(1));
	}
}

void Play :: backgroundUpdate() {
	std::thread t(&Play::keepUpdating, this);
	t.detach();
}

Play :: Play() {
	bar.set_show_close_button(true);
	set_titlebar(bar);

	add(scrolledWindow);
	scrolledWindow.add(fixed);

	bar.set_title("Playing Against the Model");

	numBox.set_text("Enter Response Here");

	enter.set_label("Enter");
	enter.signal_button_release_event().connect([&](GdkEventButton*) {
		ofstream file("response.txt", ios::out | ios::trunc);
		file << numBox.get_text();
		file.close();

		return true;
	});

	text.set_text("When the game starts, text will appear here");
	dispatcher.connect(sigc::mem_fun(*this, &Play::update_text_view));
	backgroundUpdate();
	innerWindow.add(text);
	innerWindow.set_size_request(350,100);
	
	
	fixed.add(numBox);
	fixed.add(enter);
	fixed.add(innerWindow);
	fixed.move(innerWindow, 10, 10);
	fixed.move(numBox, 10, 120);
	fixed.move(enter, 10, 170);

    resize(400,400);
    show_all();
}
