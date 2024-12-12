#ifndef UTILS_H
#define UTILS_H

#include <sys/types.h>

extern pid_t *child_pids;
extern int num_scripts;

int launch_python_scripts(int num_scripts, const char **scripts);
void handle_sigchld(int sig);  // Pour éviter les processus zombies

#endif // UTILS_H
