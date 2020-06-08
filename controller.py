from collections import defaultdict
from utils import *
import struct


class ControllerLayer:

    def __init__(self, arduino):
        self.__coord_angles = defaultdict(lambda: defaultdict(list))
        self.create_coord_dict()
        self.__arduino = arduino


    def create_coord_dict(self, coord_loc=COORD_DICT_LOC):
        """
        Parameters:
            coord_loc: Location of .txt file which contains the angles for all 64 chessboard squares

        Description:
            Reads angles from the file at coord_loc and create a dictionary. The dictionary can be
            accessed in this way: dic['e']['4'] to retrieve the angles.

        """
        alphabet = 'a'
        step = 0
        index = '8'

        with open(coord_loc) as squares:
            for line in squares:
                angles = [int(x.strip()) for x in [x.strip() for x in line.split('=')][1].split(",")]
                self.__coord_angles[alphabet][index] = angles
                if step == 7:
                    alphabet = 'a'
                    index = chr(ord(index) - 1)
                    step = 0
                else:
                    step += 1
                    alphabet = chr(ord(alphabet) + 1)


    def get_move_angles(self, move):
        """
        Parameters:
            move: Chess move e.g. e2e4

        Description:
            Returns the angles for the two squares in the move e.g Square e2 and e4.

        """
        if VERBOSE:
            print("Processing move: ", move)
        if LOGGER:
            log("Processing move: " + move)

        from_angles = self.__coord_angles[move[0]][move[1]]
        to_angles = self.__coord_angles[move[2]][move[3]]
        angles = from_angles + to_angles
        return angles


    def get_angles(self, squareArg):
        """
        Parameters:
            squareArg: A chessboard square "e2"

        Description:
            Returns the angles for the given square.

        """
        return self.__coord_angles[squareArg[0]][squareArg[1]]


    def get_all_angles(self):
        return self.__coord_angles


    def send_to_arduino(self, move):
        """
        Parameters:
            move: [ "e2e4", 0/1/2/3, "h1f1" ]. Refer to Board.self_move_details for details of meaning of the numbers.

        Description:
            If move[1] == 0 or 1, it means a piece capture or piece movement has taken place. For these, the
            robot needs to maneuver to only two squares to complete the full move so the 4 angles retrieved
            from get_move_angles() are enough. For castling, two additional sets of angles are required. Since
            castling occurs in a specific way, this function calculates the other set of angles. Overall,
            8 angles are sent whenever communicating with the Arduino. For piece capture and movement, the
            4 extra angles are padded.

        """
        angles = self.get_move_angles(move[0])

        if move[1] == 0 or move[1] == 1:
            angles = angles + [0, 0, 0, 0]  # Padding in case of piece movement/capture

        else:
            rook_position = move[2]
            angles = angles + self.get_move_angles(rook_position)

        for i in range(0, 8):
            if angles[i] < 0:
                angles[i] = abs(angles[i]) + 200

        if VERBOSE:
            print("Angles sent to Arduino: ", angles)
        if LOGGER:
            log("Angles sent to Arduino: " + str(angles))

        self.__arduino.write(struct.pack('>BBBBBBBBB', int(move[1]), int(angles[0]), int(angles[1]), int(angles[2]),
                                         int(angles[3]), int(angles[4]), int(angles[5]), int(angles[6]),
                                         int(angles[7])))

        return str(ord(self.__arduino.read().decode('ascii')))
