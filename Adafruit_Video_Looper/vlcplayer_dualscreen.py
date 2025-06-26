import os
import subprocess
import signal
import time


class VLCPlayerDualScreen:

    def __init__(self, config):
        """Create an instance of a video player that runs two VLC instances in the
        background for dual screen support.
        """
        self._process_a = None
        self._process_b = None
        self._load_config(config)

    def _load_config(self, config):
        self._extensions = (
            config.get("vlc_dualscreen", "extensions")
            .translate(str.maketrans("", "", " \t\r\n."))
            .split(",")
        )
        self._extra_args = config.get("vlc_dualscreen", "extra_args").split()
        self._display_a = config.get("vlc_dualscreen", "display_a")
        self._display_b = config.get("vlc_dualscreen", "display_b")
        # VLC audio output settings
        self._audio_output = config.get("vlc_dualscreen", "audio_output", fallback="auto")

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie_a, movie_b, loop_a=None, loop_b=None, vol=0):
        """Play the provided movie files on two screens."""
        self.stop(3)  # Up to 3 second delay to let the old players stop.

        self._process_a = self._play_movie(movie_a, self._display_a, loop_a, vol, "a")
        self._process_b = self._play_movie(movie_b, self._display_b, loop_b, vol, "b")

    def _play_movie(self, movie, display, loop, vol, instance_id):
        """Play a movie on a specific display."""
        if movie is None:
            return None
        
        args = ["cvlc", "--quiet", "--fullscreen"]
        
        # Set display/monitor for VLC
        # For Linux/X11 systems, we can use DISPLAY environment variable
        # For other systems, VLC might need different approaches
        if display:
            # VLC can use --qt-display-mode or --vout-display-wrapper
            args.extend(["--qt-display-mode", display])
        
        # Add audio output configuration
        if self._audio_output != "auto":
            args.extend(["--aout", self._audio_output])
        
        # Add extra arguments from config
        args.extend(self._extra_args)
        
        # Set volume if specified
        if vol != 0:
            # VLC volume range is typically 0-512, convert from typical 0-100 range
            vlc_vol = min(512, max(0, int(vol * 5.12)))
            args.extend(["--volume", str(vlc_vol)])
        
        # Handle looping
        if loop is None:
            loop = movie.repeats
        if loop <= -1:
            args.append("--repeat")  # Add loop parameter if necessary
        
        args.append(movie.target)  # Add movie file path
        
        # Create environment for this instance
        env = os.environ.copy()
        if display and display.startswith(":"):
            # For X11 display specification
            env["DISPLAY"] = display
        elif display and display.isdigit():
            # For monitor number specification on some systems
            env["VLC_DISPLAY"] = display
        
        # Run VLC process and direct standard output to /dev/null
        return subprocess.Popen(
            args,
            stdout=open(os.devnull, "wb"),
            stderr=open(os.devnull, "wb"),
            env=env,
            close_fds=True
        )

    def pause(self):
        """Pause both video players."""
        # VLC doesn't have a simple way to send commands to running instances
        # without additional setup. For basic implementation, we use signal pause
        if self._process_a and self._process_a.returncode is None:
            try:
                self._process_a.send_signal(signal.SIGSTOP)
            except ProcessLookupError:
                pass
        
        if self._process_b and self._process_b.returncode is None:
            try:
                self._process_b.send_signal(signal.SIGSTOP)
            except ProcessLookupError:
                pass

    def resume(self):
        """Resume both paused video players."""
        if self._process_a and self._process_a.returncode is None:
            try:
                self._process_a.send_signal(signal.SIGCONT)
            except ProcessLookupError:
                pass
        
        if self._process_b and self._process_b.returncode is None:
            try:
                self._process_b.send_signal(signal.SIGCONT)
            except ProcessLookupError:
                pass

    def sendKey(self, key: str):
        """Send key command to VLC instances."""
        # Basic implementation - VLC doesn't support stdin key sending like omxplayer
        # This is a placeholder for future VLC remote control implementation
        print(f"VLC dual screen key sending not implemented: {key}")

    def is_playing(self):
        """Return true if any video player is running, false otherwise."""
        # Check if either player is still running
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
        # Stop the players if they're running
        processes_to_stop = []
        
        if self._process_a is not None and self._process_a.returncode is None:
            processes_to_stop.append(self._process_a)
        
        if self._process_b is not None and self._process_b.returncode is None:
            processes_to_stop.append(self._process_b)
        
        # Terminate processes gracefully first
        for process in processes_to_stop:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
        
        # Wait for graceful termination
        start = time.time()
        while processes_to_stop and (time.time() - start) < block_timeout_sec:
            for process in processes_to_stop[:]:  # Copy list to modify during iteration
                process.poll()
                if process.returncode is not None:
                    processes_to_stop.remove(process)
            if processes_to_stop:
                time.sleep(0.1)
        
        # Force kill any remaining processes
        for process in processes_to_stop:
            try:
                process.kill()
            except ProcessLookupError:
                pass
        
        # Final wait for cleanup
        start = time.time()
        while (self._process_a is not None and self._process_a.returncode is None) or (
            self._process_b is not None and self._process_b.returncode is None
        ):
            if (time.time() - start) >= max(block_timeout_sec, 1):
                break
            time.sleep(0.1)
            if self._process_a:
                self._process_a.poll()
            if self._process_b:
                self._process_b.poll()

        # Clean up process references
        self._process_a = None
        self._process_b = None

    @staticmethod
    def can_loop_count():
        return True


def create_player(config, **kwargs):
    """Create new video player based on VLC for dual screens."""
    return VLCPlayerDualScreen(config)
