#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <thread>
#include <chrono>
#include <nlohmann/json.hpp>

using namespace Glib;
using namespace Gtk;
using json = nlohmann::json;

class Units : public Gtk::Window {
  public : 
    Units();
    std::string openFile(std::string);
    void update();
    void keepUpdating();
    void backgroudUpdate();
    void getAvailUnits();
  private:
    Label contents;
    Label possible;
    Fixed fixed;
    ScrolledWindow scrolledWindow;
};

void Units :: getAvailUnits() {
  std::ifstream infile("../gym_mod/gym_mod/engine/unitData.json");
  json j;
  infile >> j;

  std::vector<std::string> orks;
    std::vector<std::string> spm;

    const auto& unitData = j.at("UnitData");
    for (const auto& unit : unitData) {
        std::string army = unit.at("Army").get<std::string>();
        std::string name = unit.at("Name").get<std::string>();
        if (army == "Orks") {
            orks.push_back(name);
        } else if (army == "Space_Marine") {
            spm.push_back(name);
        }
    }

    std::string output = "Available Units:\nOrks:\n";

    for (const auto& ork : orks) {
        output += ork + ", ";
    }

    // Remove the trailing comma and space
    if (!orks.empty()) {
        output = output.substr(0, output.size() - 2);
    }

    output += "\nSpace Marines:\n";

    for (const auto& marine : spm) {
        output += marine + ", ";
    }

    // Remove the trailing comma and space
    if (!spm.empty()) {
        output = output.substr(0, output.size() - 2);
    }

    possible.set_text(output);

}

std::string Units :: openFile(std::string army) {
  std::ifstream file(army);
  std::string fullFile;
  std::string line;

  while(getline(file, line)) {
    for (int i = 0; line.length() > i; i++) {
        fullFile += line[i];
    }
    fullFile += "\n";
  }

  file.close();
  return fullFile;
}

void Units :: update() {
  std::string armypth = "units.txt";
  std::string army;
  army = openFile(armypth);
  contents.set_text(army);
}

void Units :: keepUpdating() {
  while (true) {
    update();
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
}

void Units :: backgroudUpdate() {
  std::thread t(&Units::keepUpdating, this);
  t.detach();
}

Units :: Units() {
    add(scrolledWindow);
    scrolledWindow.add(fixed);

    set_title("Army Viewer");
    backgroudUpdate();

    getAvailUnits();

    fixed.add(contents);
    fixed.move(contents, 10, 110);
    fixed.add(possible);
    fixed.move(possible, 10, 10);

    resize(600,500);
    show_all();
}