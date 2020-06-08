import datetime
import chess
currentDT = datetime.datetime.now()

HEIGHT = 64
WIDTH = 64
IMAGE_DIMS = (500, 500)
LABELS = ("b", "empty", "w")
CLASSES = len(LABELS)
MODEL_LOC = 'model/new_board_v3.model'
CHESS_ENGINE_PATH = "stockfish/Windows/stockfish_10_x64.exe"
COORD_DICT_LOC = "Squares.txt"
ARDUINO_PORT = 'COM7'
LOGGING_FILE = "logs/" + currentDT.strftime("%a, %b %d, %Y - %I;%M;%S %p") + ".txt"
VERBOSE = True
LOGGER = True
ROBOT_SIDE = chess.WHITE
DIFFICULTY = 5

with open(LOGGING_FILE, 'a', encoding="utf-8") as File:
    File.write("Logger of " + str(LOGGING_FILE))
