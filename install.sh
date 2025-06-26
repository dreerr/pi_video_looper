#!/bin/sh

# Error out if anything fails.
set -e

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --vlc              Install VLC media player"
    echo "  --omxplayer        Install omxplayer (32-bit ARM only)"
    echo "  --both             Install both VLC and omxplayer (if compatible)"
    echo "  no_hello_video     Skip hello_video installation"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "If no media player option is specified, omxplayer will be installed by default on compatible systems."
}

# Check system architecture
check_architecture() {
    ARCH=$(uname -m)
    case $ARCH in
        armv6l|armv7l)
            echo "Detected 32-bit ARM architecture: $ARCH"
            return 0  # Compatible with omxplayer
            ;;
        aarch64|arm64)
            echo "Detected 64-bit ARM architecture: $ARCH"
            return 1  # Not compatible with omxplayer
            ;;
        x86_64)
            echo "Detected 64-bit x86 architecture: $ARCH"
            return 1  # Not compatible with omxplayer
            ;;
        *)
            echo "Detected architecture: $ARCH"
            return 1  # Assume not compatible with omxplayer
            ;;
    esac
}

# Parse command line arguments
INSTALL_VLC=false
INSTALL_OMXPLAYER=false
SKIP_HELLO_VIDEO=false

for arg in "$@"; do
    case $arg in
        --vlc)
            INSTALL_VLC=true
            ;;
        --omxplayer)
            INSTALL_OMXPLAYER=true
            ;;
        --both)
            INSTALL_VLC=true
            INSTALL_OMXPLAYER=true
            ;;
        no_hello_video)
            SKIP_HELLO_VIDEO=true
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            show_usage
            exit 1
            ;;
    esac
done

# Check architecture compatibility for omxplayer
if [ "$INSTALL_OMXPLAYER" = "true" ]; then
    if ! check_architecture; then
        echo "WARNING: omxplayer is not compatible with 64-bit systems."
        echo "omxplayer installation will be skipped."
        INSTALL_OMXPLAYER=false

        # If only omxplayer was requested, suggest VLC instead
        if [ "$INSTALL_VLC" = "false" ]; then
            echo "Suggestion: Use --vlc option to install VLC media player instead."
            echo "Would you like to install VLC instead? (y/n)"
            read -r response
            if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
                INSTALL_VLC=true
            fi
        fi
    fi
fi

# If no media player options specified, use default behavior
if [ "$INSTALL_VLC" = "false" ] && [ "$INSTALL_OMXPLAYER" = "false" ]; then
    if check_architecture; then
        echo "No media player specified. Installing omxplayer (default for 32-bit ARM)."
        INSTALL_OMXPLAYER=true
    else
        echo "No media player specified. Installing VLC (default for 64-bit systems)."
        INSTALL_VLC=true
    fi
fi

echo "Installing dependencies..."
echo "=========================="

# Build package list
PACKAGES="python3 python3-pip python3-pygame python3-setuptools supervisor ntfs-3g exfat-fuse"

if [ "$INSTALL_VLC" = "true" ]; then
    echo "Adding VLC to installation list..."
    PACKAGES="$PACKAGES vlc"
fi

if [ "$INSTALL_OMXPLAYER" = "true" ]; then
    echo "Adding omxplayer to installation list..."
    PACKAGES="$PACKAGES omxplayer"
fi

echo "Installing packages: $PACKAGES"
apt update && apt -y install $PACKAGES

if [ "$SKIP_HELLO_VIDEO" = "false" ]; then
	echo "Installing hello_video..."
	echo "========================="
	apt -y install git build-essential python3-dev
	git clone https://github.com/adafruit/pi_hello_video
	cd pi_hello_video
	./rebuild.sh
	cd hello_video
	make install
	cd ../..
	rm -rf pi_hello_video
else
    echo "hello_video was not installed"
    echo "=========================="
fi

echo "Installing video_looper program..."
echo "=================================="

# change the directoy to the script location
cd "$(dirname "$0")"

mkdir -p /mnt/usbdrive0 # This is very important if you put your system in readonly after
mkdir -p /home/pi/video # create default video directory
chown pi:pi /home/pi/video

python3 setup.py install --force

cp ./assets/video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="

cp ./assets/video_looper.conf /etc/supervisor/conf.d/

service supervisor restart

echo "Finished!"
