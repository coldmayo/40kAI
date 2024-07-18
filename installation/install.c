#include <stdio.h> 
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <dirent.h>
#include <errno.h>
#include <unistd.h>
#include <stdbool.h>

void showIcon() {
    FILE *fptr;
    char c;

    fptr = fopen("ascii-icon.txt", "r");

    c = fgetc(fptr);
    while (c != EOF) { 
        printf ("%c", c); 
        c = fgetc(fptr); 
    }
  
    fclose(fptr);
}

char * slice_str(char * str, char * buffer, int start, int end) {
    int j = 0;
    for (int i = start; i <= end && str[i] != '\0'; ++i) {
        buffer[j++] = str[i];
    }
    buffer[j] = '\0';
    return buffer;
}

int parseInput(char *comm) {
    char buffer[50];
    int running = 0;
    if (strcmp(comm, "install") == 0) {
		system("cd .. ; cd gui/build ; cmake --build . --config Debug");
        char buffer2[50];
        printf("\nStarting installation...\n");
        printf("Installing Application...\n");
        const char *path = "Path=";
        char path_actual[PATH_MAX + strlen(path) + 1]; 
        const char *iconPath = "img/icon.png";
        const char *execPath = "build/Application";
        const char *symlinkpath = "gui/";
        char user[50];
        char actualpath[PATH_MAX];
        if (realpath("../../40kAI/", actualpath) != NULL) {
            strcat(actualpath, "/");
            strcpy(path_actual, path);
            strcat(path_actual, actualpath);
            strcat(path_actual, symlinkpath);
            printf("%s\n", path_actual);
            strcpy(buffer2, actualpath);

            int len = strlen(actualpath);

            // find the users username for application install path

            for (int i = 0; i<len; i++) {
                if (i > 4) {
                    slice_str(actualpath, buffer, i - 5, i);
                    if (strcmp(buffer, "/home/") == 0) {
                        for (int j = i+1; j < len; j++) {
                            if (actualpath[j] == '/') {
                                slice_str(actualpath, user, i+1, j-1);
                                break;
                            }
                        }
                    }
                }
            }
        } else {
            printf("Error: Unable to resolve symbolic link.\n");
            return running;
        }

        FILE *fptr;
        char desktopFile[100];
        strcpy(desktopFile, "/home/");
        strcat(desktopFile, user);
        strcat(desktopFile, "/.local/share/applications/org.kde.40kAI.desktop");
        printf("%s\n", desktopFile);
        fptr = fopen(desktopFile, "w");
        if (fptr == NULL) {
            perror("fopen");
            return running;
        }

        fprintf(fptr, "[Desktop Entry]\n");
        fprintf(fptr, "Type=Application\n");
        fprintf(fptr, "Name=40kAI\n");
        fprintf(fptr, "StartupNotify=true\n");
        fprintf(fptr, "Terminal=true\n");
        fprintf(fptr, "%s\n", path_actual);      

        fprintf(fptr, "Icon=%sgui/img/icon.png\n", actualpath);

        fprintf(fptr, "Exec=%sgui/build/Application\n", actualpath);
        fclose(fptr);

        int resp = 0;
        char ans[20];
        while (resp == 0) {
            printf("Install to Desktop? (y/n): ");
            scanf("%s", ans);
            if (strcmp(ans, "y")==0 || strcmp(ans, "yes")==0) {
                FILE *fptr;
                char desktopDir[PATH_MAX] = "/home/";
                strcat(desktopDir, user);
                strcat(desktopDir, "/Desktop/org.kde.40kAI.desktop");
                printf("%s\n", desktopDir);
                fptr = fopen(desktopDir, "w");

                fprintf(fptr, "[Desktop Entry]\n");
                fprintf(fptr, "Type=Application\n");
                fprintf(fptr, "Name=40kAI\n");
                fprintf(fptr, "StartupNotify=true\n");
                fprintf(fptr, "Terminal=true\n");
                fprintf(fptr, "%s\n", path_actual);      

                fprintf(fptr, "Icon=%sgui/img/icon.png\n", actualpath);

                fprintf(fptr, "Exec=%sgui/build/Application\n", actualpath);

                fclose(fptr);

                resp = 1;
            } else if (strcmp(ans, "n")==0 || strcmp(ans, "no")==0) {
                resp = 1;
            } else {
                printf("Its a yes or no question, do you want to ");
            }

        }

        printf("Application Installed!\n");
        printf("Installing Python Packages...\n");
        DIR* dir = opendir("../.venv/");
        if (dir) {
            printf("Virtual Environment found, no need to install\n");
            closedir(dir);
        } else if (ENOENT == errno) {
            printf("No Virtual Environment found, Installing...\n");
            system("cd .. ; python -m venv .venv");
        }
        system("cd .. ; source .venv/bin/activate ; cd gym_mod ; pip install .");
        printf("Packages Installed!\n");
        printf("Installing Unit and Weapon Data...\n");
        system("cd .. ; cd data_collector/unit_data ; touch links.json ; ./scrape.sh");
        printf("Data Installed!\n");
        printf("Installation Complete!\n");
        
    } else if (strcmp(comm, "uninstall") == 0) {
        char yaOrna[100];
        printf("Are you sure? (y/n)> ");
        scanf("%s", yaOrna);
		bool ans = false;
        while (ans == false) {
			if (strcmp(yaOrna, "n") == 0 || strcmp(yaOrna, "no") == 0) {
				ans = true;
				printf("Whew, thought we lost you there\n");
				return running;
			} else if (strcmp(yaOrna, "y") == 0 || strcmp(yaOrna, "yes") == 0) {
				ans = true;
				printf("Sad to see you go\n");
        		printf("Starting uninstallation...");
        		system("cd .. ; cd gui/build ; rm Application");
        		char actualpath[PATH_MAX];
        		char user[50];
        		if (realpath("../../40kAI/", actualpath) != NULL) {
            		int len = strlen(actualpath);
            		for (int i = 0; i < len; i++) {
                		if (i > 4) {
                    		slice_str(actualpath, buffer, i - 5, i);
                    		if (strcmp(buffer, "/home/") == 0) {
                        		for (int j = i+1; j<len; j++) {
                            		if (actualpath[j] == '/') {
                                		slice_str(actualpath, user, i+1, j-1);
                                		break;
                            		}
                        		}
                    		}
               			}
            		}
        		}

        		char desktopFile[100];
        		char command[50];
        		strcpy(desktopFile, "/home/");
        		strcat(desktopFile, user);
        		strcat(desktopFile, "/.local/share/applications/org.kde.40kAI.desktop");
        		strcpy(command, "rm ");
        		strcat(command, desktopFile);
        		system(command);

        		char desktopDir[PATH_MAX] = "/home/";
        		strcat(desktopDir, user);
        		strcat(desktopDir, "/Desktop/org.kde.40kAI.desktop");

        		if (access(desktopDir, F_OK) == 0) {
            		char command[50];
            		strcpy(command, "rm ");
            		strcat(command, desktopDir);
            		system(command);
        		}

        		system("cd .. ; source .venv/bin/activate ; cd gym_mod ; pip uninstall Warhammer40kAI");
        		printf("\nUninstallation Complete :(\n");

    		} else {
				printf("\nCommand not recognized, yes or no> ");
				scanf("%s", yaOrna);
			}
        }
        return running;
    } else if (strcmp(comm, "update") == 0) {
		system("cd .. ; git fetch origin ; git pull");   // most recent from main
		printf("Reinstallation starting...\n");
		system("cd .. ; cd gui/build ; cmake --build . --config Debug");
		printf("GUI Updated\n");
		system("cd .. ; source .venv/bin/activate ; cd gym_mod ; pip install .");
        printf("Packages Installed!\n");
        printf("Installing Unit and Weapon Data...\n");
        system("cd .. ; cd data_collector/unit_data ; touch links.json ; ./scrape.sh");
        printf("Data Installed!\n");
        		
    } else if (strcmp(comm, "help") == 0) {
        printf("Commands:\ninstall: Installs the 40kAI app\nupdate: Updates the application\nuninstall: Uninstalls the 40kAI app (why would you do this)\nexit: leave the installation prompt\n");
    } else if (strcmp(comm, "exit") == 0 || strcmp(comm, "quit") == 0) {
        running = 1;
        return running;
    } else {
        printf("%s is not a command, use the help command\n", comm);
    }
    return running;
}
int main() {
    
    char comm[100];
    int running = 0;

    showIcon();
    printf("\nWelcome to the 40kAI Install Medium\n");
    printf("Use the 'help' command to see the available commands\n");
    while (running == 0) {
        printf("\n> ");
        scanf("%s", comm);
        running = parseInput(comm);
    }
    printf("Exiting...\n");
}
