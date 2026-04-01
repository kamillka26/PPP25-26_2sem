from abc import ABC, abstractmethod
import copy


class Figure(ABC):
    """Класс, описывающий базовую фигуру."""
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.was_moved = False

    @abstractmethod
    def symbol(self):
        pass

    @abstractmethod
    def is_valid_move(self, board, new_position):
        pass


class Position:
    """Класс, необходимый для представления координат."""
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __str__(self):
        return f"{chr(self.col + 97)}{8 - self.row}"


class Move:
    """Класс для хранения информации о сделанном коде."""
    def __init__(self, piece, start, end, captured=None):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured = captured


class Pawn(Figure):
    """Класс, определяющий пешку"""
    def symbol(self):
        return "P" if self.color == "white" else "p"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        direction = 1 if self.color == 'white' else -1
        start_row = 1 if self.color == 'white' else 6 

        if new_col == current_col and new_row == current_row + direction:
            if board.get_piece_at(new_position) is None:
                return True

        elif current_row == start_row and new_col == current_col and new_row == current_row + 2 * direction:
            if board.get_piece_at(new_position) is None and board.get_piece_at((current_row + direction, current_col)) is None:
                return True

        elif abs(new_col - current_col) == 1 and new_row == current_row + direction:
            target_piece = board.get_piece_at(new_position)
            if target_piece and target_piece.color != self.color:
                return True

        return False


class Rook(Figure):
    """Класс, определяющий ладью."""
    def symbol(self):
        return "R" if self.color == "white" else "r"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        if current_row == new_row:
            step = 1 if new_col > current_col else -1
            for col in range(current_col + step, new_col, step):
                if board.get_piece_at((current_row, col)) is not None:
                    return False

        elif current_col == new_col:
            step = 1 if new_row > current_row else -1
            for row in range(current_row + step, new_row, step):
                if board.get_piece_at((row, current_col)) is not None:
                    return False

        else:
            return False

        target_piece = board.get_piece_at(new_position)
        if target_piece is None or target_piece.color != self.color:
            return True
        return False


class Knight(Figure):
    """Класс, определяющий коня."""
    def symbol(self):
        return "H" if self.color == "white" else "h"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        row_diff = abs(new_row - current_row)
        col_diff = abs(new_col - current_col)

        if not ((row_diff == 1 and col_diff == 2) or (row_diff == 2 and col_diff == 1)):
            return False
        else:
            return True

        target_piece = board.get_piece_at(new_position)
        if target_piece is None or target_piece.color != self.color:
            return True
        return False


class Bishop(Figure):
    """Класс, определяющий слона"""
    def symbol(self):
        return "B" if self.color == "white" else "b"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        if abs(new_row - current_row) != abs(new_col - current_col):
            return False

        row_step = 1 if new_row > current_row else -1
        col_step = 1 if new_col > current_col else -1

        row, col = current_row + row_step, current_col + col_step
        while row != new_row and col != new_col:
            if board.get_piece_at((row, col)) is not None:
                return False
            row += row_step
            col += col_step

        target_piece = board.get_piece_at(new_position)
        if target_piece is None or target_piece.color != self.color:
            return True
        return False


class Queen(Figure):
    """Класс, определяющий ферзя."""
    def symbol(self):
        return "Q" if self.color == "white" else "q"

    def is_valid_move(self, board, new_position):
        rook_moves = Rook(self.color, self.position).is_valid_move(board, new_position)
        bishop_moves = Bishop(self.color, self.position).is_valid_move(board, new_position)
        return rook_moves or bishop_moves


class King(Figure):
    """Класс, определяющий короля."""
    def symbol(self):
        return "K" if self.color == "white" else "k"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        row_diff = abs(new_row - current_row)
        col_diff = abs(new_col - current_col)

        if not (row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff > 0)):
            return False

        target_piece = board.get_piece_at(new_position)
        if target_piece is None or target_piece.color != self.color:
            return True
        return False


class Elephant(Figure):
    """ Класс, определяющий нового слона.
        Новый слон ходит на 2 клетки по диагонали.
        Может перепрыгивать через фигуры."""
    def symbol(self):
        return "E" if self.color == "white" else "e"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        row_diff = abs(new_row - current_row)
        col_diff = abs(new_col - current_col)

        if row_diff == 2 and col_diff == 2:
            target = board.get_piece_at(new_position)
            if target is None or target.color != self.color:
                return True

        return False


