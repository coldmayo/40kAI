#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>

using namespace Glib;
using namespace Gtk;

class PopUp : public Gtk::Window {
  public : 
    PopUp();
    std::string openFile(std::string);
    bool isNum(char num);
    void update();
  private:
    Label contents;
    Fixed fixed;
    ScrolledWindow scrolledWindow;
    Button refresh;
};

bool PopUp :: isNum(char num) {
  std::string nums= "0123456789";
  for (char n : nums) {
    if (n == num) {
      return true;
    }
  }
  return false;
}

std::string PopUp :: openFile(std::string board) {
  std::fstream file;
  file.open(board, std::ios::in);
  std::string fullFile;
  char last; 
  if (!file) {
    std::cout << "File does not exist";
    fullFile.append(":(");
  } else {
    char ch;
    while (1) {
      file >> ch;
      if (file.eof()) {
        break;
      }
      if (last == '0' && ch != ',') {
        fullFile += '\n';
      } else if (ch == '0' && isNum(last) == true) {
        fullFile += '\n';
      }
      fullFile += ch;
      last = ch;
    }
    //std::cout << fullFile;
  }
  file.close();
  return fullFile;
}

void PopUp :: update() {
  std::string boardpth = "../board.txt";
  std::string board;
  board = openFile(boardpth);
  contents.set_text(board);
}

PopUp :: PopUp() {
  add(scrolledWindow);
  scrolledWindow.add(fixed);
  
  set_title("board.txt");
  std::string boardpth = "../board.txt";
  std::string board;
  board = openFile(boardpth);
  contents.set_text(board);

  refresh.set_label("Update...");
  refresh.signal_button_release_event().connect([&](GdkEventButton*) {
    update();
    return true;
  });
  
  fixed.add(contents);
  fixed.move(contents, 0, 30);
  fixed.add(refresh);
  fixed.move(refresh, 0, 0);

  resize(600,500);
  show_all();
}