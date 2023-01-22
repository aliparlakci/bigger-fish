import subprocess
import time

from enum import Enum


class SupportedPlayers(Enum):
    MPV = 1
    MPLAYER = 2
    VLC = 3

    def map(self, name: str):
        if name.lower() == "mpv":
            return self.MPV
        if name.lower() == "mplayer":
            return self.MPLAYER
        if name.lower() == "vlc":
            return self.VLC


class VideoPlayer:
    players = None
    player = None

    def __init__(self, players=SupportedPlayers, player=SupportedPlayers.VLC):
        self.players = players
        self.player = player.name

    def play(self, file_path, length):
        player_name = self.player.lower()
        player_process = subprocess.Popen([player_name, file_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        time.sleep(length)
        player_process.kill()
