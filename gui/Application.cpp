#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <thread>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <vector>
#include <algorithm>
#include <nlohmann/json.hpp>
#include "include/Application.h"
#include "include/popup.h"
#include "include/units.h"
#include "include/warn.h"
#include "include/help.h"

using namespace Glib;
using namespace Gtk;
namespace fs = std::filesystem;

using json = nlohmann::json;

std::string gifpth = "img/model_train.gif";
std::string rewpth = "img/reward.png";
std::string losspth = "img/loss.png";
std::string eplenpth = "img/epLen.png";
std::string imgpth = "img/icon.png";

Form :: Form() {

  modelClass = " Space_Marine";
  enemyClass = " Space_Marine";
  path = " ";
  open = false;
  x = 60;
  y = 40;
  training = false;
  playing = false;

  bar.set_show_close_button(true);
  help.set_image_from_icon_name("help-about");
  help.signal_button_release_event().connect([&](GdkEventButton*){
    openHelpMenu();
    return true;
  });
  bar.pack_end(help);
  set_titlebar(bar);

  add(scrolledWindow);
  scrolledWindow.add(fixed);

  fixed.add(tabControl1);
  fixed.move(tabControl1, 10, 10);

  tabControl1.insert_page(tabPage2, "Train", 0);
  tabControl1.insert_page(tabPage3, "Show Trained Model", 1);
  tabControl1.insert_page(tabPage5, "Metrics", 2);
  tabControl1.insert_page(tabPage4, "Play", 3);
  tabControl1.insert_page(tabPage1, "Settings", 4);

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

  savetoTxt(enemyUnits, modelUnits);

  labelPage2.set_label("Train");
  tabControl1.set_tab_label(tabPage2, labelPage2);
  tabPage2.add(fixedTabPage2);

  textbox1.set_text("Train Model:");
  status.set_text("Press the Train button to train a model");
    
  button1.set_label("Train");
  button1.signal_button_release_event().connect([&](GdkEventButton*) {
    updateInits(modelClass, enemyClass);
    if (exists_test("data.json") && training == false) {
      status.set_text("Training...");
      startTrainInBackground();
    }
    return true;
  });

  numOfGames.set_text("# of Games in Training:");
  setIters.set_text("100");

  modelUnitLabel.set_text("Enter Model Units:");
  enemyUnitLabel.set_text("Enter Player Units:");
  openArmyPopup.set_label("Army Viewer");
  openArmyPopup.signal_button_release_event().connect([&](GdkEventButton*) {
    openArmyView();
    return true;
  });

  dimens.set_text("Dimensions of Board: ");

  dimX.set_text("X : ");
  enterDimensX.set_text(std::to_string(x));
  upX.set_label("+");
  upX.signal_button_release_event().connect([&](GdkEventButton*) {
    x+=10;
    enterDimensX.set_text(std::to_string(x));
    return true;
  });
  downX.set_label("-");
  downX.signal_button_release_event().connect([&](GdkEventButton*) {
    x-=10;
    enterDimensX.set_text(std::to_string(x));
    return true;
  });

  dimY.set_text("Y :");
  enterDimensY.set_text(std::to_string(y));
  upY.set_label("+");
  upY.signal_button_release_event().connect([&](GdkEventButton*) {
    y+=10;
    enterDimensY.set_text(std::to_string(y));
    return true;
  });
  downY.set_label("-");
  downY.signal_button_release_event().connect([&](GdkEventButton*) {
    y-=10;
    enterDimensY.set_text(std::to_string(y));
    return true;
  });

  button3.set_label("Clear Model Cache");
  button3.signal_button_release_event().connect([&](GdkEventButton*) {
    std::string mess = "Warning: You are about to delete all of the saved models";
    openWarnMenu(mess, 0);
    return true;
  });

  spmModel.set_label("Space Marine");
  spmModel.set_group(factionModel);
  spmModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Space_Marine";
  });

  orksModel.set_label("Orks");
  orksModel.set_group(factionModel);
  orksModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Orks";
  });

  sobModel.set_label("Sisters of Battle");
  sobModel.set_group(factionModel);
  sobModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Sisters_of_Battle";
  });

  adcModel.set_label("Adeptus Custodes");
  adcModel.set_group(factionModel);
  adcModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Custodes";
  });

  tyrModel.set_label("Tyrannids");
  tyrModel.set_group(factionModel);
  tyrModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Tyrannids";
  });

  milModel.set_label("Astra Militarum");
  milModel.set_group(factionModel);
  milModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Militarum";
  });

  tauModel.set_label("Tau");
  tauModel.set_group(factionModel);
  tauModel.signal_toggled().connect([this]() {
    modelUnits.clear();
    modelClass = " Tau";
  });

  spmEnemy.set_label("Space Marine");
  spmEnemy.set_group(factionEnemy);
  spmEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Space_Marine";
  });

  orksEnemy.set_label("Orks");
  orksEnemy.set_group(factionEnemy);
  orksEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Orks";
  });

  sobEnemy.set_label("Sisters of Battle");
  sobEnemy.set_group(factionEnemy);
  sobEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Sisters_of_Battle";
  });

  adcEnemy.set_label("Adeptus Custodes");
  adcEnemy.set_group(factionEnemy);
  adcEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Custodes";
  });

  tyrEnemy.set_label("Tyrannids");
  tyrEnemy.set_group(factionEnemy);
  tyrEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Tyrannids";
  });

  tauEnemy.set_label("Tau");
  tauEnemy.set_group(factionEnemy);
  tauEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Tau";
  });

  milEnemy.set_label("Astra Militarum");
  milEnemy.set_group(factionEnemy);
  milEnemy.signal_toggled().connect([this]() {
    enemyUnits.clear();
    enemyClass = " Militarum";
  });

  enemyFact.set_text("Player Faction: ");
  modelFact.set_text("Model Faction: ");
  clearAllModel.set_label("Clear");
  clearAllModel.signal_button_release_event().connect([&](GdkEventButton*) {
    modelUnits.clear();
    savetoTxt(enemyUnits, modelUnits);
    return true;
  });
  clearAllEnemy.set_label("Clear");
  clearAllEnemy.signal_button_release_event().connect([&](GdkEventButton*) {
    enemyUnits.clear();
    savetoTxt(enemyUnits, modelUnits);
    return true;
  });
  enemyEnter.set_label("Add");
  enemyEnter.signal_button_release_event().connect([&](GdkEventButton*) {
    if (isValidUnit(1, enterEnemyUnit.get_text()) == true) {
      savetoTxt(enemyUnits, modelUnits);
    }
    return true;
  });
  modelEnter.set_label("Add");
  modelEnter.signal_button_release_event().connect([&](GdkEventButton*) {
    if (isValidUnit(0, enterModelUnit.get_text()) == true) {
      savetoTxt(enemyUnits, modelUnits);
    }
    return true;
  });

  // add initial armies (Space Marines) 

  std::string unit = "Apothecary";
  modelUnits.push_back(unit);
  unit = "Eliminator Squad";
  modelUnits.push_back(unit); 

  unit = "Apothecary";
  enemyUnits.push_back(unit);
  unit = "Eliminator Squad";
  enemyUnits.push_back(unit);  

  savetoTxt(modelUnits, enemyUnits);

  fixedTabPage2.add(dimX);
  fixedTabPage2.move(dimX, 10, 265);
  fixedTabPage2.add(dimens);
  fixedTabPage2.move(dimens, 10, 240);
  fixedTabPage2.add(enterDimensX);
  fixedTabPage2.move(enterDimensX, 30, 260);
  fixedTabPage2.add(upX);
  fixedTabPage2.move(upX, 200, 260);
  fixedTabPage2.add(downX);
  fixedTabPage2.move(downX, 220, 260);

  fixedTabPage2.add(dimY);
  fixedTabPage2.move(dimY, 260, 265);
  fixedTabPage2.add(enterDimensY);
  fixedTabPage2.move(enterDimensY, 260+30, 260);
  fixedTabPage2.add(upY);
  fixedTabPage2.move(upY, 250+200, 260);
  fixedTabPage2.add(downY);
  fixedTabPage2.move(downY, 250+220, 260);

  fixedTabPage2.add(numOfGames);
  fixedTabPage2.move(numOfGames, 10, 45);
  fixedTabPage2.add(enemyFact);
  fixedTabPage2.move(enemyFact, 10, 120);
  fixedTabPage2.add(modelFact);
  fixedTabPage2.move(modelFact, 10, 80);
  fixedTabPage2.add(orksModel);
  fixedTabPage2.move(orksModel, 100, 80);
  fixedTabPage2.add(spmModel);
  fixedTabPage2.move(spmModel, 160, 80);
  fixedTabPage2.add(sobModel);
  fixedTabPage2.move(sobModel, 270, 80);
  fixedTabPage2.add(adcModel);
  fixedTabPage2.move(adcModel, 390, 80);
  fixedTabPage2.add(tyrModel);
  fixedTabPage2.move(tyrModel, 530, 80);
  fixedTabPage2.add(milModel);
  fixedTabPage2.move(milModel, 100, 100);
  fixedTabPage2.add(tauModel);
  fixedTabPage2.move(tauModel, 220, 100);
  fixedTabPage2.add(orksEnemy);
  fixedTabPage2.move(orksEnemy, 100, 120);
  fixedTabPage2.add(spmEnemy);
  fixedTabPage2.move(spmEnemy, 160, 120);
  fixedTabPage2.add(sobEnemy);
  fixedTabPage2.move(sobEnemy, 270, 120);
  fixedTabPage2.add(adcEnemy);
  fixedTabPage2.move(adcEnemy, 390, 120);
  fixedTabPage2.add(tyrEnemy);
  fixedTabPage2.move(tyrEnemy, 530, 120);
  fixedTabPage2.add(milEnemy);
  fixedTabPage2.move(milEnemy, 100, 140);
  fixedTabPage2.add(tauEnemy);
  fixedTabPage2.move(tauEnemy, 220, 140);
  fixedTabPage2.add(modelUnitLabel);
  fixedTabPage2.move(modelUnitLabel, 10, 163);
  fixedTabPage2.add(enterModelUnit);
  fixedTabPage2.move(enterModelUnit, 130, 160);
  fixedTabPage2.add(modelEnter);
  fixedTabPage2.move(modelEnter, 300, 160);
  fixedTabPage2.add(enemyUnitLabel);
  fixedTabPage2.move(enemyUnitLabel, 10, 203);
  fixedTabPage2.add(enterEnemyUnit);
  fixedTabPage2.move(enterEnemyUnit, 130, 200);
  fixedTabPage2.add(enemyEnter);
  fixedTabPage2.move(enemyEnter, 300, 200);
  fixedTabPage2.add(clearAllModel);
  fixedTabPage2.move(clearAllModel, 340, 160);
  fixedTabPage2.add(clearAllEnemy);
  fixedTabPage2.move(clearAllEnemy, 340, 200);
  fixedTabPage2.add(openArmyPopup);
  fixedTabPage2.move(openArmyPopup, 400, (160+200)/2);
  fixedTabPage2.add(textbox1);
  fixedTabPage2.move(textbox1, 10, 10);
  fixedTabPage2.add(button1);
  fixedTabPage2.move(button1, 150, 300);
  fixedTabPage2.add(setIters);
  fixedTabPage2.move(setIters, 160, 40);
  fixedTabPage2.add(button3);
  fixedTabPage2.move(button3, 10, 300);
  fixedTabPage2.add(status);
  fixedTabPage2.move(status, 10, 350);

    // show trained model tab

  labelPage3.set_label("Show Trained Model");
  tabControl1.set_tab_label(tabPage3, labelPage3);
  tabPage3.add(fixedTabPage3);
    
  fixedTabPage3.add(pictureBox1);
  pictureBox1.set_size_request(280, 280);
  update_picture();

  // show metrics tab
  labelPage5.set_label("Model Metrics");
  tabControl1.set_tab_label(tabPage5, labelPage5);
  tabPage5.add(fixedTabPage5);
  
  chooseMetrics.set_label("Choose");
  chooseMetrics.signal_button_release_event().connect([&](GdkEventButton * event){
	FileChooserDialog folderBrowserDialog("", FILE_CHOOSER_ACTION_OPEN);
    folderBrowserDialog.add_button("Cancel", RESPONSE_CANCEL);
    folderBrowserDialog.add_button("Open", RESPONSE_OK);
    char resolved_path[PATH_MAX];
    realpath("../../40kAI", resolved_path);
    strcat(resolved_path, "/models");
    folderBrowserDialog.set_current_folder(resolved_path);
    folderBrowserDialog.set_transient_for(*this);

    auto filter_text = Gtk::FileFilter::create();
    filter_text->set_name("Pickle Files");
    filter_text->add_pattern("*.pickle");
    folderBrowserDialog.add_filter(filter_text);

    if (folderBrowserDialog.run() == RESPONSE_OK) {
      path = folderBrowserDialog.get_file()->get_path();
      changeMetrics(path);
    }
    return true;
  });

  fixedTabPage5.add(metricBox);
  fixedTabPage5.add(metricBox2);
  fixedTabPage5.add(metricBox3);
  fixedTabPage5.add(chooseMetrics);
  fixedTabPage5.move(metricBox2, 640/2, 0);
  fixedTabPage5.move(metricBox3, 640/4, 480/2+10);
  fixedTabPage5.move(chooseMetrics, 620/2, 500);
  update_metrics();

     // Play tab
  labelPage4.set_label("Play");
  tabControl1.set_tab_label(tabPage4, labelPage4);
  tabPage4.add(fixedTabPage4);
  button2.set_label("Play");
  textbox2.set_text("Play Against Model in Terminal:");
  button2.signal_button_release_event().connect([&](GdkEventButton*) {
    if (playing == false) {
      runPlayAgainstModelInBackground();
    }
    return true;
  });
  setModelFile.set_text(" ");
  button5.set_label("Choose");
  button5.signal_button_release_event().connect([&](GdkEventButton* event) {
    FileChooserDialog folderBrowserDialog("", FILE_CHOOSER_ACTION_OPEN);
    folderBrowserDialog.add_button("Cancel", RESPONSE_CANCEL);
    folderBrowserDialog.add_button("Open", RESPONSE_OK);
    char resolved_path[PATH_MAX];
    realpath("../../40kAI", resolved_path);
    strcat(resolved_path, "/models");
    folderBrowserDialog.set_current_folder(resolved_path);
    folderBrowserDialog.set_transient_for(*this);

    auto filter_text = Gtk::FileFilter::create();
    filter_text->set_name("Pickle Files");
    filter_text->add_pattern("*.pickle");
    folderBrowserDialog.add_filter(filter_text);

    if (folderBrowserDialog.run() == RESPONSE_OK) {
      path = folderBrowserDialog.get_file()->get_path();
      setModelFile.set_text(path);
    }
    return true;
  });
  showBoard.set_label("Show Board");
  showBoard.signal_button_release_event().connect([&](GdkEventButton* event) {
    openPopUp();
    return true;
  });

  fixedTabPage4.add(textbox2);
  fixedTabPage4.add(button2);
  fixedTabPage4.add(showBoard);
  fixedTabPage4.add(button5);
  fixedTabPage4.add(setModelFile);
  fixedTabPage4.move(textbox2, 10, 10);
  fixedTabPage4.move(showBoard, 60, 80);
  fixedTabPage4.move(button2, 10, 80);
  fixedTabPage4.move(button5, 10, 40);
  fixedTabPage4.move(setModelFile, 80, 40);

  bar.set_title("40kAI GUI");
  resize(700, 600);
  show_all();
}

