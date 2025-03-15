#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Error out if anything fails.
set -e

# Extra steps for DietPi installations
if id "pi" >/dev/null 2>&1; then
	echo "pi user exists"
else
    echo "Creating pi user"
	sudo useradd -m -u 1000 -G adm,audio,video,sudo,adm pi
	sudo mkdir -p /run/user/1000
	sudo chmod 700 /run/user/1000
fi

# old version cleanup
sudo supervisorctl stop video_looper &>/dev/null
sudo rm /etc/supervisor/conf.d/video_looper.conf &>/dev/null

echo "Installing dependencies..."
echo "=========================="
sudo apt update && sudo apt -y install python3 python3-pip omxplayer ntfs-3g exfat-fuse libsdl2-ttf-2.0-0 libsdl2-image-2.0-0

# pygame1 dependencies:
sudo apt -y install git python3-dev python3-setuptools python3-numpy python3-opengl \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
    libsdl1.2-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    libtiff5-dev libx11-6 libx11-dev fluid-soundfont-gm timgm6mb-soundfont \
    xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic fontconfig fonts-freefont-ttf libfreetype6-dev


if [ "$*" != "no_hello_video" ]
then
	echo "Installing hello_video..."
	echo "========================="
	cd $SCRIPT_DIR
	sudo apt -y install git build-essential python3-dev
	git clone https://github.com/adafruit/pi_hello_video
	cd pi_hello_video
	./rebuild.sh
	cd hello_video
	sudo make install
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

sudo -u pi /usr/bin/python3 -m pip install --user --upgrade pip
sudo -u pi /usr/bin/python3 -m pip install --user $SCRIPT_DIR

sudo cp $SCRIPT_DIR/assets/video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="

sudo cp $SCRIPT_DIR/assets/video_looper.service /etc/systemd/system/video_looper.service
sudo chmod 644 /etc/systemd/system/video_looper.service

sudo systemctl daemon-reload
sudo systemctl enable video_looper
sudo systemctl start video_looper
sleep 1
sudo systemctl status video_looper

echo "Finished!"
