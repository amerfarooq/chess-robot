# Autonomous Game-Playing Robot

<p align="center">
  <a href="https://imgbb.com/"><img src="https://i.ibb.co/HXYhgvX/logo.png" alt="logo" border="0" width="150" height="150"></a>
</p>

## Demo:

https://www.facebook.com/questlabpk/posts/1439493929557214


## Installation:

1. Install Python 3.7. Do not install the latest 3.8 version as it is not compatible with TensorFlow. 
1. Install the Arduino application.
1. Install DRV8825.h libray from Sketch -> Include Libraries -> Manage Libraries
1. Select Arduino Nano from Tools -> Board
1. Select ATmega328P (Old Bootloader) from Tools -> Processor
1. Connect the Arduino to the laptop containing the rest of the code.
1. Upload the automatic.ino file from the repository to the Arduino.
1. Install Stockfish.
1. Create a new conda environment using the requirements.txt from the repository.
1. Configure the constants in config.py, specifically providing paths for the Stockfish engine, the CNN model and the Squares.txt file.
1. Install IPWebcam application on an Android phone and start it. Copy the associated IP to the constants in config.py
1. Look up the port in Arduino and copy it to the constants as well. 
1. Place the phone on the stand, making sure the whole chessboard is visible.
1. Make sure all the chess pieces are in their correct places.
1. Run main.py


## Inspired by:

Raspberry Turk, by Joey Meyer. His implementation can be found at http://www.raspberryturk.com/
