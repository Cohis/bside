/*
 * Ponte de ABI para a cópia Windows do B-Side.
 *
 * O Assembly original usa System V AMD64. O MinGW e a Raylib para Windows
 * usam a ABI x64 da Microsoft. Estes wrappers recebem os argumentos System V
 * e deixam o compilador fazer a chamada Windows, inclusive structs por valor.
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <raylib.h>
#include <rlgl.h>

#if !defined(__x86_64__) || !defined(__GNUC__)
#error "Compile com MinGW-w64 GCC x86-64, que oferece sysv_abi."
#endif
#define SYSV __attribute__((sysv_abi))

/* O ponto de entrada do Assembly mantém a ABI original; main do CRT é Windows. */
extern int bside_main_sysv(void) SYSV;
int main(void) { return bside_main_sysv(); }

/* Janela, entrada e tempo. */
SYSV void sysv_InitWindow(int width, int height, const char *title) { InitWindow(width, height, title); }
SYSV void sysv_CloseWindow(void) { CloseWindow(); }
SYSV bool sysv_IsWindowReady(void) { return IsWindowReady(); }
SYSV bool sysv_WindowShouldClose(void) { return WindowShouldClose(); }
SYSV void sysv_SetTargetFPS(int fps) { SetTargetFPS(fps); }
SYSV float sysv_GetFrameTime(void) { return GetFrameTime(); }
SYSV double sysv_GetTime(void) { return GetTime(); }
SYSV bool sysv_IsKeyDown(int key) { return IsKeyDown(key); }
SYSV bool sysv_IsKeyPressed(int key) { return IsKeyPressed(key); }
SYSV void sysv_ToggleBorderlessWindowed(void) { ToggleBorderlessWindowed(); }
SYSV int sysv_GetScreenWidth(void) { return GetScreenWidth(); }
SYSV int sysv_GetScreenHeight(void) { return GetScreenHeight(); }

/* Desenho e recursos: o retorno por valor é convertido entre as duas ABIs. */
SYSV Texture2D sysv_LoadTexture(const char *path) { return LoadTexture(path); }
SYSV void sysv_UnloadTexture(Texture2D texture) { UnloadTexture(texture); }
SYSV bool sysv_FileExists(const char *path) { return FileExists(path); }
SYSV void sysv_GenTextureMipmaps(Texture2D *texture) { GenTextureMipmaps(texture); }
SYSV void sysv_SetTextureFilter(Texture2D texture, int filter) { SetTextureFilter(texture, filter); }
SYSV RenderTexture2D sysv_LoadRenderTexture(int width, int height) { return LoadRenderTexture(width, height); }
SYSV void sysv_UnloadRenderTexture(RenderTexture2D target) { UnloadRenderTexture(target); }
SYSV void sysv_BeginTextureMode(RenderTexture2D target) { BeginTextureMode(target); }
SYSV void sysv_EndTextureMode(void) { EndTextureMode(); }
SYSV void sysv_BeginDrawing(void) { BeginDrawing(); }
SYSV void sysv_EndDrawing(void) { EndDrawing(); }
SYSV void sysv_ClearBackground(Color color) { ClearBackground(color); }
SYSV void sysv_DrawTexturePro(Texture2D texture, Rectangle source, Rectangle dest, Vector2 origin, float rotation, Color tint) {
    DrawTexturePro(texture, source, dest, origin, rotation, tint);
}
SYSV void sysv_DrawRectangle(int x, int y, int width, int height, Color color) { DrawRectangle(x, y, width, height, color); }
SYSV void sysv_DrawRectangleLines(int x, int y, int width, int height, Color color) { DrawRectangleLines(x, y, width, height, color); }
SYSV void sysv_DrawLine(int x1, int y1, int x2, int y2, Color color) { DrawLine(x1, y1, x2, y2, color); }
SYSV void sysv_DrawText(const char *text, int x, int y, int size, Color color) { DrawText(text, x, y, size, color); }
SYSV int sysv_MeasureText(const char *text, int size) { return MeasureText(text, size); }
SYSV void sysv_TakeScreenshot(const char *path) { TakeScreenshot(path); }
SYSV void sysv_BeginBlendMode(int mode) { BeginBlendMode(mode); }
SYSV void sysv_EndBlendMode(void) { EndBlendMode(); }
SYSV void sysv_rlDrawRenderBatchActive(void) { rlDrawRenderBatchActive(); }
SYSV void sysv_rlPushMatrix(void) { rlPushMatrix(); }
SYSV void sysv_rlPopMatrix(void) { rlPopMatrix(); }
SYSV void sysv_rlTranslatef(float x, float y, float z) { rlTranslatef(x, y, z); }
SYSV void sysv_rlScalef(float x, float y, float z) { rlScalef(x, y, z); }

/* Áudio. A Raylib Windows expõe os mesmos tipos públicos da versão Linux. */
SYSV void sysv_InitAudioDevice(void) { InitAudioDevice(); }
SYSV void sysv_CloseAudioDevice(void) { CloseAudioDevice(); }
SYSV bool sysv_IsAudioDeviceReady(void) { return IsAudioDeviceReady(); }
SYSV Music sysv_LoadMusicStream(const char *path) { return LoadMusicStream(path); }
SYSV void sysv_UnloadMusicStream(Music music) { UnloadMusicStream(music); }
SYSV void sysv_PlayMusicStream(Music music) { PlayMusicStream(music); }
SYSV void sysv_UpdateMusicStream(Music music) { UpdateMusicStream(music); }
SYSV void sysv_SetMusicVolume(Music music, float volume) { SetMusicVolume(music, volume); }
SYSV Sound sysv_LoadSound(const char *path) { return LoadSound(path); }
SYSV void sysv_UnloadSound(Sound sound) { UnloadSound(sound); }
SYSV void sysv_PlaySound(Sound sound) { PlaySound(sound); }
SYSV void sysv_SetSoundVolume(Sound sound, float volume) { SetSoundVolume(sound, volume); }

/* CRT e matemática. */
SYSV char *sysv_getenv(const char *name) { return getenv(name); }
SYSV int sysv_puts(const char *text) { return puts(text); }
SYSV int sysv_sscanf(const char *text, const char *format, ...) {
    int result;
    va_list args;
    va_start(args, format);
    result = vsscanf(text, format, args);
    va_end(args);
    return result;
}
SYSV int sysv_strcmp(const char *left, const char *right) { return strcmp(left, right); }
SYSV float sysv_sinf(float value) { return sinf(value); }
SYSV float sysv_cosf(float value) { return cosf(value); }

/* A versão Windows aceita as notas pelas teclas 1-4; MIDI continua opcional. */
SYSV int sysv_open(const char *path, int flags, ...) { (void)path; (void)flags; return -1; }
SYSV long long sysv_read(int fd, void *buffer, unsigned long long size) {
    (void)fd; (void)buffer; (void)size; return -1;
}
SYSV int sysv_close(int fd) { (void)fd; return 0; }
