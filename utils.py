from chess import RANK_NAMES
from chess import square
import cv2
import numpy as np
from config import *


def log(data):
    with open(LOGGING_FILE, 'a', encoding="utf-8") as File:
        File.write("\n" + data)


def adjust_gamma(image, gamma=1.5):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)


def get_pred(preds, labels):
    index_of_max = np.argmax(preds)
    return labels[index_of_max]


def show_img(img):
    img = cv2.resize(img, (700, 700))
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def write_board(board, invert_color: bool = False, borders: bool = False) -> str:
    """
    Returns a string representation of the board with Unicode pieces.
    Useful for pretty-printing to a terminal.

    :param board: Board that needs to be written
    :param invert_color: Invert color of the Unicode pieces.
    :param borders: Show borders and a coordinate margin.
    """
    builder = []
    for rank_index in range(7, -1, -1):
        if borders:
            builder.append("  ")
            builder.append("-" * 17)
            builder.append("\n")

            builder.append(RANK_NAMES[rank_index])
            builder.append(" ")

        for file_index in range(8):
            square_index = square(file_index, rank_index)

            if borders:
                builder.append("|")
            elif file_index > 0:
                builder.append(" ")

            piece = board.piece_at(square_index)

            if piece:
                builder.append(piece.unicode_symbol(invert_color=invert_color))
            else:
                builder.append("⭘")

        if borders:
            builder.append("|")

        if borders or rank_index > 0:
            builder.append("\n")

    if borders:
        builder.append("  ")
        builder.append("-" * 17)
        builder.append("\n")
        builder.append("   a b c d e f g h")

    return "".join(builder)
