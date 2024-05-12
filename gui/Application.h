#ifndef APP_H
#define APP_H

#include <iostream>
#include <gtkmm.h>
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <thread>
#include <chrono>
#include "popup.h"

class Form : public Window {

public : 
  Form();
  int openPopUp();
  void update_picture();
  void updateInits(std::string model, std::string enemy);
  void startTrainInBackground();
  void startTrain();
  void runPlayAgainstModelInBackground();
  void playAgainstModel();
  inline bool exists_test (const std::string& name);

private:
  Window* aboutw_;
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
  Button showBoard;
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
  std::string foldPath;
  Label numOfGames;
  Label dimens;
  Label dimX;
  Label dimY;
  Entry enterDimensX;
  Entry enterDimensY;
  Button upX;
  Button downX;
  Button upY;
  Button downY;
  int button1Clicked = 0;
  int x;
  int y;
  bool open;
};

#endif