#include <iostream>
#include <gtkmm.h>
#include <cstdlib>

using namespace Glib;
using namespace Gtk;

class Form : public Window {
public:
  Form() {

    const char *imgpth = "img/model_train.gif";

    add(scrolledWindow);
    scrolledWindow.add(fixed);
    
    tabControl1.set_size_request(370, 250);
    fixed.add(tabControl1);
    fixed.move(tabControl1, 10, 10);

    tabControl1.insert_page(tabPage2, "Train", 0);
    tabControl1.insert_page(tabPage3, "Show Trained Model", 1);
    tabControl1.insert_page(tabPage1, "Settings", 2);

    // settings tab

    labelPage1.set_label("Settings");
    tabControl1.set_tab_label(tabPage1, labelPage1);
    tabPage1.add(fixedTabPage1);

    fixedTabPage1.add(radioTop);
    fixedTabPage1.move(radioTop, 10, 10);
    radioTop.set_label("Top");
    radioTop.set_group(radioButtonGroup);
    radioTop.signal_toggled().connect([this]() {
       tabControl1.set_tab_pos(PositionType::POS_TOP);
    });

    fixedTabPage1.add(radioLeft);
    fixedTabPage1.move(radioLeft, 10, 40);
    radioLeft.set_label("Left");
    radioLeft.set_group(radioButtonGroup);
    radioLeft.signal_toggled().connect([this]() {
      tabControl1.set_tab_pos(PositionType::POS_LEFT);
    });

    fixedTabPage1.add(radioRight);
    fixedTabPage1.move(radioRight, 10, 70);
    radioRight.set_label("Right");
    radioRight.set_group(radioButtonGroup);
    radioRight.signal_toggled().connect([this]() {
      tabControl1.set_tab_pos(PositionType::POS_RIGHT);
    });

    fixedTabPage1.add(radioBottom);
    fixedTabPage1.move(radioBottom, 10, 100);
    radioBottom.set_label("Bottom");
    radioBottom.set_group(radioButtonGroup);
    radioBottom.signal_toggled().connect([this]() {
      tabControl1.set_tab_pos(PositionType::POS_BOTTOM);
    });

    // train tab

    labelPage2.set_label("Train");
    tabControl2.set_tab_label(tabPage2, labelPage2);
    tabPage2.add(fixedTabPage2);
    
    button1.set_label("Train");
    button1.signal_button_release_event().connect([&](GdkEventButton*) {
      system("cd ../../ ; ./train.sh");
      return true;
    });
    fixedTabPage2.add(button1);

    // show trained model tab

    labelPage3.set_label("Show Trained Model");
    tabControl3.set_tab_label(tabPage3, labelPage3);
    tabPage3.add(fixedTabPage3);
    
    fixedTabPage3.add(pictureBox1);
    pictureBox1.set_size_request(280, 280);
    pictureBox1.set(imgpth);

    set_title("GUI");
    resize(390, 270);
    show_all();
  }
  
private:
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
  RadioButtonGroup radioButtonGroup;
  RadioButton radioTop;
  RadioButton radioLeft;
  RadioButton radioRight;
  RadioButton radioBottom;
  Fixed fixedTabPage1;
  Fixed fixedTabPage2;
  Fixed fixedTabPage3;
  Button button1;
  int button1Clicked = 0;
};

int main(int argc, char* argv[]) {
  RefPtr<Application> application = Application::create(argc, argv);
  Form form;
  return application->run(form);
}