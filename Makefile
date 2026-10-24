CC := gcc
CFLAGS := -c -x assembler-with-cpp
LDFLAGS := -no-pie
RAYLIB := vendor/raylib/libraylib.a
LIBS := -lGL -lm -lpthread -ldl -lrt -lX11

.PHONY: all run clean
all: bside

bside: bside.o $(RAYLIB)
	$(CC) $(LDFLAGS) bside.o $(RAYLIB) $(LIBS) -o $@

bside.o: bside.s
	$(CC) $(CFLAGS) $< -o $@

run: bside
	./bside

clean:
	$(RM) bside.o bside
