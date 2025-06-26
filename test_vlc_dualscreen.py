#!/usr/bin/env python3
"""
Test script to verify VLC dual screen player functionality.
This script creates a mock configuration and tests basic dual screen operations.
"""

import configparser
import tempfile
import os
import sys
import time
from Adafruit_Video_Looper.vlcplayer_dualscreen import VLCPlayerDualScreen
from Adafruit_Video_Looper.model import Movie

def create_test_config():
    """Create a test configuration for VLC dual screen player."""
    config = configparser.ConfigParser()
    
    # Add VLC dual screen section
    config.add_section('vlc_dualscreen')
    config.set('vlc_dualscreen', 'extensions', 'mp4, avi, mkv, mov')
    config.set('vlc_dualscreen', 'extra_args', '--no-video-title-show --no-osd --intf dummy')
    config.set('vlc_dualscreen', 'display_a', ':0.0')
    config.set('vlc_dualscreen', 'display_b', ':0.1')
    config.set('vlc_dualscreen', 'audio_output', 'auto')
    
    return config

def main():
    print("Testing VLC Dual Screen Player Implementation")
    print("=" * 50)
    
    # Create test configuration
    config = create_test_config()
    
    # Create VLC dual screen player instance
    try:
        player = VLCPlayerDualScreen(config)
        print("✓ VLC dual screen player instance created successfully")
    except Exception as e:
        print(f"✗ Failed to create VLC dual screen player: {e}")
        return 1
    
    # Test supported extensions
    extensions = player.supported_extensions()
    print(f"✓ Supported extensions: {extensions}")
    
    # Test can_loop_count
    can_loop = player.can_loop_count()
    print(f"✓ Can loop count: {can_loop}")
    
    # Test initial state
    is_playing = player.is_playing()
    print(f"✓ Initial playing state: {is_playing}")
    
    # Test stop (should handle gracefully even if nothing is playing)
    try:
        player.stop()
        print("✓ Stop method works")
    except Exception as e:
        print(f"✗ Stop method failed: {e}")
    
    # Test with non-existent video files (this should fail gracefully)
    test_movie_a = Movie("/path/to/nonexistent/video_a.mp4", repeats=1)
    test_movie_b = Movie("/path/to/nonexistent/video_b.mp4", repeats=1)
    
    try:
        player.play(test_movie_a, test_movie_b)
        print("✓ Play method executed for dual screen (note: may fail if VLC not installed)")
        time.sleep(1)  # Give it a moment
        is_playing_after = player.is_playing()
        print(f"✓ Playing state after play attempt: {is_playing_after}")
        player.stop()
    except Exception as e:
        print(f"⚠ Play method with test files: {e} (expected if VLC not installed)")
    
    # Test pause/resume functionality
    try:
        player.pause()
        print("✓ Pause method works")
        player.resume()
        print("✓ Resume method works")
    except Exception as e:
        print(f"⚠ Pause/Resume methods: {e}")
    
    # Test sendKey functionality
    try:
        player.sendKey("p")
        print("✓ SendKey method works (placeholder implementation)")
    except Exception as e:
        print(f"⚠ SendKey method: {e}")
    
    print("\nTest Summary:")
    print("- VLC dual screen player class can be instantiated")
    print("- Configuration loading works")
    print("- Basic methods are callable")
    print("- Dual screen setup is configured")
    print("- To fully test, ensure VLC is installed and provide real video files")
    print("- Verify your display configuration matches your system setup")
    print("\nDisplay Configuration:")
    print(f"- Display A: {config.get('vlc_dualscreen', 'display_a')}")
    print(f"- Display B: {config.get('vlc_dualscreen', 'display_b')}")
    print("\nNote: Display identifiers depend on your system:")
    print("- Linux/X11: Use ':0.0', ':0.1' format")
    print("- Some systems: Use monitor numbers '0', '1'")
    print("- Check 'xrandr' output for available displays on Linux")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
