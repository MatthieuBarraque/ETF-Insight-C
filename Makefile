CC = gcc

CFLAGS = -I./include \
         -Wall -Wextra -Werror -pedantic -std=c11 \
         -O2 -g -fstack-protector-strong -D_FORTIFY_SOURCE=2 \
         -D_POSIX_C_SOURCE=200809L \
         -I/usr/local/include/cjson

LDFLAGS = -lm -lcjson

SRC_DIR = src
OBJ_DIR = build/obj
BIN_DIR = build/bin

EXECUTABLE = etf_analyzer

SOURCES = $(shell find $(SRC_DIR) -type f -name '*.c')

OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(SOURCES))

.PHONY: all clean fclean re

all: $(BIN_DIR)/$(EXECUTABLE)

$(BIN_DIR)/$(EXECUTABLE): $(OBJECTS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -rf $(OBJ_DIR)

fclean: clean
	rm -rf $(BIN_DIR)/$(EXECUTABLE)

re: fclean all