class Miner(Figure):
    """Класс, определяющий сапёра.
       Сапёр ходит на 1 клетку в любом направлении,
       но не бьёт вражеские фигуры."""
    def symbol(self):
        return "M" if self.color == "white" else "m"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        row_diff = abs(new_row - current_row)
        col_diff = abs(new_col - current_col)

        if row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff > 0):
            target = board.get_piece_at(new_position)
            if target is None:
                return True
        return False


class Healer(Figure):
    """Класс, описывающий лекаря.
       Лекарь перепрыгивает через одну фигуру по горизонтали или вертикали на 2 клетки.
       Не может бить, только перемещается на пустые клетки."""
    def symbol(self):
        return "D" if self.color == "white" else "d"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        row_diff = new_row - current_row
        col_diff = new_col - current_col

        if row_diff == 0 and abs(col_diff) == 2:
            step = 1 if col_diff > 0 else -1
            mid_col = current_col + step
            middle = board.get_piece_at((current_row, mid_col))
            if middle is not None:
                target = board.get_piece_at(new_position)
                if target is None:
                    return True

        elif col_diff == 0 and abs(row_diff) == 2:
            step = 1 if row_diff > 0 else -1
            mid_row = current_row + step
            middle = board.get_piece_at((mid_row, current_col))
            if middle is not None:
                target = board.get_piece_at(new_position)
                if target is None:
                    return True

        return False


class Checker(Figure):
    """Класс, определяющий шашку."""
    def symbol(self):
        return "x" if self.color == "white" else "o"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        direction = 1 if self.color == "white" else -1
        row_diff = new_row - current_row
        col_diff = abs(new_col - current_col)

        if row_diff == direction and col_diff == 1:
            if board.get_piece_at(new_position) is None:
                return True

        if row_diff == 2 * direction and col_diff == 2:
            middle_row = current_row + direction
            middle_col = current_col + (1 if new_col > current_col else -1)
            middle_piece = board.get_piece_at((middle_row, middle_col))
            if middle_piece and middle_piece.color != self.color and board.get_piece_at(new_position) is None:
                return True

        return False


class CheckerKing(Checker):
    """Класс, определяющий шашечную дамку."""
    def symbol(self):
        return "X" if self.color == "white" else "O"

    def is_valid_move(self, board, new_position):
        current_row, current_col = self.position
        new_row, new_col = new_position

        if not (0 <= new_row < 8 and 0 <= new_col < 8):
            return False

        row_diff = new_row - current_row
        col_diff = new_col - current_col

        if abs(row_diff) != abs(col_diff):
            return False

        row_step = 1 if row_diff > 0 else -1
        col_step = 1 if col_diff > 0 else -1

        row, col = current_row + row_step, current_col + col_step
        captured = None

        while (row, col) != (new_row, new_col):
            if not (0 <= row < 8 and 0 <= col < 8):
                return False
            piece = board.get_piece_at((row, col))
            if piece:
                if captured is None and piece.color != self.color:
                    captured = piece
                else:
                    return False
            row += row_step
            col += col_step

        target = board.get_piece_at(new_position)
        if captured:
            return target is None
        return target is None or target.color != self.color


