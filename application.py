import chess
import chess.engine
import chess.svg
from utils import *
import sys
import numpy as np


class ApplicationLayer:

    # -------------PUBLIC FUNCTIONS----------------#

    def __init__(self, side, initial_board_arr, resume=False):
        """
        Parameters:
            side:               Specifies the side the robot will play on. True means White and vice versa.

            initial_board_arr:  The initial board configuration where no piece has been moved. Required to learn
                                the board orientation and orient board arrays accordingly later on.

            resume:             Specifies that board should be initialized using position saved in
                                saves/latest position.txt

        Description:
            Initialises the chess.Board which is used to track the board. Learns the board orientation and
            loads the chess engine.

        """
        if resume:
            self.__load_prev_game()
        else:
            self.__load_new_game(initial_board_arr, side)

        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(CHESS_ENGINE_PATH)
        except FileNotFoundError:
            sys.stderr.write("Chess Engine could not be loaded.\n")
            sys.exit(0)

    def display(self):
        """
        Description:
            Prints the chess.Board in SVG format i.e graphically.

        """
        try:
            board = chess.svg.board(board=self.__board, flipped=not self.__side, size=300, lastmove=self.__board.peek())
        except IndexError:
            board = chess.svg.board(board=self.__board, flipped=not self.__side, size=300)

        return board

    def move(self, a_board_arr=None):
        if self.__board.is_game_over():
            sys.stderr.write("Game Over")
            sys.exit(0)
        else:
            self.__do_move(a_board_arr)

    def is_robots_turn(self):
        return self.__turn

    def get_move_details(self):
        """
        Description:
            Returns the details of the move to be made by the robot. The details include:

            a) String representation of the move e.g. e2e4
            b) A flag, which can be 0, 1, 2 or 3.
                0 -> Piece movement
                1 -> Piece capture
                2 -> King-side castling
                3 -> Queen-side castling

        """
        return self.current_engine_move

    # -------------PRIVATE FUNCTIONS----------------#

    def __adjust_move_for_side(self, move):
        if VERBOSE:
            print("Initial move:", move)
        if LOGGER:
            log("Initial move:" + move)

        if self.__side == chess.BLACK:
            if VERBOSE:
                print("Side black, move flipped.")
            if LOGGER:
                log("Side black, move flipped.")
            return chr(8 + ord('a') - ord(move[0]) + 96) + str(8 - int(move[1]) + 1) + chr(
                8 + ord('a') - ord(move[2]) + 96) + str(8 - int(move[3]) + 1)
        else:
            if VERBOSE:
                print("Side white, move used as it is.")
            if LOGGER:
                log("Side white, move used as it is.")
            return move

    def __set_move_details(self, move):
        """
        Description:
            Sets the details of the move to be made by the robot. The details include:

            a) String representation of the move e.g. e2e4
            b) A flag, which can be 0, 1, 2 or 3.
                0 -> Piece movement
                1 -> Piece capture
                2 -> King-side castling
                3 -> Queen-side castling
            c) String representation of the position of the rook, if a castling move has been done, empty otherwise.

           These details are used by the Arduino to send the angles for the corresponding chessboard squares.

        """
        flag = 0
        move = str(move)
        rook_position = ""
        flipped_move_castling = ""

        if self.__board.is_capture(chess.Move.from_uci(str(move))):
            flag = 1

        elif self.__board.is_kingside_castling(chess.Move.from_uci(str(move))):
            flag = 2
            if VERBOSE:
                print("King side Castling detected")
            if LOGGER:
                log("King side Castling detected")
            rook_position = 'h' + move[1] + 'f' + move[1]

        elif self.__board.is_queenside_castling(chess.Move.from_uci(str(move))):
            flag = 3
            if VERBOSE:
                print("Queen side Castling detected")
            if LOGGER:
                log("Queen side Castling detected")
            rook_position = 'a' + move[1] + 'd' + move[1]

        flipped_move = self.__adjust_move_for_side(move)

        if flag == 2 or flag == 3:
            flipped_move_castling = self.__adjust_move_for_side(rook_position)
            if VERBOSE:
                print("Move rook:", flipped_move_castling)
            if LOGGER:
                log("Move rook:" + flipped_move_castling)

        if VERBOSE:
            print("Flipped Move:", flipped_move)
        if LOGGER:
            log("Flipped Move:" + flipped_move)

        self.current_engine_move = [
            str(flipped_move),
            flag,
            str(flipped_move_castling)
        ]
        if VERBOSE:
            print("Engine Move details: ", self.current_engine_move)
        if LOGGER:
            log("Engine Move details: " + str(self.current_engine_move))

    def __do_move(self, a_board_arr=None):
        """
        Description:
            Performs a move. If it is the robot's turn, then the move is provided by the
            engine, otherwise it is determined from the passed board_arr. The move is
            pushed onto the board and the board_arr and turn are updated.

        """
        if self.__turn:  # Robot's turn
            next_move = self.__get_engine_move()
            self.__set_move_details(next_move)
            self.__board.push(next_move)
            self.__update_board_arr()
            self.__turn = False
            if VERBOSE:
                print("Engine move: ", next_move)
            if LOGGER:
                log("Engine move: " + next_move)
        else:
            next_move = self.__get_player_move(a_board_arr)

            if next_move is None:
                return

            self.__board.push(next_move)
            self.__board_arr = self.__orient_board(a_board_arr)
            self.__turn = True

        self.__save_game_state()

    def __get_board_orientation(self, a_board_arr):
        """
        Parameters:
            a_board_arr: 8x8 numpy array corresponding to an initial chessboard setup.

        Description:
            Calculates which side the White pieces are on the given board array.

        Returns:
            The board orientation with respect to the White pieces.
            WT = White top | WB = White bottom | WL = White left | WR = White right

        """
        first_row_sum = int(np.sum(a_board_arr[0]))
        first_col_sum = int(np.sum(a_board_arr[:, 0]))

        if first_row_sum == 8:
            return "WT"
        elif first_row_sum == 0:
            return "WB"
        elif first_col_sum == 8:
            return "WL"
        elif first_col_sum == 0:
            return "WR"
        else:
            sys.stderr.write("Invalid Board Array")

    def __orient_board(self, a_board_arr):
        """
        Parameters:
            a_board_arr: 8x8 numpy array corresponding to a chessboard configuration

        Description:
            Orients the given board array according to the board's set orientation so that
            the White pieces are always at the bottom. This is to conform to the board
            configuration in chess.Board which uses a similar layout.

        Returns:
            The oriented array.

        """
        if self.__board_orientation is None:
            sys.stderr.write("Board array cannot be oriented as no orientation has been set.")

        if self.__board_orientation == "WT":
            return np.flip(a_board_arr)

        elif self.__board_orientation == "WR":
            return np.rot90(a_board_arr, 3)

        elif self.__board_orientation == "WL":
            return np.rot90(a_board_arr, 1)
        # If already WB then no need to orient.
        else:
            return a_board_arr

    def __get_square(self, coord):
        """
        Parameters:
            coord: A list containing a row and col index which represents a position in
                   8x8 numpy array e.g [2, 3]

        Description:
            Calculates which square (0 to 63) on the board is represented by the given indexes.

        """
        return (8 * coord[0]) + coord[1]

    def __get_moveset_length(self, tuple_list):
        """
        Parameters:
            tuple_list: A list containing two arrays like so: (arr[0, 2], arr[0, 3]). These correspond
                        to the indexes in the board_array where the np.where function located a provided
                        search value. The first array contains the row and the second array contains the
                        column indexes. This means that the board indexes where some given values were
                        found are (0, 0) and (2, 3).

        Description:
            Calculates the number of squares represented by the tuple list

        """
        return len(tuple_list[0])

    def __update_board_arr(self):
        """
        Description:
            When the chess engine updates self.__board after making a move, the update
            needs to be reflected in the board_array as well. This function reads the
            updated self.__board and recreates a new board array which is used to overwrite
            the previous board array.

        """
        new_arr = np.zeros((8, 8))

        for i in range(0, 8):
            for j in range(0, 8):
                # color_at returns 1 for White, 0 for Black and None for Empty
                color = self.__board.color_at(self.__get_square([i, j]))

                if color is None:
                    color = -1

                new_arr[7 - i][j] = color

        self.__board_arr = new_arr

        if VERBOSE:
            print("\nUpdated arr: \n", self.__board_arr)
        if LOGGER:
            log("\nUpdated arr: \n" + self.__board_arr)

    def __get_engine_move(self):
        """
        Description:
            Returns the move the chess engine recommends on the current board state.

        """
        result = self.engine.play(self.__board, chess.engine.Limit(depth=DIFFICULTY))
        return result.move

    def __get_move_details(self, new_board_arr):
        """
        Parameters:
            new_board_arr: Oriented board array corresponding to the board array
                           after the player has made a move.

        Description:
            By subtracting new_board_arr from our current board_arr, we can find
            the exact squares that have witnessed any movement. The movement will
            be in the form of 1's and 2's on the sub(tracked) board. However, we
            need to identify which piece has moved from where to where.

        Returns:
            movement: A list containing 2 array's, one containing the row indexes and
                      one containing the column indexes which corresponds to the squares
                      on the board_array where pieces have moved.

            side: Which side made the move, W or B.

            white_capture(bool): Specifies if White has captured a piece.

        """
        sub = abs(self.__board_arr - new_board_arr)
        if VERBOSE:
            print(sub)
        if LOGGER:
            log(sub)

        movement = None
        side = None
        white_capture = False
        possible_white_move = np.where(sub == 2)
        possible_black_move = np.where(sub == 1)
        if VERBOSE:
            print("White:", possible_white_move, "\nBlack:", possible_black_move)
        if LOGGER:
            log("White:" + possible_white_move + "\nBlack:" + possible_black_move)

        # When there are only 2's on the board, it means White has moved a piece.
        # This is because when an empty square has a White piece placed on it,
        # the difference is -1-(1) = 2.
        if (self.__get_moveset_length(possible_white_move) != 0 and
                self.__get_moveset_length(possible_black_move) == 0):
            movement = possible_white_move
            side = "W"

        # When there are only 1's on the board, it means Black has either moved
        # a piece or captured a piece. The capture is so because whenever
        # an opposite color piece is occupied, the difference in boards
        # will show it as 1. Since when a Black piece moves, the difference is
        # also 1, multiple 1's means either capture or movement.
        elif (self.__get_moveset_length(possible_black_move) != 0 and
              self.__get_moveset_length(possible_white_move) == 0):
            movement = possible_black_move
            side = "B"

        # If there are 1's and 2's on the subtracted board, it can only mean
        # that White has captured a piece. This is because a White piece
        # movement results in a 2, and when a White piece occupies a former
        # Black piece, the difference is 0-(1)=1. Hence, we are certain it
        # is a White capture.
        elif (self.__get_moveset_length(possible_black_move) != 0 and
              self.__get_moveset_length(possible_white_move) != 0):
            side = "W"
            white_capture = True
            movement = ((np.append(possible_black_move[0], possible_white_move[0])),
                        (np.append(possible_black_move[1], possible_white_move[1])))

            if VERBOSE:
                print("White capture result")
            if LOGGER:
                log("White capture result")

        return movement, side, white_capture

    def __get_capture_or_movement(self, squares, pieces, white_capture):
        """
        Parameters:
            squares: The squares (0-63) where piece movements have occured.
            pieces: The pieces on the given squares.

        Description:
            Since there are only 2 squares, we can use their colors to determine
            if a capture or movement has occured. For a capture, the colors
            will be different and for a movement, they will be similar.

        Returns:
            The detected move.

        """
        color_square_1 = self.__board.color_at(squares[0])
        color_square_2 = self.__board.color_at(squares[1])
        if VERBOSE:
            print("Colors: ", color_square_1, color_square_2)
        if LOGGER:
            log("Colors: " + str(color_square_1) + str(color_square_2))

        if white_capture:
            if VERBOSE:
                print("White capture")
            if LOGGER:
                log("White capture")

            if color_square_1 == chess.WHITE and color_square_2 == chess.BLACK:
                move_from = squares[0]
                move_to = squares[1]
            elif color_square_1 == chess.BLACK and color_square_2 == chess.WHITE:
                move_from = squares[1]
                move_to = squares[0]

        # Black capture
        elif (color_square_1 != color_square_2) and (color_square_1 is not None) and (color_square_2 is not None):
            if VERBOSE:
                print("Black capture")
            if LOGGER:
                log("Black capture")
            if color_square_1 == chess.WHITE and color_square_2 == chess.BLACK:
                move_from = squares[1]
                move_to = squares[0]
            elif color_square_1 == chess.BLACK and color_square_2 == chess.WHITE:
                move_from = squares[0]
                move_to = squares[1]

        # Movement
        else:
            if VERBOSE:
                print("Piece movement")
            if LOGGER:
                log("Piece movement")
            move_to = squares[(np.where(np.array(pieces) == None)[0][0])]
            move_from = squares[(np.where(np.array(pieces) != None)[0][0])]

        if VERBOSE:
            print("From ", move_from, " to ", move_to)
        if LOGGER:
            log("From " + move_from + " to " + move_to)
        return chess.Move(move_from, move_to)

    def __get_castling_move(self, squares, pieces, side):
        """
        Parameters:
            squares: The squares (0-63) where piece movements have occurred.
            pieces: The pieces on the given squares.
            side: The side which made the move

        Description:
            Since board is always checked in row-order, a Queen-side and King-side
            castle can be detected by the order of King and Rook placement.

        Returns:
            The corresponding castling move.

        """
        # Queen-side castling
        if (self.__board.piece_type_at(squares[0]) == chess.ROOK and
                pieces[1] is None and
                pieces[2] is None and
                self.__board.piece_type_at(squares[3]) == chess.KING):
            if VERBOSE:
                print("Queen-side castling requirements met")
            if LOGGER:
                log("Queen-side castling requirements met")

            if ((side == "W" and bool(self.__board.castling_rights & chess.BB_A1)) or
                    (side == "B" and bool(self.__board.castling_rights & chess.BB_A8))):
                if VERBOSE:
                    print("Queen-side castling completed")
                if LOGGER:
                    log("Queen-side castling completed")
                return self.__board.parse_san('O-O-O')

        # King-side castling
        elif (self.__board.piece_type_at(squares[0]) == chess.KING and
              pieces[1] is None and
              pieces[2] is None and
              self.__board.piece_type_at(squares[3]) == chess.ROOK):

            """
            Castling all cases.
            King side castling and queen side castling.
            """
            if VERBOSE:
                print("King-side castling requirements met")
            if LOGGER:
                log("King-side castling requirements met")

            if ((side == "W" and bool(self.__board.castling_rights & chess.BB_H1)) or
                    (side == "B" and bool(self.__board.castling_rights & chess.BB_H8))):
                if VERBOSE:
                    print("King-side castling completed")
                if LOGGER:
                    log("King-side castling completed")
                return self.__board.parse_san('O-O')

        else:
            sys.stderr.write("Invalid castling move")

    def __save_game_state(self):
        """
        Description:
            Saves the current state of the game by saving the FEN representing the current
            board position, the current turn and board orientation.
        """
        file = open("saves/last position.txt", "w+")
        file.write(self.__board.fen() + "\n")
        file.write(str(self.__turn) + "\n")
        file.write(self.__board_orientation)
        file.close()

    def __load_new_game(self, initial_board_arr, side):
        """
        Description:
            Freshly initialises game variables.

        """
        self.__board = chess.Board()
        self.__board_orientation = self.__get_board_orientation(initial_board_arr)
        if VERBOSE:
            print("Orientation learned: ", self.__board_orientation)
        if LOGGER:
            log("Orientation learned: " + self.__board_orientation)
        self.__board_arr = self.__orient_board(initial_board_arr)
        self.__turn = side
        self.__side = side

    def __load_prev_game(self):

        """
        Description:
            Sets game variables to those saved in the last position.txt. This is done to
            recover the the current game state in case of a Python or Jupyter notebook crash.

        """
        file = open("saves/last position.txt", "r")
        data = file.readlines()

        if data[1][:-1] == "False":
            self.__turn = False
        else:
            self.__turn = True

        self.__board = chess.Board(fen=data[0][:-1])
        self.__board_orientation = data[2]
        self.__update_board_arr()

        file.close()

    def __get_player_move(self, new_board_arr):
        """
        Parameters:
            new_board_arr: New board array from the new board position

        Description:
            Checks the given board array and determines what kind of move
            has been made by the human player on the board

        Returns:
            Returns the detected move

        """
        if VERBOSE:
            print("\nPerforming Move\n")
        if LOGGER:
            log("\nPerforming Move\n")
        oriented_board = self.__orient_board(new_board_arr)

        if VERBOSE:
            print("Old Board Array\n", self.__board_arr)
            print("New Board Array\n", oriented_board)
        if LOGGER:
            log("Old Board Array\n" + self.__board_arr)
            log("New Board Array\n" + oriented_board)

        if np.array_equal(self.__board_arr, oriented_board):
            print("No move detected")
            log("No move detected")
            return None

        movement, side, white_capture = self.__get_move_details(oriented_board)
        moveset_len = self.__get_moveset_length(movement)

        # 2 corresponds to piece movement or capture
        # 4 corresponds to castling
        if moveset_len not in [2, 4]:
            sys.stderr.write("Invalid number of pieces have been moved.")
            return None
        move = None
        squares = []
        pieces = []
        for i in range(moveset_len):
            movement[0][i] = 7 - movement[0][i]
            squares.append(self.__get_square((movement[0][i], movement[1][i])))
            pieces.append(self.__board.piece_at(squares[i]))

        # Castling
        if moveset_len == 4:
            move = self.__get_castling_move(squares, pieces, side)
        # Movement or capture
        elif moveset_len == 2:
            move = self.__get_capture_or_movement(squares, pieces, white_capture)

        if not self.__board.is_legal(move):
            sys.stderr.write("Invalid move detected")
        else:
            return move
