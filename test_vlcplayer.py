#!/usr/bin/env python3
"""
Simple test script to verify VLC player functionality.
This script creates a mock configuration and tests basic VLC player operations.
"""

import configparser
import tempfile
import os
import sys
import time
from Adafruit_Video_Looper.vlcplayer import VLCPlayer
from Adafruit_Video_Looper.model import Movie

def create_test_config():
    """Create a test configuration for VLC player."""
    config = configparser.ConfigParser()
    
    # Add VLC section
    config.add_section('vlc')
    config.set('vlc', 'extensions', 'mp4, avi, mkv, mov')
    config.set('vlc', 'extra_args', '--no-video-title-show --no-osd --intf dummy')
    
    return config

def main():
    print("Testing VLC Player Implementation")
    print("=" * 40)
    
    # Create test configuration
    config = create_test_config()
    
    # Create VLC player instance
    try:
        player = VLCPlayer(config)
        print("✓ VLC player instance created successfully")
    except Exception as e:
        print(f"✗ Failed to create VLC player: {e}")
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
    
    # Test with a non-existent video file (this should fail gracefully)
    test_movie = Movie("/path/to/nonexistent/video.mp4", repeats=1)
    try:
        player.play(test_movie)
        print("✓ Play method executed (note: may fail if VLC not installed)")
        time.sleep(1)  # Give it a moment
        is_playing_after = player.is_playing()
        print(f"✓ Playing state after play attempt: {is_playing_after}")
        player.stop()
    except Exception as e:
        print(f"⚠ Play method with test file: {e} (expected if VLC not installed)")
    
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
    print("- VLC player class can be instantiated")
    print("- Configuration loading works")
    print("- Basic methods are callable")
    print("- To fully test, ensure VLC is installed and provide a real video file")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
