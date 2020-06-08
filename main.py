import serial
from utils import *
from controller import ControllerLayer
from perception import PerceptionLayer
from application import ApplicationLayer
from keras.models import load_model
import config
import sys
import cv2

if __name__ == "__main__":

    # Initialize Perception Layer
    model = load_model(MODEL_LOC)
    perceptLayer = PerceptionLayer(model)

    # Initialize Controller layer
    arduino = serial.Serial(ARDUINO_PORT, 9600)
    controlLayer = ControllerLayer(arduino)
    
    # Initialize camera
    cam = cv2.VideoCapture(0)
    
    # Generate initial board array
    ret, initial_board_img = cam.read()
    show_img(initial_board_img)
    starting_arr = perceptLayer.generate_board_arr(initial_board_img)
    print("Initial Board Array\n", starting_arr)
    
    # Initialize Application Layer
    chess_board = ApplicationLayer(ROBOT_SIDE, starting_arr)
    chess_board.display()
    
    try:
        while True:
            ret, image = cam.read()
            cv2.imshow("Board Image", image)
            key = cv2.waitKey(1)
    
            if key % 256 == 27:  # Escape
                break
    
            elif key % 56 == 32:  # Space-bar
                if chess_board.is_robots_turn():
                    chess_board.move()
                    move = chess_board.get_move_details()
                    controlLayer.send_to_arduino(move)
    
                else:
                    board_arr = perceptLayer.generate_board_arr(image) 
                    chess_board.move(board_arr) 

                chess_board.display()
    
    except Exception as e:
        print(e)
        arduino.close()
    
    cam.release()
    cv2.destroyAllWindows()
    arduino.close()
