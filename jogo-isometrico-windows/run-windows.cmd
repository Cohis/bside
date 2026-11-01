@echo off
setlocal EnableExtensions
title B-Side - versao atualizada do ZIP

rem Este launcher antigo agora direciona para a copia atualizada com suporte MIDI.
set "ZIP_LAUNCHER=%~dp0..\bside-main-zip\bside-main\jogo-isometrico-windows\run-windows.cmd"
if not exist "%ZIP_LAUNCHER%" goto erro_versao

call "%ZIP_LAUNCHER%" %*
exit /b %ERRORLEVEL%

:erro_versao
echo ERRO: nao encontrei o launcher da versao atualizada do ZIP:
echo "%ZIP_LAUNCHER%"
echo Confira se a pasta bside-main-zip continua junto desta pasta.
echo.
pause
exit /b 1