class Board:
    """Класс, описывающий доску для шахмат и шашек."""
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.history = []
        self.mode = "chess"
        self.initialize_board()

    def initialize_board(self):
        for col in range(8):
            self.grid[1][col] = Pawn('white', (1, col))
            self.grid[6][col] = Pawn('black', (6, col))

        self.grid[0][0] = Rook('white', (0, 0))
        self.grid[0][7] = Rook('white', (0, 7))
        self.grid[7][0] = Rook('black', (7, 0))
        self.grid[7][7] = Rook('black', (7, 7))

        self.grid[0][1] = Knight('white', (0, 1))
        self.grid[0][6] = Knight('white', (0, 6))
        self.grid[7][1] = Knight('black', (7, 1))
        self.grid[7][6] = Knight('black', (7, 6))

        self.grid[0][2] = Bishop('white', (0, 2))
        self.grid[0][5] = Bishop('white', (0, 5))
        self.grid[7][2] = Bishop('black', (7, 2))
        self.grid[7][5] = Bishop('black', (7, 5))

        self.grid[0][3] = Queen('white', (0, 3))
        self.grid[7][3] = Queen('black', (7, 3))

        self.grid[0][4] = King('white', (0, 4))
        self.grid[7][4] = King('black', (7, 4))

    def setup_checkers(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Checker('white', (r, c))
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Checker('black', (r, c))
        self.mode = "checkers"

    def setup_new_figures(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        for col in range(8):
            self.grid[1][col] = Pawn('white', (1, col))
            self.grid[6][col] = Pawn('black', (6, col))

        self.grid[0][0] = Rook('white', (0, 0))
        self.grid[0][7] = Rook('white', (0, 7))
        self.grid[7][0] = Rook('black', (7, 0))
        self.grid[7][7] = Rook('black', (7, 7))

        self.grid[0][1] = Elephant('white', (0, 1))
        self.grid[0][6] = Miner('white', (0, 6))
        self.grid[7][1] = Elephant('black', (7, 1))
        self.grid[7][6] = Miner('black', (7, 6))

        self.grid[0][2] = Healer('white', (0, 2))
        self.grid[0][5] = Healer('white', (0, 5))
        self.grid[7][2] = Healer('black', (7, 2))
        self.grid[7][5] = Healer('black', (7, 5))

        self.grid[0][3] = Queen('white', (0, 3))
        self.grid[7][3] = Queen('black', (7, 3))

        self.grid[0][4] = King('white', (0, 4))
        self.grid[7][4] = King('black', (7, 4))
        self.mode = "new_figures"

    def get_piece_at(self, position):
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None

    def inside(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def find_king_position(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if isinstance(piece, King) and piece.color == color:
                    return (r, c)
        return None

    def is_square_attacked(self, position, attacking_color):
        target_row, target_col = position
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.color == attacking_color:
                    original_pos = piece.position
                    piece.position = (r, c)
                    if piece.is_valid_move(self, (target_row, target_col)):
                        piece.position = original_pos
                        return True
                    piece.position = original_pos
        return False

    def is_in_check(self, color):
        if self.mode == "checkers":
            return False
        king_pos = self.find_king_position(color)
        if king_pos is None:
            return False
        opponent_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(king_pos, opponent_color)

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    original_pos = piece.position
                    piece.position = (r, c)

                    for new_row in range(8):
                        for new_col in range(8):
                            if piece.is_valid_move(self, (new_row, new_col)):
                                temp_board = copy.deepcopy(self)
                                temp_piece = temp_board.grid[r][c]
                                temp_piece.position = (r, c)

                                temp_board.grid[new_row][new_col] = temp_piece
                                temp_board.grid[r][c] = None
                                temp_piece.position = (new_row, new_col)

                                if not temp_board.is_in_check(color):
                                    piece.position = original_pos
                                    return False

                    piece.position = original_pos
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    original_pos = piece.position
                    piece.position = (r, c)

                    for new_row in range(8):
                        for new_col in range(8):
                            if piece.is_valid_move(self, (new_row, new_col)):
                                temp_board = copy.deepcopy(self)
                                temp_piece = temp_board.grid[r][c]
                                temp_piece.position = (r, c)

                                temp_board.grid[new_row][new_col] = temp_piece
                                temp_board.grid[r][c] = None
                                temp_piece.position = (new_row, new_col)

                                if not temp_board.is_in_check(color):
                                    piece.position = original_pos
                                    return False

                    piece.position = original_pos
        return True

    def make_move(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        piece = self.grid[start_row][start_col]
        if not piece:
            print("Начальная позиция пуста.")
            return False

        if not piece.is_valid_move(self, end_pos):
            print("Неверный ход.")
            return False

        target_piece = self.get_piece_at(end_pos)
        if target_piece and target_piece.color == piece.color:
            print("Нельзя съесть свою фигуру.")
            return False

        if self.mode != "checkers":
            temp_board = copy.deepcopy(self)
            temp_piece = temp_board.grid[start_row][start_col]
            temp_piece.position = start_pos

            temp_board.grid[end_row][end_col] = temp_piece
            temp_board.grid[start_row][start_col] = None
            temp_piece.position = end_pos

            if temp_board.is_in_check(piece.color):
                print("Ход невозможен: король будет под шахом!")
                return False

        move = Move(piece, Position(start_row, start_col), Position(end_row, end_col), target_piece)
        self.history.append(move)

        self.grid[end_row][end_col] = piece
        self.grid[start_row][start_col] = None
        piece.position = end_pos
        piece.was_moved = True

        if self.mode != "checkers" and isinstance(piece, Pawn):
            if (piece.color == "white" and end_row == 7) or (piece.color == "black" and end_row == 0):
                self.grid[end_row][end_col] = Queen(piece.color, end_pos)

        if self.mode == "checkers" and isinstance(piece, Checker):
            if (piece.color == "white" and end_row == 0) or (piece.color == "black" and end_row == 7):
                self.grid[end_row][end_col] = CheckerKing(piece.color, end_pos)
        return True

    def undo_move(self):
        if not self.history:
            print("Нет ходов для отката.")
            return False

        move = self.history.pop()

        self.grid[move.start.row][move.start.col] = move.piece
        move.piece.position = (move.start.row, move.start.col)
        move.piece.was_moved = False

        self.grid[move.end.row][move.end.col] = move.captured

        return True

    def move_piece(self, start_pos, end_pos):
        return self.make_move(start_pos, end_pos)

    def get_threatened_pieces(self, color):
        threatened = []
        opponent_color = 'black' if color == 'white' else 'white'

        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    if self.is_square_attacked((r, c), opponent_color):
                        threatened.append((r, c))
        return threatened

    def display(self, threatened=None, check_pos=None):
        print(" +----------------+")
        for r in range(7, -1, -1):
            row_str = f"{r + 1}|"
            for c in range(8):
                piece = self.grid[r][c]
                if piece:
                    symbol = piece.symbol()
                    if check_pos and (r, c) == check_pos:
                        row_str += "!" + symbol + " "
                    elif threatened and (r, c) in threatened:
                        row_str += "!" + symbol + " "
                    else:
                        row_str += symbol + " "
                else:
                    row_str += ". "
            print(row_str + "|")
        print(" +----------------+")
        print("  a b c d e f g h")


class Game:
    """Класс, определяющий игровой процесс."""
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'
        self.game_over = False
        self.result_message = ""

    def choose_mode(self):
        print("\nВыберите режим игры:")
        print("1 - Обычные шахматы")
        print("2 - Шахматы с новыми фигурами")
        print("3 - Шашки")

        choice = input("Ваш выбор (1/2/3): ").strip()
        if choice == "2":
            self.board.setup_new_figures()
        elif choice == "3":
            self.board.setup_checkers()
        else:
            self.board.initialize_board()

    def parse_move_input(self, move_str):
        try:
            parts = move_str.split()
            if len(parts) != 2:
                raise ValueError("Ожидается формат 'e2 e4'")

            start_coord = parts[0]
            end_coord = parts[1]

            start_col = ord(start_coord[0]) - ord('a')
            start_row = int(start_coord[1]) - 1
            end_col = ord(end_coord[0]) - ord('a')
            end_row = int(end_coord[1]) - 1

            return (start_row, start_col), (end_row, end_col)
        except (IndexError, ValueError):
            print("Неверный формат ввода. Необходимо: 'e2 e4'.")
            return None, None

    def get_game_status(self):
        if self.board.mode == "checkers":
            return None
        if self.board.is_checkmate(self.current_turn):
            winner = "Чёрные" if self.current_turn == "white" else "Белые"
            return f"МАТ! Победили {winner}!"
        elif self.board.is_stalemate(self.current_turn):
            return "ПАТ! Ничья!"
        elif self.board.is_in_check(self.current_turn):
            return "ШАХ!"
        return None

    def run(self):
        self.choose_mode()

        print("\nДля хода введите начальную и конечную позицию (например, 'e2 e4').")
        print("Команды:")
        print("  undo - откат последнего хода")
        print("  exit - выход")

        while not self.game_over:
            threatened = self.board.get_threatened_pieces(self.current_turn)
            king_pos = self.board.find_king_position(self.current_turn)
            check_pos = king_pos if self.board.is_in_check(self.current_turn) else None

            self.board.display(check_pos=check_pos, threatened=threatened)

            status = self.get_game_status()
            if status:
                print(status)
                if "МАТ" in status or "ПАТ" in status:
                    self.game_over = True
                    self.result_message = status
                    break

            print(f"\nХод {self.current_turn} игрока.")
            move_input = input("Ваш ход: ").lower()

            if move_input == 'exit':
                self.game_over = True
                self.result_message = 'Игра завершена.'
                print(self.result_message)
                break

            if move_input == 'undo':
                if self.board.undo_move():
                    self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                continue

            start_pos, end_pos = self.parse_move_input(move_input)

            if start_pos is None or end_pos is None:
                continue

            piece_to_move = self.board.get_piece_at(start_pos)

            if piece_to_move is None or piece_to_move.color != self.current_turn:
                print("Неверная фигура для хода или не ваш ход.")
                continue

            if self.board.move_piece(start_pos, end_pos):
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        if self.game_over and "МАТ" not in self.result_message and "ПАТ" not in self.result_message:
            print("Игра окончена.")


if __name__ == "__main__":
    game = Game()
    game.run()
