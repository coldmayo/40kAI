#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <thread>
#include <chrono>

using namespace Glib;
using namespace Gtk;

class PopUp : public Gtk::Window {
  public : 
    PopUp();
    std::string openFile(std::string);
    bool isNum(char num);
    void update();
    void keepUpdating();
    void backgroudUpdate();
  private:
    Label contents;
    Fixed fixed;
    ScrolledWindow scrolledWindow;
    HeaderBar bar;
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
      } else if (ch == '0' && isNum(last)) {
        fullFile += '\n';
      } else if (isNum(ch) && ch != '0' && ch != '3') {
        fullFile += ch;
      } else if (isNum(ch) && ch == '3') {
        fullFile += '0';
        fullFile += '\x20';
      } else {
        fullFile += '_';
        fullFile += '\x20';
      }
      last = ch;
    }
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

void PopUp :: keepUpdating() {
  while (true) {
    update();
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
}

void PopUp :: backgroudUpdate() {
  std::thread t(&PopUp::keepUpdating, this);
  t.detach();
}

PopUp :: PopUp() {

  bar.set_show_close_button(true);
  set_titlebar(bar);

  add(scrolledWindow);
  scrolledWindow.add(fixed);
  
  bar.set_title("board.txt");

  backgroudUpdate();
  
  fixed.add(contents);
  fixed.move(contents, 0, 0);

  resize(800,500);
  show_all();
}