import cv2
import numpy as np
import keras
from keras.applications.xception import preprocess_input
from utils import *
from misc import utils
from misc.utils import ImageObject
from misc.slid import pSLID, SLID, slid_tendency
from misc.laps import LAPS
from misc.llr import LLR, llr_pad

keras.backend.set_learning_phase(0)
load = cv2.imread
save = cv2.imwrite


class PerceptionLayer:

    def __init__(self, model):
        """
        model: CNN model that detects whether a chessboard square has a black piece, white piece or is empty.
        """
        self.model = model


    def generate_board(self, board):
        """
        Parameters:
            board: A cropped overhead image of a chessboard.

        Description:
            Takes the chessboard image "board" and cuts into 64 squares. Each square is then passed
            to the CNN model and its output is used to construct a 8x8 array that represents the chessboard
            in "board" picture.

        """
        side_len = int(board.shape[0] / 8)
        dim = (WIDTH, HEIGHT)
        board_arr = np.zeros((8, 8))

        for i in range(8):
            for j in range(8):
                tile = board[i * side_len: (i + 1) * side_len, j * side_len: (j + 1) * side_len]
                tile = cv2.resize(tile, dim)
                tile = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                tile = adjust_gamma(tile)
                tile = np.expand_dims(np.array(tile), axis=0)
                tile = preprocess_input(tile)

                pred = get_pred(self.model.predict(tile)[0], LABELS)

                if pred == "empty":
                    board_arr[i, j] = -1
                elif pred == "w":
                    board_arr[i, j] = 1

        return board_arr


    def generate_board_arr(self, frame):
        """
        Parameters:
            frame: Overhead image of a chessboard.

        Description:
            Returns a 8x8 array that represents the chessboard image passed as "frame". First,
            the detect function crops "frame" and extracts only the chessboard from the picture,
            removing everything else. The generate board function then takes the cropped image
            and returns its corresponding array.

        """
        warped = self.detect(frame)
        return self.generate_board(warped)


    def layer(self):
        global NC_LAYER, NC_IMAGE

        segments = pSLID(NC_IMAGE['main'])
        raw_lines = SLID(NC_IMAGE['main'], segments)
        lines = slid_tendency(raw_lines)
        points = LAPS(NC_IMAGE['main'], lines)
        inner_points = LLR(NC_IMAGE['main'], points, lines)
        four_points = llr_pad(inner_points, NC_IMAGE['main'])

        try:
            NC_IMAGE.crop(four_points)
            save(str(NC_LAYER) + ".png", NC_IMAGE['orig'])

        except:
            utils.warn("Next layer is not needed")
            NC_IMAGE.crop(inner_points)

        print("\n")


    def detect(self, image):
        global NC_LAYER, NC_IMAGE, NC_CONFIG

        NC_IMAGE, NC_LAYER = ImageObject(image), 0
        for _ in range(NC_CONFIG['layers']):
            NC_LAYER += 1
            self.layer()

        show_img(NC_IMAGE['orig'])
        return NC_IMAGE['orig']
