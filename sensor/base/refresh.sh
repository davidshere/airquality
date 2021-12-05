#!/bin/bash

# exit on error
set -e

arduino-cli compile --fqbn=arduino:avr:uno

arduino-cli upload --fqbn=arduino:avr:uno --port=/dev/ttyACM0

minicom --device=/dev/ttyACM0 -b 9600
