![Build Image](https://github.com/interactionresearchstudio/NaturewatchCameraServer/workflows/Build%20Image/badge.svg)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/interactionresearchstudio/NaturewatchCameraServer)
![GitHub all releases](https://img.shields.io/github/downloads/interactionresearchstudio/NaturewatchCameraServer/total)
# NaturewatchCameraServer

This is a Python server script that captures a video stream from a Pi Camera and serves it as a .mjpg through a control website to another device. Part of the My Naturewatch project in collaboration with the RCA.

# How to install

To use the image, download the lastest zip build from [Releases](https://github.com/interactionresearchstudio/NaturewatchCameraServer/releases)

Uncompress and burn this to an SD card. We recommend using [Balena Etcher](https://www.balena.io/etcher/) for this.

## Configuring the wifi setup

Run the config setup python script. This will reboot the pi

	sudo python3 NaturewatchCameraServer/cfgsetup.py

## Access the interface

The website is then accessible through its hostname:

	http://naturewatchcamera.local/

Be sure to replace `raspberrypi.local` with whatever hostname the Pi has.

## Reporting bugs

Please provide as much information as possible. If you'd like to open an issue about a
possible bug, please do so here and include as much information as possible.

## Pull requests

If you'd like to submit a pull request, please let us know whether you're submitting a
new feature, or a bug fix. We have an internal release schedule, so please don't be
offended if it takes us some time to fit your PR in! We will respond to every single
one of them and let you know if we're evaluating it for a full release. It's also worth
testing your PR against the `dev` branch, which has more experimental features.

## Support

If you require support, please head over to the [My Naturewatch Forum](https://mynaturewatch.net/forum).

