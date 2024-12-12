#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include "utils.h"

extern pid_t *child_pids;
extern int num_scripts;
int launch_python_scripts(int num_scripts, const char **scripts) {
    child_pids = malloc(num_scripts * sizeof(pid_t));
    if (!child_pids) {
        perror("Erreur d'allocation mémoire pour les PID");
        return -1;
    }

    for (int i = 0; i < num_scripts; i++) {
        pid_t pid = fork();
        if (pid == -1) {
            perror("Erreur lors de la création d'un processus enfant");
            return -1;
        } else if (pid == 0) {
            execlp("python3", "python3", scripts[i], NULL);
            perror("Erreur lors de l'exécution du script Python");
            exit(EXIT_FAILURE);
        } else {
            child_pids[i] = pid;
            printf("Script Python lancé avec PID %d : %s\n", pid, scripts[i]);
        }
    }
    return 0;
}

// Gestionnaire de signal SIGCHLD pour éviter les processus zombies
void handle_sigchld(int sig) {
    (void)sig;
    while (waitpid(-1, NULL, WNOHANG) > 0);
