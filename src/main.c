#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>
#include "utils.h"
pid_t *child_pids = NULL;
int num_scripts = 0;

void handle_sigint(int sig)
{
    (void)sig;
    printf("\nSIGINT reçu, arrêt des processus enfants...\n");
    for (int i = 0; i < num_scripts; i++) {
        if (child_pids[i] > 0) {
            kill(child_pids[i], SIGKILL);
            printf("Processus enfant avec PID %d tué\n", child_pids[i]);
        }
    }
    free(child_pids); 
    exit(EXIT_SUCCESS);
}

int main(void)
{
    signal(SIGINT, handle_sigint);
    const char *scripts[] = {
        "scripts/data_acquisition.py",
        "scripts/data_financials.py",
        "scripts/data_technical.py"
    };
    num_scripts = sizeof(scripts) / sizeof(scripts[0]);
    if (launch_python_scripts(num_scripts, scripts) == -1)
    {
        fprintf(stderr, "Erreur lors du lancement des scripts Python.\n");
        return EXIT_FAILURE;
    }
    for (int i = 0; i < num_scripts; i++) 
    {
        waitpid(child_pids[i], NULL, 0);
    }
    free(child_pids);
    return EXIT_SUCCESS;
}
