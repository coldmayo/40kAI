//#include <iostream>
#include <stdio.h> 
#include <stdlib.h>
#include <string.h>
#include <limits.h>

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
        char buffer2[50];
        printf("\nStarting installation...\n");
        const char *path = "Path=";
        const char *iconPath = "img/icon.png";
        const char *execPath = "build/Application";
        const char *symlinkpath = "gui/";
        char user[50];
        char actualpath[PATH_MAX];
        if (realpath("install.c", actualpath) != NULL) {
            int len = strlen(actualpath);
            for (int i = 0; i < len; i++) {
                if (i > 4) {
                    slice_str(actualpath, buffer, i - 5, i);
                    if (strcmp(buffer, "/home/") == 0) {
                        for (int j = i+1; j<len; j++) {
                            if (actualpath[j] == '/') {
                                slice_str(actualpath, user, i+1, j-1);
                                //printf("%s\n",slice_str(actualpath, user, i+1, j-1));
                                break;
                            }
                        }
                    }

                    if (strcmp(buffer, "40kAI/") == 0) {
                        slice_str(actualpath, buffer, 0, i);
                        strcat(buffer, symlinkpath);
                        //printf("%s\n", buffer);
                        break;
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
        fptr = fopen(desktopFile, "w");
        if (fptr == NULL) {
            perror("fopen");
            return running;
        }
        char path_actual[PATH_MAX + strlen(path) + 1]; 
        strcpy(path_actual, path);
        strcat(path_actual, buffer);
        strcpy(buffer2, buffer);

        fprintf(fptr, "[Desktop Entry]\n");
        fprintf(fptr, "Type=Application\n");
        fprintf(fptr, "Name=40kAI\n");
        fprintf(fptr, "StartupNotify=true\n");
        fprintf(fptr, "Terminal=true\n");
        fprintf(fptr, "%s\n", path_actual);

        strcpy(path_actual, "Icon=");
        strcat(path_actual, strcat(buffer, "img/icon.png"));        

        fprintf(fptr, "%s\n", path_actual);

        strcpy(path_actual, "Exec=");
        strcat(path_actual, strcat(buffer2, "build/Application"));  

        fprintf(fptr, "%s\n", path_actual);
        fclose(fptr);

        printf("Installation Complete!\n");
    } else if (strcmp(comm, "uninstall") == 0) {
        printf("Sad to see you go\n");
        printf("Starting uninstallation...");
        char actualpath[PATH_MAX];
        char user[50];
        if (realpath("install.c", actualpath) != NULL) {
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

        printf("\nInstallation Complete :(\n");

    } else if (strcmp(comm, "help") == 0) {

        printf("Commands:\ninstall: Installs the 40kAI app\nuninstall: Uninstalls the 40kAI app (why would you do this)\nexit: leave the installation prompt\n");

    } else if (strcmp(comm, "exit") == 0) {
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
    printf("\nWelcome to the 40kAI Install\n");
    printf("Use the 'help' command to see the available commands\n");
    while (running == 0) {
        printf("\n> ");
        scanf("%s", comm);
        running = parseInput(comm);
    }
    printf("Exiting...\n");
}