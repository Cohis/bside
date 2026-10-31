#!/usr/bin/env python3
"""Gera os efeitos sonoros da Sala 2 em WAV mono 16 bits (44,1 kHz).

As 4 notas do jogo usam a mesma oitava; as frequências padrão (Dó, Ré, Mi, Sol)
precisam casar com a tabela notas_midi em sala2.s.

Saídas em assets/sons/:
  nota0..3.wav  timbre de piano elétrico
  tique.wav     metrônomo
  berro.wav     alto-falante atraindo os anjos
  grito.wav     grito do anjo (erro)
  estatica.wav  aparelhos chiando quando o disco sai da caixa
  clarao.wav    teleporte do agente
  grito-anjo.wav  anjos levantando voo; vem de assets/sons/originais/grito-anjo.mp3
                (áudio baixado pelo usuário), convertido com ffmpeg: mono, 44,1 kHz,
                sem o silêncio do fim e com 0,15 s de fade
  baque.wav     a caixa do pedido caindo da estante do depósito
  zumbido.wav   névoa (loop)

Uso: python3 ferramentas/gerar_sons.py   (ou `make arte`)
"""
import math
import shutil
import subprocess
import random
import struct
import wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TAXA = 44100
NOTAS_HZ = [261.63, 293.66, 329.63, 392.00]     # C4 D4 E4 G4


def salvar(nome, amostras):
    pico = max(1e-9, max(abs(a) for a in amostras))
    escala = 0.85 / pico if pico > 0.85 else 1.0
    pasta = RAIZ / "assets" / "sons"
    pasta.mkdir(parents=True, exist_ok=True)
    with wave.open(str(pasta / nome), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(b"".join(struct.pack("<h", int(a * escala * 32767)) for a in amostras))


def nota(hz, dur=0.9):
    n = int(TAXA * dur)
    s = []
    for i in range(n):
        t = i / TAXA
        env = min(1.0, t / 0.004) * math.exp(-t * 4.0)
        v = (math.sin(2 * math.pi * hz * t)
             + 0.35 * math.sin(2 * math.pi * hz * 2 * t) * math.exp(-t * 7)
             + 0.12 * math.sin(2 * math.pi * hz * 3 * t + 0.5) * math.exp(-t * 10))
        s.append(0.5 * env * v)
    return s


def tique():
    rng = random.Random(1)
    n = int(TAXA * 0.05)
    return [0.6 * math.exp(-i / 180) * (math.sin(2 * math.pi * 1800 * i / TAXA) + 0.3 * rng.uniform(-1, 1))
            for i in range(n)]


def berro():
    """Corneta saturada: a nota grave da doca passando por um alto-falante velho."""
    n = int(TAXA * 0.8)
    s = []
    for i in range(n):
        t = i / TAXA
        hz = 180 + 40 * math.sin(2 * math.pi * 6 * t)
        v = math.sin(2 * math.pi * hz * t) + 0.6 * math.sin(2 * math.pi * hz * 1.5 * t)
        v = math.tanh(3.5 * v)
        env = min(1.0, t / 0.02) * (1 - t / 0.8) ** 0.5
        s.append(0.5 * env * v)
    return s


def grito():
    rng = random.Random(7)
    n = int(TAXA * 1.1)
    s = []
    fase = 0.0
    for i in range(n):
        t = i / TAXA
        hz = 900 + 1400 * t + 120 * math.sin(2 * math.pi * 23 * t)
        fase += 2 * math.pi * hz / TAXA
        v = math.sin(fase) + 0.5 * math.sin(fase * 1.51) + 0.4 * rng.uniform(-1, 1)
        env = min(1.0, t / 0.05) * max(0.0, 1 - t / 1.1)
        s.append(0.45 * env * math.tanh(2 * v))
    return s


def estatica():
    rng = random.Random(3)
    n = int(TAXA * 1.6)
    s = []
    ant = 0.0
    for i in range(n):
        t = i / TAXA
        r = rng.uniform(-1, 1)
        ant = 0.6 * ant + 0.4 * r
        corte = 1.0 if math.sin(2 * math.pi * 7 * t) > -0.3 else 0.2
        env = min(1.0, t / 0.03) * max(0.0, 1 - t / 1.6)
        s.append(0.5 * env * corte * ant + 0.1 * env * math.sin(2 * math.pi * 60 * t))
    return s


def clarao():
    n = int(TAXA * 0.45)
    s = []
    fase = 0.0
    for i in range(n):
        t = i / TAXA
        hz = 200 * (1 + 12 * t)
        fase += 2 * math.pi * hz / TAXA
        env = min(1.0, t / 0.01) * math.exp(-t * 6)
        s.append(0.5 * env * (math.sin(fase) + 0.5 * math.sin(fase * 2.01)))
    return s


def baque():
    """Caixa de papelão batendo no chão: pancada grave e um chiado curto de papelão."""
    rng = random.Random(11)
    n = int(TAXA * 0.35)
    s = []
    ant = 0.0
    for i in range(n):
        t = i / TAXA
        ant = 0.7 * ant + 0.3 * rng.uniform(-1, 1)
        corpo = math.sin(2 * math.pi * (95 - 60 * t) * t) * math.exp(-t * 18)
        papelao = ant * math.exp(-t * 40)
        s.append(0.7 * min(1.0, t / 0.002) * (corpo + 0.8 * papelao))
    return s


def zumbido():
    """Laço de 4 s sem emenda audível: só frequências com número inteiro de ciclos."""
    dur = 4.0
    n = int(TAXA * dur)
    s = []
    for i in range(n):
        t = i / TAXA
        v = (math.sin(2 * math.pi * 55 * t) + 0.5 * math.sin(2 * math.pi * 82.5 * t)
             + 0.3 * math.sin(2 * math.pi * 110.25 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.5 * t)))
        s.append(0.25 * v)
    return s


def grito_anjo():
    origem = RAIZ / "assets" / "sons" / "originais" / "grito-anjo.mp3"
    if not origem.exists() or not shutil.which("ffmpeg"):
        print("grito-anjo.wav: sem o mp3 original ou sem ffmpeg; mantido como está")
        return
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(origem),
                    "-af", "atrim=0:3.95,afade=t=out:st=3.8:d=0.15",
                    "-ac", "1", "-ar", str(TAXA), "-sample_fmt", "s16",
                    str(RAIZ / "assets" / "sons" / "grito-anjo.wav")], check=True)


def main():
    for k, hz in enumerate(NOTAS_HZ):
        salvar(f"nota{k}.wav", nota(hz))
    salvar("tique.wav", tique())
    salvar("berro.wav", berro())
    salvar("grito.wav", grito())
    salvar("estatica.wav", estatica())
    salvar("clarao.wav", clarao())
    salvar("baque.wav", baque())
    grito_anjo()
    salvar("zumbido.wav", zumbido())
    print("assets/sons: 12 efeitos")


if __name__ == "__main__":
    main()
