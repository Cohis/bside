# B-Side para Windows

Esta pasta contém a adaptação Windows anterior. O `run-windows.cmd` encaminha para a versão atualizada extraída de `bside-main.zip`, que implementa MIDI com WinMM. `../jogo/` e `../jogo-isometrico/` permanecem como estavam.

## Como compilar

O projeto original usa Assembly x86-64 e a ABI System V do Linux. Esta variante mantém o Assembly e faz a conversão para a ABI do Windows em `win32_bridge.c`.

Requisitos no Windows x64:

- MSYS2 com GCC MinGW-w64 x86-64 e GNU Make;
- Raylib para Windows x64, incluindo `raylib.h`, `rlgl.h` e a biblioteca de link;
- OpenGL, GDI e WinMM do Windows (fornecidos pelo SDK/toolchain).

No terminal **MSYS2 UCRT64**, instale os pacotes de compilação e Raylib:

```sh
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-make mingw-w64-ucrt-x86_64-raylib
```

Abra o terminal **UCRT64** do MSYS2, entre nesta pasta e rode:

```sh
mingw32-make -f Makefile.windows
./bside.exe
```

Para iniciar a versão atualizada, abra `run-windows.cmd` no Explorador de Arquivos; ele encaminha para `../bside-main-zip/bside-main/jogo-isometrico-windows/run-windows.cmd`, que recompila se necessário e ativa o diagnóstico MIDI. A compilação manual abaixo ainda compila esta adaptação anterior.

Se a Raylib estiver fora dos caminhos padrão do MinGW, indique os diretórios:

```sh
make -f Makefile.windows RAYLIB_CFLAGS='-IC:/caminho/raylib/include' RAYLIB_LIBS='-LC:/caminho/raylib/lib -lraylib -lopengl32 -lgdi32 -lwinmm'
```

Esta adaptação anterior aceita as notas 1–4 e não tem entrada MIDI. Para usar o teclado MIDI, inicie pelo launcher, que abre a adaptação atualizada com WinMM.

Os assets são carregados por caminhos relativos, então execute `bside.exe` com esta pasta como diretório atual.
