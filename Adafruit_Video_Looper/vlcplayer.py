import subprocess
import os
import signal
import time

class VLCPlayer:

    def __init__(self, config):
        """Create an instance of a video player that runs VLC in the
        background."""
        self._process = None
        self._load_config(config)

    def _load_config(self, config):
        self._extensions = config.get('vlc', 'extensions').translate(str.maketrans('', '', ' \t\r\n.')).split(',')
        self._extra_args = config.get('vlc', 'extra_args').split()

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie, loop=None, vol=0):
        """Play the provided movie file, optionally looping it repeatedly."""
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        # Assemble list of arguments.
        args = ['cvlc', '--quiet', '--fullscreen']
        args.extend(self._extra_args)  # Add extra arguments from config.
        if vol != 0:
            args.extend(['--volume', str(vol)])
        if loop is None:
            loop = movie.repeats
        if loop <= -1:
            args.append('--repeat')  # Add loop parameter if necessary.
        args.append(movie.target)  # Add movie file path.
        # Run VLC process and direct standard output to /dev/null.
        self._process = subprocess.Popen(args, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))

    def pause(self):
        if self.is_playing():
            self._process.send_signal(signal.SIGSTOP)

    def resume(self):
        if self.is_playing():
            self._process.send_signal(signal.SIGCONT)
    
    def sendKey(self, key: str):
        # VLC doesn't support direct key sending via stdin like omxplayer
        # This is a placeholder for future VLC remote control implementation
        print(f"VLC key sending not implemented: {key}")

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        if self._process is None:
            return False
        self._process.poll()
        return self._process.returncode is None

    def stop(self, block_timeout_sec=0):
        """Stop the video player.  block_timeout_sec is how many seconds to
        block waiting for the player to stop before moving on.
        """
        # Stop the player if it's running.
        if self._process is not None and self._process.returncode is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=block_timeout_sec)
            except subprocess.TimeoutExpired:
                self._process.kill()
        # If a blocking timeout was specified, wait up to that amount of time
        # for the process to stop.
        start = time.time()
        while self._process is not None and self._process.returncode is None:
            if (time.time() - start) >= block_timeout_sec:
                break
            time.sleep(0.1)
        # Let the process be garbage collected.
        self._process = None

    @staticmethod
    def can_loop_count():
        return True

def create_player(config, **kwargs):
    """Create new video player based on VLC."""
    return VLCPlayer(config)

