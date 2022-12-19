import subprocess
import time
import sys

from enum import Enum


class SupportedPlayers(Enum):
    WINDOWS_MEDIA_PLAYER = 1
    MPLAYER = 2
    VLC = 3


class VideoPlayer:
    players = None
    player = None

    def __init__(self, players=SupportedPlayers):
        self.players = players

    def play(self, file_path, length):
        player_name = {"linux": "vlc", "win32": "vlc.exe", "darwin": "/Applications/VLC.app/Contents/MacOS/VLC"}[
            sys.platform]
        player = subprocess.Popen([player_name, file_path])
        time.sleep(length)
        player.kill()
