CC := gcc
CFLAGS := -c -x assembler-with-cpp
LDFLAGS := -no-pie
RAYLIB := vendor/raylib/libraylib.a
LIBS := -lGL -lm -lpthread -ldl -lrt -lX11
OBJETOS := bside.o fase1.o sala2.o atores.o roteiro.o ritmo.o doca.o
INCLUDES := estruturas.inc tileset.inc personagens.inc cenario.inc doca_dados.inc doca_roteiro.inc

.PHONY: all run arte doca clean teste
all: bside

bside: $(OBJETOS) $(RAYLIB)
	$(CC) $(LDFLAGS) $(OBJETOS) $(RAYLIB) $(LIBS) -o $@

%.o: %.s $(INCLUDES)
	$(CC) $(CFLAGS) $< -o $@

run: bside
	./bside

# Regera o atlas do cenário, o do elenco, o agente (das bases da Eva), o anjo, a névoa e os sons
# (Python 3 + Pillow + NumPy).
arte:
	python3 ferramentas/gerar_iso.py
	python3 ferramentas/gerar_personagens.py
	python3 ferramentas/gerar_agente.py
	python3 ferramentas/gerar_anjo.py
	python3 ferramentas/montar_elenco_hd.py
	python3 ferramentas/gerar_sons.py
	python3 ferramentas/gerar_doca.py --mapas

# Refaz e verifica os trechos da fuga (plantas, alto-falantes, pontos e soluções).
doca:
	python3 ferramentas/gerar_doca.py --mapas

clean:
	$(RM) $(OBJETOS) bside bside-teste

# Jogo com o robô de teste no lugar do teclado (ferramentas/teste_auto.c).
bside-teste: $(OBJETOS) $(RAYLIB) ferramentas/teste_auto.c ferramentas/doca_solucoes.h
	$(CC) $(LDFLAGS) $(OBJETOS) ferramentas/teste_auto.c $(RAYLIB) $(LIBS) \
		-Wl,--wrap=IsKeyDown,--wrap=IsKeyPressed,--wrap=EndDrawing -o $@

teste: bside-teste
	mkdir -p teste
	BSIDE_CENA=loja BSIDE_BOT=loja ./bside-teste
	BSIDE_CENA=galpao BSIDE_BOT=galpao ./bside-teste
	BSIDE_CENA=doca BSIDE_BOT=doca ./bside-teste
