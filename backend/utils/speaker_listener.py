#!/usr/bin/env python3
"""
Speaker Listener (via logs)
---------------------------
Ce script lit le fichier de logs Django en continu et prononce les messages
qui contiennent un tag spécial [TOSPEAK].

⚙️ Requirements système :
    sudo apt-get install espeak libttspico-utils alsa-utils

💡 Fonctionnement prévu :
    - Django écrit dans les logs une ligne du type :
        [TOSPEAK] engine=espeak voice=fr+f3 speed=140 pitch=70 Guillaume a envoyé "Salut !" à Léonce
    - Le script détecte ce tag, extrait les paramètres et fait la synthèse vocale.
    - Lancement recommandé en service systemd.
"""

import subprocess
import tempfile
import os
import re
import shlex

LOGFILE = "/opt/nuagefernandez/backend/logs/app.log"  # adapte au chemin de tes logs


# -----------------------------
# Fonctions de synthèse vocale
# -----------------------------


def speak_espeak(message, voice="fr+f3", speed="140", pitch=None):
    cmd = ["espeak", f"-v{voice}", f"-s{speed}", "--stdout"]
    if pitch:
        cmd.append(f"-p{pitch}")
    cmd.append(message)

    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    subprocess.run(["aplay", "-D", "sysdefault:CARD=Headphones"], stdin=p1.stdout)


def speak_pico(message, voice="fr-FR"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_path = f.name
    try:
        subprocess.run(
            ["pico2wave", f"-l={voice}", "-w", wav_path, message], check=True
        )
        subprocess.run(
            ["aplay", "-D", "sysdefault:CARD=Headphones", wav_path], check=True
        )
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


# -----------------------------
# Parsing des lignes loguées
# -----------------------------


def parse_line(line):
    """
    Extrait params + message depuis une ligne de log [TOSPEAK].
    """
    try:
        parts = shlex.split(line)
    except ValueError:
        parts = line.split()

    params = {"engine": "espeak", "voice": "fr+f3", "speed": "140", "pitch": None}
    message_parts = []

    for p in parts:
        if "=" in p and not p.startswith(("'", '"')):
            k, v = p.split("=", 1)
            params[k] = v
        else:
            message_parts.append(p)

    return params, " ".join(message_parts)


# -----------------------------
# Boucle principale
# -----------------------------


def main():
    # Message de démarrage
    speak_espeak("Speaker listener démarré et prêt", voice="fr+f3")

    # tail -F pour suivre le log en continu
    process = subprocess.Popen(
        ["tail", "-F", LOGFILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    pattern = re.compile(r"\[TOSPEAK\]\s*(.*)")

    for line in process.stdout:
        m = pattern.search(line)
        if not m:
            continue

        raw = m.group(1).strip()
        if not raw:
            continue

        params, message = parse_line(raw)
        if not message:
            continue

        engine = params.get("engine", "espeak")
        if engine == "pico2wave":
            speak_pico(message, voice=params.get("voice", "fr-FR"))
        else:
            speak_espeak(
                message,
                voice=params.get("voice", "fr+f3"),
                speed=params.get("speed", "140"),
                pitch=params.get("pitch"),
            )


if __name__ == "__main__":
    main()
