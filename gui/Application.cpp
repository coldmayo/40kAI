#include <iostream>
#include <gtkmm.h>
#include <cstdlib>

using namespace Glib;
using namespace Gtk;

const char *gifpth = "img/model_train.gif";
const char *imgpth = "img/icon.png";

class Form : public Window {
public:
  Form() {

    set_icon_from_file(imgpth);

    add(scrolledWindow);
    scrolledWindow.add(fixed);
    
    tabControl1.set_size_request(370, 250);
    fixed.add(tabControl1);
    fixed.move(tabControl1, 10, 10);

    tabControl1.insert_page(tabPage2, "Train", 0);
    tabControl1.insert_page(tabPage3, "Show Trained Model", 1);
    tabControl1.insert_page(tabPage4, "Play", 2);
    tabControl1.insert_page(tabPage1, "Settings", 3);

    // settings tab

    labelPage1.set_label("Settings");
    tabControl1.set_tab_label(tabPage1, labelPage1);
    tabPage1.add(fixedTabPage1);

    textbox.set_text("Change Tab Location:");
    fixedTabPage1.add(textbox);
    fixedTabPage1.move(textbox, 10, 10);

    fixedTabPage1.add(radioTop);
    fixedTabPage1.move(radioTop, 10, 40);
    radioTop.set_label("Top");
    radioTop.set_group(radioButtonGroup);
    radioTop.signal_toggled().connect([this]() {
       tabControl1.set_tab_pos(PositionType::POS_TOP);
    });

    fixedTabPage1.add(radioLeft);
    fixedTabPage1.move(radioLeft, 10, 70);
    radioLeft.set_label("Left");
    radioLeft.set_group(radioButtonGroup);
    radioLeft.signal_toggled().connect([this]() {
      tabControl1.set_tab_pos(PositionType::POS_LEFT);
    });

    fixedTabPage1.add(radioRight);
    fixedTabPage1.move(radioRight, 10, 100);
    radioRight.set_label("Right");
    radioRight.set_group(radioButtonGroup);
    radioRight.signal_toggled().connect([this]() {
      tabControl1.set_tab_pos(PositionType::POS_RIGHT);
    });

    fixedTabPage1.add(radioBottom);
    fixedTabPage1.move(radioBottom, 10, 130);
    radioBottom.set_label("Bottom");
    radioBottom.set_group(radioButtonGroup);
    radioBottom.signal_toggled().connect([this]() {
      tabControl1.set_tab_pos(PositionType::POS_BOTTOM);
    });

    // train tab

    labelPage2.set_label("Train");
    tabControl2.set_tab_label(tabPage2, labelPage2);
    tabPage2.add(fixedTabPage2);

    textbox1.set_text("Train Model:");
    status.set_text("Press the Train button to train a model");
    
    button1.set_label("Train");
    button1.signal_button_release_event().connect([&](GdkEventButton*) {
      status.set_text("Training...");
      system("cd .. ; ./train.sh");
      status.set_text("Completed!");
      update_picture();
      return true;
    });

    button3.set_label("Clear Model Cache");
    button3.signal_button_release_event().connect([&](GdkEventButton*) {
      system("cd .. ; rm models/*");
      return true;
    });

    fixedTabPage2.add(textbox1);
    fixedTabPage2.move(textbox1, 10, 10);
    fixedTabPage2.add(button1);
    fixedTabPage2.move(button1, 10, 70);
    fixedTabPage2.add(button3);
    fixedTabPage2.move(button3, 10, 40);
    fixedTabPage2.add(status);
    fixedTabPage2.move(status, 10, 110);

    // show trained model tab

    labelPage3.set_label("Show Trained Model");
    tabControl3.set_tab_label(tabPage3, labelPage3);
    tabPage3.add(fixedTabPage3);
    
    fixedTabPage3.add(pictureBox1);
    pictureBox1.set_size_request(280, 280);
    update_picture();

     // Play tab
    tabPage4.add(fixedTabPage4);
    button2.set_label("Play");
    textbox2.set_text("Play Against Model in Terminal:");
    button2.signal_button_release_event().connect([&](GdkEventButton*) {
      system("cd .. ; ./play.sh");
      return true;
    });
    fixedTabPage4.add(textbox2);
    fixedTabPage4.add(button2);
    fixedTabPage4.move(textbox2, 10, 10);
    fixedTabPage4.move(button2, 10, 40);

    set_title("GUI");
    resize(700, 600);
    show_all();

  }
  
private:
  void update_picture() {
    pictureBox1.set(gifpth);
  }
  Image pictureBox1;
  Fixed fixed;
  ScrolledWindow scrolledWindow;
  Notebook tabControl1;
  Notebook tabControl2;
  Notebook tabControl3;
  Label labelPage1;
  Label labelPage2;
  Label labelPage3;
  Label label1;
  Frame tabPage1;
  Frame tabPage2;
  Frame tabPage3;
  Frame tabPage4;
  RadioButtonGroup radioButtonGroup;
  RadioButton radioTop;
  RadioButton radioLeft;
  RadioButton radioRight;
  RadioButton radioBottom;
  Fixed fixedTabPage1;
  Fixed fixedTabPage2;
  Fixed fixedTabPage3;
  Fixed fixedTabPage4;
  Button button1;
  Button button2;
  Button button3;
  Label textbox;
  Label textbox2;
  Label textbox1;
  Label status;
  int button1Clicked = 0;
};

int main(int argc, char* argv[]) {
  RefPtr<Application> application = Application::create(argc, argv);
  Form form;
  return application->run(form);
}