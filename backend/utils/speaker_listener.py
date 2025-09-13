#!/usr/bin/env python3
"""
Speaker Listener
----------------
Ce script lit une FIFO (pipe nommé) et prononce à voix haute les messages reçus.

⚙️ Requirements système :
    sudo apt-get install espeak libttspico-utils alsa-utils

⚠️ Fonctionnement prévu :
    - Django (ou un autre programme) écrit une ligne dans /tmp/speak.fifo
      Exemple : engine=espeak voice=fr+f3 speed=140 pitch=70 Guillaume a envoyé "Salut !" à Léonce
    - Le script lit la ligne
    - Il choisit le moteur (espeak ou pico2wave) et prononce le message

💡 Bonnes pratiques :
    - Ce script doit être lancé en service (systemd) pour tourner en continu
    - La FIFO /tmp/speak.fifo est créée automatiquement si elle n’existe pas
"""

import subprocess
import shlex
import tempfile
import os


# -----------------------------
# Fonctions de synthèse vocale
# -----------------------------


def speak_espeak(message, voice="fr+f3", speed="140", pitch=None):
    """
    Utilise espeak pour prononcer un message.
    :param message: texte à dire
    :param voice: voix (ex. fr+f3, en+m1)
    :param speed: vitesse (par défaut 140)
    :param pitch: hauteur (facultatif, ex. 50-80)
    """
    cmd = ["espeak", f"-v{voice}", f"-s{speed}"]
    if pitch:
        cmd.append(f"-p{pitch}")
    cmd.append(message)
    subprocess.run(cmd)


def speak_pico(message, voice="fr-FR"):
    """
    Utilise pico2wave pour prononcer un message.
    Génère un fichier WAV temporaire et le joue avec aplay.
    :param message: texte à dire
    :param voice: voix (fr-FR, en-US, de-DE, etc.)
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_path = f.name
    try:
        # génération fichier wav
        subprocess.run(
            ["pico2wave", f"-l={voice}", "-w", wav_path, message], check=True
        )
        # lecture avec aplay
        subprocess.run(["aplay", wav_path], check=True)
    finally:
        # nettoyage
        if os.path.exists(wav_path):
            os.remove(wav_path)


# -----------------------------
# Parsing des lignes FIFO
# -----------------------------


def parse_line(line):
    """
    Analyse une ligne reçue depuis la FIFO.
    La ligne peut contenir des paramètres (engine, voice, speed, pitch)
    suivis du texte à prononcer.

    Exemple :
        engine=espeak voice=fr+f3 speed=140 pitch=70 Guillaume a envoyé "Hello" à Léonce

    :param line: ligne brute venant de la FIFO
    :return: (params, message)
    """
    parts = shlex.split(line)  # sépare en respectant les guillemets
    params = {"engine": "espeak", "voice": "fr+f3", "speed": "140", "pitch": None}
    message_parts = []

    for p in parts:
        if "=" in p and not p.startswith(("'", '"')):
            # c'est un paramètre clé=valeur
            k, v = p.split("=", 1)
            params[k] = v
        else:
            # fait partie du texte du message
            message_parts.append(p)

    return params, " ".join(message_parts)


# -----------------------------
# Boucle principale
# -----------------------------


def main():
    fifo_path = "/tmp/speak.fifo"

    # Crée la FIFO si elle n'existe pas
    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)
        os.chmod(fifo_path, 0o666)  # accessible à tous

    # Petit message de démarrage
    speak_espeak("Bonjour bande de petit morveux, je suis prêt", voice="fr+f3")

    # Boucle infinie de lecture
    with open(fifo_path, "r") as fifo:
        for line in fifo:
            params, message = parse_line(line.strip())
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
