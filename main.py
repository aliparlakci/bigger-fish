from trace_collector import TraceCollector
from video_player import VideoPlayer

import threading
import pickle
import argparse
import sys

parser = argparse.ArgumentParser(description='Automate the collection of video player based CPU traces.')
parser.add_argument("--trace_len", type=int, default=1, help="The trace length for the recordings in seconds.")
parser.add_argument("--num_runs", type=int, default=5, help="The number of runs for each video file.")
parser.add_argument("--out_dir", type=str, default="", help="The output location.")
parser.add_argument("--var", choices=["codec", "player"], default="player", help="The variable that will be changed. \
        Choosing the codec will record traces for each codec and vice versa.")
opts = parser.parse_args()

NUM_OF_RUNS = opts.num_runs
TRACE_LENGTH = opts.trace_len
OUT_DIR = opts.out_dir

traces = []


def run(file_path, trace_length):
    with TraceCollector(trace_length=trace_length) as collector:
        player = VideoPlayer()

        player_thread = threading.Thread(target=lambda: player.play(file_path, trace_length))
        player_thread.start()

        trace = collector.collect_traces()
        traces.append([trace, file_path])
        player_thread.join()


def main():
    if opts.control == "player":
        for player in VideoPlayer.players:
            file = "sample.mp4"
            for _ in range(NUM_OF_RUNS):
                run(file, TRACE_LENGTH)
    elif opts.control == "codec":
        for file_path in VIDEO_FILES:
            for player in SupportedPlayers:
                for i in range(NUM_OF_RUNS):
                    run(file_path, TRACE_LENGTH)

    with open(OUT_DIR, "wb") as f:
        pickle.dump(traces, f)


if __name__ == "__main__":
    main()
