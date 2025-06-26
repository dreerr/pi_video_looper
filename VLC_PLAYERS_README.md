# VLC Player Implementations for pi_video_looper

This document describes the VLC player implementations added to the pi_video_looper project.

## Overview

Two new VLC-based video players have been implemented:

1. **VLC Player** (`vlcplayer.py`) - Single screen VLC implementation
2. **VLC Dual Screen Player** (`vlcplayer_dualscreen.py`) - Dual screen VLC implementation

Both implementations provide alternatives to the existing omxplayer-based solutions, offering better format support and cross-platform compatibility.

## Features

### VLC Player (`vlc`)
- Supports a wide range of video formats (avi, mov, mkv, mp4, m4v, wmv, flv, webm, ogv, 3gp, ts, m2ts, mts)
- Full audio and video playback
- Looping support
- Volume control
- Pause/resume functionality
- Configurable extra arguments

### VLC Dual Screen Player (`vlc_dualscreen`)
- All features of the single screen VLC player
- Supports playing different videos on two displays simultaneously
- Independent display configuration
- Audio output configuration
- Synchronized playback control

## Installation Requirements

### VLC Media Player
Make sure VLC is installed on your system:

**On Raspberry Pi OS / Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install vlc
```

**On macOS:**
```bash
brew install vlc
```

**On other Linux distributions:**
Follow your distribution's package manager instructions to install VLC.

## Configuration

### Single Screen VLC Player

To use the VLC player, modify your `video_looper.ini` file:

```ini
[video_looper]
video_player = vlc

[vlc]
# Supported file extensions
extensions = avi, mov, mkv, mp4, m4v, wmv, flv, webm, ogv, 3gp, ts, m2ts, mts

# Extra VLC arguments
extra_args = --no-video-title-show --no-osd --intf dummy
```

### Dual Screen VLC Player

To use the dual screen VLC player:

```ini
[video_looper]
video_player = vlc_dualscreen

[vlc_dualscreen]
# Supported file extensions
extensions = avi, mov, mkv, mp4, m4v, wmv, flv, webm, ogv, 3gp, ts, m2ts, mts

# Display identifiers for the two screens
display_a = :0.0
display_b = :0.1

# Audio output method
audio_output = auto

# Extra VLC arguments
extra_args = --no-video-title-show --no-osd --intf dummy
```

## Display Configuration

### For Linux/X11 Systems

Use display identifiers in the format `:display.screen`:
- `:0.0` - First screen on first display
- `:0.1` - Second screen on first display

To check available displays:
```bash
xrandr --listmonitors
```

### For Other Systems

Display configuration may vary. Common alternatives:
- Monitor numbers: `0`, `1`, `2`, etc.
- Display names specific to your system

Check VLC documentation for your platform for specific display options.

## VLC-Specific Options

### Common Extra Arguments

```ini
# Disable video title overlay
--no-video-title-show

# Disable on-screen display
--no-osd

# Use dummy interface (no GUI)
--intf dummy

# Keep video on top
--video-on-top

# Set specific video output module
--vout x11

# Disable mouse cursor
--mouse-hide-timeout 0
```

### Audio Configuration

```ini
# Force specific audio output
--aout pulse    # PulseAudio
--aout alsa     # ALSA
--aout oss      # OSS

# Set audio device
--alsa-audio-device hw:0,0
```

### Video Configuration

```ini
# Set video output
--vout x11      # X11 output
--vout fb       # Framebuffer
--vout drm      # Direct Rendering Manager

# Aspect ratio
--aspect-ratio 16:9

# Deinterlacing
--deinterlace-mode linear
```

## Testing

### Test Scripts

Two test scripts are provided:

1. **test_vlc_dualscreen.py** - Tests the dual screen implementation
```bash
python3 test_vlc_dualscreen.py
```

### Manual Testing

1. Ensure VLC is installed:
```bash
which cvlc
```

2. Test basic VLC functionality:
```bash
cvlc --intf dummy --quiet /path/to/test/video.mp4
```

3. Test dual screen (if you have multiple displays):
```bash
DISPLAY=:0.0 cvlc --intf dummy --quiet /path/to/video1.mp4 &
DISPLAY=:0.1 cvlc --intf dummy --quiet /path/to/video2.mp4 &
```

## Troubleshooting

### VLC Not Found
**Error:** `[Errno 2] No such file or directory: 'cvlc'`
**Solution:** Install VLC or ensure `cvlc` is in your PATH.

### Display Issues
**Problem:** Videos not appearing on expected displays
**Solutions:**
1. Check available displays with `xrandr`
2. Verify display identifiers in configuration
3. Test with basic VLC commands manually

### Audio Issues
**Problem:** No audio or audio on wrong output
**Solutions:**
1. Set `audio_output` to specific driver (pulse, alsa, etc.)
2. Add audio-specific extra_args
3. Check system audio configuration

### Performance Issues
**Problem:** Stuttering or poor performance
**Solutions:**
1. Add hardware acceleration arguments:
   ```ini
   extra_args = --no-video-title-show --no-osd --intf dummy --avcodec-hw any
   ```
2. Adjust buffer sizes:
   ```ini
   extra_args = --no-video-title-show --no-osd --intf dummy --file-caching 1000
   ```

## Comparison with OMXPlayer

| Feature | OMXPlayer | VLC Player |
|---------|-----------|------------|
| Platform Support | Raspberry Pi only | Cross-platform |
| Format Support | Limited | Extensive |
| Hardware Acceleration | Excellent on RPi | Good, configurable |
| Startup Time | Fast | Moderate |
| Loop Seamlessness | Very good | Good |
| Configuration Options | Limited | Extensive |
| Remote Control | Basic stdin | Advanced (with HTTP interface) |

## Advanced Features

### Future Enhancements

The current implementation provides basic functionality. Potential improvements include:

1. **HTTP Remote Control** - Using VLC's HTTP interface for better control
2. **Subtitle Support** - Adding subtitle file support
3. **Streaming Support** - Network stream playback
4. **Advanced Display Management** - Better multi-monitor support

### HTTP Interface Implementation

For advanced control, VLC's HTTP interface can be enabled:

```python
# In future versions, this could enable remote control:
args.extend(['--intf', 'http', '--http-password', 'vlcremote'])
```

This would allow pause, stop, volume control, and other operations via HTTP requests.

## Files Added

- `Adafruit_Video_Looper/vlcplayer.py` - Single screen VLC player
- `Adafruit_Video_Looper/vlcplayer_dualscreen.py` - Dual screen VLC player
- `test_vlc_dualscreen.py` - Test script for dual screen functionality
- Updated `assets/video_looper.ini` - Configuration sections for VLC players

## Contributing

When contributing to the VLC player implementations:

1. Follow the existing code style and patterns
2. Test on multiple platforms if possible
3. Update this documentation for new features
4. Ensure compatibility with the existing video_looper interface

## License

These VLC player implementations follow the same license as the original pi_video_looper project (GNU GPLv2).
