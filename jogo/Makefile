CC := gcc
CFLAGS := -c -x assembler-with-cpp
LDFLAGS := -no-pie
RAYLIB := vendor/raylib/libraylib.a
LIBS := -lGL -lm -lpthread -ldl -lrt -lX11
OBJETOS := bside.o fase1.o

.PHONY: all run arte clean
all: bside

bside: $(OBJETOS) $(RAYLIB)
	$(CC) $(LDFLAGS) $(OBJETOS) $(RAYLIB) $(LIBS) -o $@

%.o: %.s estruturas.inc tileset.inc
	$(CC) $(CFLAGS) $< -o $@

run: bside
	./bside

# Regera assets/tileset-bside.png, assets/luz.png, assets/vinheta.png e tileset.inc.
arte:
	python3 ferramentas/gerar_tileset.py

clean:
	$(RM) $(OBJETOS) bside