void Form :: changeMetrics(std::string path) {
    std::string jsonID = path.substr(path.length()-16,9);
	
	if (jsonID[0] == '-') {
		jsonID = path.substr(path.length()-15,8);
	} 
	
	std::ifstream infile("../models/data_"+jsonID+".json");
	json j;
	infile >> j;

	losspth = j.at("loss");
	rewpth = j.at("reward");
	eplenpth = j.at("epLen");

	update_metrics();
}

int Form :: openPopUp() {
  boardShow = new PopUp;
  boardShow->show();
  return 0;
}

int Form :: openArmyView() {
  armyView = new Units;
  armyView->show();
  return 0;
}

int Form :: openWarnMenu(std::string mess, int comm) {
  warn = new Warn(mess, comm);
  warn->show();
  return 0;
}

int Form :: openHelpMenu() {
  helpMenu = new Help;
  helpMenu->show();
  return 0;
}

std::string Form :: toLower(std::string data) {
  std::transform(data.begin(), data.end(), data.begin(),[](unsigned char c){ return std::tolower(c); });
  return data;
}

// model: id = 0
// enemy: id = 1

bool Form :: isValidUnit(int id, std::string name) {
  std::ifstream infile("../gym_mod/gym_mod/engine/unitData.json");
  json j;
  infile >> j;

  const auto& unitData = j.at("UnitData");
  for (const auto& unit : unitData) {
    if (strcmp(toLower(unit.at("Name").get<std::string>()).data(), toLower(name).data()) == 0) {
      if (id == 0 && strcmp(toLower(unit.at("Army").get<std::string>()).data(), toLower(modelClass.substr(1, modelClass.length())).data()) == 0) {
        modelUnits.push_back(unit.at("Name").get<std::string>());
        return true;
      } else if (id == 1 && strcmp(toLower(unit.at("Army").get<std::string>()).data(), toLower(enemyClass.substr(1, enemyClass.length())).data()) == 0) {
        enemyUnits.push_back(unit.at("Name").get<std::string>());
        return true;
      }
    }
  }
  return false;
}

