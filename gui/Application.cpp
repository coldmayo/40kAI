#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>

using namespace Glib;
using namespace Gtk;

const char *gifpth = "img/model_train.gif";
const char *imgpth = "img/icon.png";

class Form : public Window {

public : Form() {

    modelClass = " Space_Marine";
    enemyClass = " Space_Marine";
    path = " ";

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
    tabControl1.set_tab_label(tabPage2, labelPage2);
    tabPage2.add(fixedTabPage2);

    textbox1.set_text("Train Model:");
    status.set_text("Press the Train button to train a model");
    
    button1.set_label("Train");
    button1.signal_button_release_event().connect([&](GdkEventButton*) {
      updateInits(modelClass, enemyClass);
      if (exists_test("data.json")) {
        status.set_text("Training...");
        system("cd .. ; ./train.sh");
        status.set_text("Completed!");
        update_picture();
      }
      return true;
    });

    setIters.set_text("# of Lifetimes");

    button3.set_label("Clear Model Cache");
    button3.signal_button_release_event().connect([&](GdkEventButton*) {
      system("cd .. ; rm models/*");
      return true;
    });

    spmModel.set_label("Space Marine");
    spmModel.set_group(factionModel);
    spmModel.signal_toggled().connect([this]() {
      modelClass = " Space_Marine";
    });

    orksModel.set_label("Orks");
    orksModel.set_group(factionModel);
    orksModel.signal_toggled().connect([this]() {
      modelClass = " Orks";
    });

    spmEnemy.set_label("Space Marine");
    spmEnemy.set_group(factionEnemy);
    spmEnemy.signal_toggled().connect([this]() {
      enemyClass = " Space_Marine";
    });

    orksEnemy.set_label("Orks");
    orksEnemy.set_group(factionEnemy);
    orksEnemy.signal_toggled().connect([this]() {
      enemyClass = " Orks";
    });

    enemyFact.set_text("Enemy Faction: ");
    modelFact.set_text("Model Faction: ");

    fixedTabPage2.add(enemyFact);
    fixedTabPage2.move(enemyFact, 10, 100);
    fixedTabPage2.add(modelFact);
    fixedTabPage2.move(modelFact, 10, 80);
    fixedTabPage2.add(orksModel);
    fixedTabPage2.move(orksModel, 100, 80);
    fixedTabPage2.add(spmModel);
    fixedTabPage2.move(spmModel, 160, 80);
    fixedTabPage2.add(orksEnemy);
    fixedTabPage2.move(orksEnemy, 100, 100);
    fixedTabPage2.add(spmEnemy);
    fixedTabPage2.move(spmEnemy, 160, 100);
    fixedTabPage2.add(textbox1);
    fixedTabPage2.move(textbox1, 10, 10);
    fixedTabPage2.add(button1);
    fixedTabPage2.move(button1, 150, 130);
    fixedTabPage2.add(setIters);
    fixedTabPage2.move(setIters, 10, 40);
    fixedTabPage2.add(button3);
    fixedTabPage2.move(button3, 10, 130);
    fixedTabPage2.add(status);
    fixedTabPage2.move(status, 10, 170);

    // show trained model tab

    labelPage3.set_label("Show Trained Model");
    tabControl1.set_tab_label(tabPage3, labelPage3);
    tabPage3.add(fixedTabPage3);
    
    fixedTabPage3.add(pictureBox1);
    pictureBox1.set_size_request(280, 280);
    update_picture();

     // Play tab
    labelPage4.set_label("Play");
    tabControl1.set_tab_label(tabPage4, labelPage4);
    tabPage4.add(fixedTabPage4);
    button2.set_label("Play");
    textbox2.set_text("Play Against Model in Terminal:");
    button2.signal_button_release_event().connect([&](GdkEventButton*) {
      path = setModelFile.get_text();
      playAgainstModel(path);
      return true;
    });
    setModelFile.set_text(" ");
    button5.set_label("Choose");
    button5.signal_button_release_event().connect([&](GdkEventButton* event) {
      FileChooserDialog folderBrowserDialog("", FILE_CHOOSER_ACTION_OPEN);
      folderBrowserDialog.add_button("Cancel", RESPONSE_CANCEL);
      folderBrowserDialog.add_button("Open", RESPONSE_OK);
      folderBrowserDialog.set_current_folder(ustring::compose("%1/Home", ustring(getenv("HOME"))));
      folderBrowserDialog.set_transient_for(*this);

      auto filter_text = Gtk::FileFilter::create();
      filter_text->set_name("Pickle Files");
      filter_text->add_pattern("*.pickle");
      folderBrowserDialog.add_filter(filter_text);

      if (folderBrowserDialog.run() == RESPONSE_OK) {
        path = folderBrowserDialog.get_file()->get_path();
        std::cout << "File selected: " <<  path << std::endl;
        setModelFile.set_text(path);
      }
      return true;
    });

    fixedTabPage4.add(textbox2);
    fixedTabPage4.add(button2);
    fixedTabPage4.add(button5);
    fixedTabPage4.add(setModelFile);
    fixedTabPage4.move(textbox2, 10, 10);
    fixedTabPage4.move(button2, 10, 80);
    fixedTabPage4.move(button5, 10, 40);
    fixedTabPage4.move(setModelFile, 80, 40);

    set_title("GUI");
    resize(700, 600);
    show_all();

  }

private:
  void update_picture() {
    pictureBox1.set(gifpth);
  }
  void updateInits(std::string model, std::string enemy) {
    std::string command = "cd .. ; ./data.sh ";
    printf("%s\n", model.data());
    command.append(setIters.get_text().data());
    command.append(model);
    command.append(enemy);
    system(command.data());
    //printf("%s\n", command.data());
  }
  void playAgainstModel(std::string path) {
    std::string command = "cd .. ; ./play.sh ";
    if (strlen(path.data()) < 2) {
      command.append("None");
    } else {
      command.append(path);
    }
    //printf("%s\n", command.data());
    system(command.data());
  }
  inline bool exists_test (const std::string& name) {
    struct stat buffer;   
    return (stat (name.c_str(), &buffer) == 0); 
  }
  Image pictureBox1;
  Fixed fixed;
  ScrolledWindow scrolledWindow;
  Notebook tabControl1;
  Label labelPage1;
  Label labelPage2;
  Label labelPage3;
  Label labelPage4;
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
  Button button4;
  Button button5;
  Button button6;
  Label textbox;
  Label textbox2;
  Label textbox1;
  Label enemyFact;
  Label modelFact;
  Label status;
  Entry setIters;
  Entry setModelFile;
  RadioButtonGroup factionModel;
  RadioButton orksModel;
  RadioButton spmModel;
  RadioButtonGroup factionEnemy;
  RadioButton orksEnemy;
  RadioButton spmEnemy;
  std::string enemyClass;
  std::string modelClass;
  std::string path;
  int button1Clicked = 0;
};

int main(int argc, char* argv[]) {
  RefPtr<Application> application = Application::create(argc, argv);
  Form form;
  return application->run(form);
}