# Autonomous Game-Playing Robot

```
<p align="center">
  <img width="120" height="120" src="https://imgur.com/a/YyhA0CP">
</p>
```

------

## Dependencies:

- Keras
- Matplotlib
- opencvpython==3.4.5.20
- pythonchess
- tensorFlow

------

### Demo:

[https://www.linkedin.com/posts/quest-software-quality-engineering-%26-testing-laboratory_at-quest-we-strive-for-innovation-and-are-activity-6636241653235585024-Ei7-]()

------

## Installation:

1. Install Python 3.7. Do not install the latest 3.8 version as it is not compatible with TensorFlow. 
1. Install the Arduino application.
1. Install DRV8825.h libray from Sketch -> Include Libraries -> Manage Libraries
1. Select Arduino Nano from Tools -> Board
1. Select ATmega328P (Old Bootloader) from Tools -> Processor
1. Connect the Arduino to the laptop/Pi.
1. Upload the automatic.ino file from the repository to the Arduino.
1. Install Stockfish.
1. Create a new conda environment using requirements.txt from the repository.
1. Open core.ipynb and configure the constants, specifically providing paths for the Stockfish engine, the CNN model and Squares.txt.
1. Install IPWebcam application on an Android phone and start it. Copy the associated IP to the constants in core.ipynb
1. Look up the port in Arduino and copy it to the constants aswell. 
1. Place the phone on the stand, making sure the whole chessboard is visible.
1. Make sure all the chess pieces are in their correct places.
1. Run all the cells in core.ipynb, except for the one that saves images.

------

### Inspired by:

[Raspberry Turk]: https://github.com/joeymeyer/raspberryturk	"Raspeberry Turk by Joey Meyer"

