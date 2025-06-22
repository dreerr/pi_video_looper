# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import shutil
import subprocess
import tempfile
import time

from .alsa_config import parse_hw_device


class OMXPlayerDualScreen:

    def __init__(self, config):
        """Create an instance of a video player that runs two omxplayer instances in the
        background for dual screen support.
        """
        self._process_a = None
        self._process_b = None
        self._temp_directory = None
        self._load_config(config)

    def __del__(self):
        if self._temp_directory:
            shutil.rmtree(self._temp_directory)

    def _get_temp_directory(self):
        if not self._temp_directory:
            self._temp_directory = tempfile.mkdtemp()
        return self._temp_directory

    def _load_config(self, config):
        self._extensions = (
            config.get("omxplayer_dualscreen", "extensions")
            .translate(str.maketrans("", "", " \t\r\n."))
            .split(",")
        )
        self._extra_args = config.get("omxplayer_dualscreen", "extra_args").split()
        self._sound = config.get("omxplayer_dualscreen", "sound").lower()
        assert self._sound in (
            "hdmi",
            "local",
            "both",
            "alsa",
        ), "Unknown omxplayer sound configuration value: {0} Expected hdmi, local, both or alsa.".format(
            self._sound
        )
        self._alsa_hw_device = parse_hw_device(config.get("alsa", "hw_device"))
        if self._alsa_hw_device != None and self._sound == "alsa":
            self._sound = "alsa:hw:{},{}".format(
                self._alsa_hw_device[0], self._alsa_hw_device[1]
            )
        self._show_titles = config.getboolean("omxplayer_dualscreen", "show_titles")
        self._display_a = config.get("omxplayer_dualscreen", "display_a")
        self._display_b = config.get("omxplayer_dualscreen", "display_b")
        if self._show_titles:
            title_duration = config.getint("omxplayer_dualscreen", "title_duration")
            if title_duration >= 0:
                m, s = divmod(title_duration, 60)
                h, m = divmod(m, 60)
                self._subtitle_header = (
                    "00:00:00,00 --> {:d}:{:02d}:{:02d},00\n".format(h, m, s)
                )
            else:
                self._subtitle_header = "00:00:00,00 --> 99:59:59,00\n"

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie_a, movie_b, loop_a=None, loop_b=None, vol=0):
        """Play the provided movie files on two screens."""
        self.stop(3)  # Up to 3 second delay to let the old players stop.

        self._process_a = self._play_movie(movie_a, self._display_a, loop_a, vol)
        self._process_b = self._play_movie(movie_b, self._display_b, loop_b, vol)

    def _play_movie(self, movie, display, loop, vol):
        if movie is None:
            return None
        args = ["omxplayer"]
        args.extend(["--display", display])
        args.extend(["-o", self._sound])
        args.extend(self._extra_args)
        if vol != 0:
            args.extend(["--vol", str(vol)])
        if loop is None:
            loop = movie.repeats
        if loop <= -1:
            args.append("--loop")
        if self._show_titles and movie.title:
            srt_path = os.path.join(
                self._get_temp_directory(),
                (
                    "video_looper_a.srt"
                    if display == self._display_a
                    else "video_looper_b.srt"
                ),
            )
            with open(srt_path, "w") as f:
                f.write(self._subtitle_header)
                f.write(movie.title)
            args.extend(["--subtitles", srt_path])
        args.append(movie.target)
        return subprocess.Popen(
            args, stdout=open(os.devnull, "wb"), stdin=subprocess.PIPE, close_fds=True
        )

    def is_playing(self):
        """Return true if any video player is running, false otherwise."""
        # To simplify, we'll just check one of the players.
        # A more robust solution would check both.
        if self._process_a is None and self._process_b is None:
            return False

        if self._process_a:
            self._process_a.poll()
            if self._process_a.returncode is None:
                return True

        if self._process_b:
            self._process_b.poll()
            if self._process_b.returncode is None:
                return True

        return False

    def stop(self, block_timeout_sec=0):
        """Stop both video players."""
        # Stop the players if they're running.
        if (self._process_a is not None and self._process_a.returncode is None) or (
            self._process_b is not None and self._process_b.returncode is None
        ):
            subprocess.call(["pkill", "-9", "omxplayer"])

        start = time.time()
        while (self._process_a is not None and self._process_a.returncode is None) or (
            self._process_b is not None and self._process_b.returncode is None
        ):
            if (time.time() - start) >= block_timeout_sec:
                break
            time.sleep(0)
            if self._process_a:
                self._process_a.poll()
            if self._process_b:
                self._process_b.poll()

        self._process_a = None
        self._process_b = None

    @staticmethod
    def can_loop_count():
        return False


def create_player(config, **kwargs):
    """Create new video player based on omxplayer for dual screens."""
    return OMXPlayerDualScreen(config)