void Form :: savetoTxt(std::vector<std::string> enemyUnits, std::vector<std::string> modelUnits) {

  std::ofstream outfile("units.txt");
  outfile << "Player Units\n";
  for (const auto& str : enemyUnits) {
    outfile << str << std::endl;
  }
  outfile << "Model Units\n";
  for (const auto& str : modelUnits) {
    outfile << str << std::endl;
  }
  outfile.close();
}

void Form :: update_picture() {
  pictureBox1.set(gifpth);
}

void Form :: update_metrics() {
  // scale down images
  Glib::RefPtr<Gdk::Pixbuf> m_Pixbuf = Gdk::Pixbuf::create_from_file(rewpth);
  Glib::RefPtr<Gdk::Pixbuf> m_Pixbuf2 = Gdk::Pixbuf::create_from_file(losspth);
  Glib::RefPtr<Gdk::Pixbuf> m_Pixbuf3 = Gdk::Pixbuf::create_from_file(eplenpth);
  
  Glib::RefPtr<Gdk::Pixbuf> scaled_pixbuf = m_Pixbuf->scale_simple(350, 250, Gdk::INTERP_BILINEAR);
  metricBox.set(scaled_pixbuf);
  Glib::RefPtr<Gdk::Pixbuf> scaled_pixbuf2 = m_Pixbuf2->scale_simple(350, 250, Gdk::INTERP_BILINEAR);
  metricBox2.set(scaled_pixbuf2);
  Glib::RefPtr<Gdk::Pixbuf> scaled_pixbuf3 = m_Pixbuf3->scale_simple(350, 230, Gdk::INTERP_BILINEAR);
  metricBox3.set(scaled_pixbuf3);
}

void Form :: updateInits(std::string model, std::string enemy) {
  std::string command = "cd .. ; ./data.sh ";
  command.append(setIters.get_text().data());
  command.append(model);
  command.append(enemy);
  command.append(" ");
  command.append(enterDimensX.get_text().data());
  command.append(" ");
  command.append(enterDimensY.get_text().data());
  system(command.data());
}

void Form :: startTrainInBackground() {
  std::thread t(&Form::startTrain, this);
  t.detach();
}

void Form :: startTrain() {
  training = true;
  system("clear");
  system("cd .. ; ./train.sh");
  status.set_text("Completed!");
  training = false;
  update_picture();
  update_metrics();
}

void Form :: runPlayAgainstModelInBackground() {
  std::thread t(&Form::playAgainstModel, this);
  t.detach();
}
  
void Form :: playAgainstModel() {
  path = setModelFile.get_text();
  std::string command = "cd .. ; ./play.sh ";
  if (strlen(path.data()) < 2) {
    command.append("None");
  } else {
    command.append(path);
  }
  playing = true;
  system("clear");
  system(command.data());
  playing = false;
}

inline bool Form :: exists_test (const std::string& name) {
  struct stat buffer;   
  return (stat (name.c_str(), &buffer) == 0); 
}
