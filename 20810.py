import pygame
import sys




# 파이게임
pygame.init()




# 보드, 색상 등 설정
WIDTH, HEIGHT = 800, 800
CELL_SIZE = WIDTH // 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GREEN = (144, 238, 144)
FONT_SIZE = 50
FONT = pygame.font.Font(None, FONT_SIZE)




# 화면 초기화
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")




# 체스판
chessboard = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]


# 기물 선택 함수
selected_piece = None
selected_row = None
selected_col = None


valid_moves = []  # 유효한 이동 확인 변수


# 킹과 룩의 이동 확인 변수
white_king_moved = False
black_king_moved = False
white_king_rook_moved = False
white_queen_rook_moved = False
black_king_rook_moved = False
black_queen_rook_moved = False


# 체스 판 만들기
def draw_chessboard():
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = WHITE
            else:
                color = BLACK
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


#기물 생성
def draw_pieces(): 
    for row in range(8):
        for col in range(8):
            piece = chessboard[row][col]
            if piece:
                piece_color = BROWN if piece.islower() else GRAY
                text = FONT.render(piece, True, piece_color)
                text_rect = text.get_rect()
                text_rect.center = (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
                screen.blit(text, text_rect)


#이동 가능 영역 표시
def draw_valid_moves(valid_moves):
    for move in valid_moves:
        row, col = move
        pygame.draw.rect(screen, LIGHT_GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# 기물의 이동
def move_piece(start_row, start_col, end_row, end_col):
    piece = chessboard[start_row][start_col]
    chessboard[end_row][end_col] = piece
    chessboard[start_row][start_col] = ""


# 폰의 이동 확인
def is_valid_pawn_move(start_row, start_col, end_row, end_col, player_color):
    # 폰의 방향 설정
    if player_color == "white":
        direction = -1  # 흰색 폰 방향
        start_row_first_move = 6  # 폰의 위치
    else:
        direction = 1  # 검은색 폰 방향
        start_row_first_move = 1  # 폰의 위치

    delta_x = end_col - start_col
    delta_y = end_row - start_row

    if delta_x == 0:
        if delta_y == direction:
            if chessboard[end_row][end_col] == "":
                return True
        elif delta_y == 2 * direction and start_row == start_row_first_move:
            if chessboard[end_row][end_col] == "" and chessboard[start_row + direction][start_col] == "":
                return True
    elif abs(delta_x) == 1 and delta_y == direction:
        if chessboard[end_row][end_col] != "" and (chessboard[end_row][end_col].islower() if player_color == "white" else chessboard[end_row][end_col].isupper()):
            return True

    return False



# 나이트의 이동 확인
def is_valid_knight_move(start_row, start_col, end_row, end_col):
    delta_x = abs(end_col - start_col)
    delta_y = abs(end_row - start_row)
    return (delta_x == 2 and delta_y == 1) or (delta_x == 1 and delta_y == 2)


# 비숍의 이동 확인
def is_valid_bishop_move(start_row, start_col, end_row, end_col):
    delta_x = abs(end_col - start_col)
    delta_y = abs(end_row - start_row)

    if delta_x != delta_y:
        return False

    # 이동경로에 다른 기물이 있는가?
    step_x = 1 if end_col > start_col else -1 if end_col < start_col else 0
    step_y = 1 if end_row > start_row else -1 if end_row < start_row else 0
    row, col = start_row + step_y, start_col + step_x
    while row != end_row:
        if chessboard[row][col] != "":
            return False
        row += step_y
        col += step_x

    return True

# 룩의 이동 확인
def is_valid_rook_move(start_row, start_col, end_row, end_col):
    delta_x = abs(end_col - start_col)
    delta_y = abs(end_row - start_row)

    if delta_x > 0 and delta_y > 0:
        return False  # 대각선 이동 불가
    
    step_x = 1 if end_col > start_col else -1 if end_col < start_col else 0
    step_y = 1 if end_row > start_row else -1 if end_row < start_row else 0
    row, col = start_row + step_y, start_col + step_x
    while row != end_row or col != end_col:
        if chessboard[row][col] != "":
            return False
        row += step_y
        col += step_x

    return True


# 킹의 이동 확인
def is_valid_king_move(start_row, start_col, end_row, end_col):
    delta_x = abs(end_col - start_col)
    delta_y = abs(end_row - start_row)
    return delta_x <= 1 and delta_y <= 1


# 퀸의 이동 확인
def is_valid_queen_move(start_row, start_col, end_row, end_col):
    delta_x = abs(end_col - start_col)
    delta_y = abs(end_row - start_row)

    if delta_x == 0 or delta_y == 0:
        # 직선 경로
        step_x = 1 if end_col > start_col else -1 if end_col < start_col else 0
        step_y = 1 if end_row > start_row else -1 if end_row < start_row else 0
        row, col = start_row + step_y, start_col + step_x
        while row != end_row or col != end_col:
            if chessboard[row][col] != "":
                return False
            row += step_y
            col += step_x
        return True

    if delta_x == delta_y:
        # 대각선 경로
        step_x = 1 if end_col > start_col else -1 if end_col < start_col else 0
        step_y = 1 if end_row > start_row else -1 if end_row < start_row else 0
        row, col = start_row + step_y, start_col + step_x
        while row != end_row:
            if chessboard[row][col] != "":
                return False
            row += step_y
            col += step_x
        return True
    return False

# 캐슬링
def is_valid_castling_move(start_row, start_col, end_row, end_col, player_color):
    if player_color == "white":
        king_row = 7
    else:
        king_row = 0

    if start_row != king_row or start_col != 4:
        return False  # 킹 선택

    if end_row != king_row:
        return False  # 캐슬링 중 이동 불가

    if abs(end_col - start_col) != 2:
        return False  # 캐슬링 중 이동가능 경로

    # 1. 두 기물 사이가 비어있나?
    if end_col > start_col:
        rook_col = 7
    else:
        rook_col = 0
    for col in range(start_col + 1, rook_col):
        if chessboard[king_row][col] != "":
            return False
        
    # 2. 킹과 룩이 이전에 움직이지 않았는가?
    if player_color == "white":
        if white_king_moved or white_king_rook_moved:
            return False
    else:
        if black_king_moved or black_king_rook_moved:
            return False
        
    return True

# 폰을 승급
def promote_pawn(row, col, player_color):
    if player_color == "white" and row == 0:
        chessboard[row][col] = "Q"
    elif player_color == "black" and row == 7:
        chessboard[row][col] = "q"

# 아군을 무시하지 않기
def is_valid_move_without_jumping(start_row, start_col, end_row, end_col, player_color):
    piece = chessboard[start_row][start_col]
    target = chessboard[end_row][end_col]

    # 목표 칸에 다른 기물이 있는가?
    if (target != "" and target.isupper() and player_color == "white") or (target != "" and target.islower() and player_color == "black"):
        return False
    if piece in ("P", "p"):
        return is_valid_pawn_move(start_row, start_col, end_row, end_col, player_color)
    elif piece in ("N", "n"):
        return is_valid_knight_move(start_row, start_col, end_row, end_col)
    elif piece in ("B", "b"):
        return is_valid_bishop_move(start_row, start_col, end_row, end_col)
    elif piece in ("R", "r"):
        return is_valid_rook_move(start_row, start_col, end_row, end_col)
    elif piece in ("Q", "q"):
        return is_valid_queen_move(start_row, start_col, end_row, end_col)
    elif piece in ("K", "k"):
        return is_valid_king_move(start_row, start_col, end_row, end_col)
    elif piece in ("K", "k"):
        return is_valid_castling_move(start_row, start_col, end_row, end_col, player_color)
    return False

# 유효한 이동
def calculate_valid_moves(row, col, player_color):
    piece = chessboard[row][col]
    valid_moves = []
    for i in range(8):
        for j in range(8):
            if (row, col) != (i, j) and is_valid_move_without_jumping(row, col, i, j, player_color):
                valid_moves.append((i, j))
    return valid_moves

# 조각을 이동하려고 시도, 이동이 유효한가?
def try_move_piece(start_row, start_col, end_row, end_col):
    if is_valid_move_without_jumping(start_row, start_col, end_row, end_col, turn):
        move_piece(start_row, start_col, end_row, end_col)
        if (turn == "white" and end_row == 0) or (turn == "black" and end_row == 7):
            promote_pawn(end_row, end_col, turn)
        return True
    return False

# 선택 기물 바꾸기
def deselect_piece():
    global selected_piece, selected_row, selected_col, valid_moves
    selected_piece = None
    selected_row = None
    selected_col = None
    valid_moves = []

# 다른 기물 선택
def switch_selected_piece(new_row, new_col):
    global selected_piece, selected_row, selected_col, valid_moves
    selected_piece = chessboard[new_row][new_col]
    selected_row = new_row
    selected_col = new_col
    valid_moves = calculate_valid_moves(new_row, new_col, turn)

# 유효한 이동 표시
def draw_valid_moves(valid_moves):
    for move in valid_moves:
        row, col = move
        target_piece = chessboard[row][col]
        # 아군 기물이 있는 칸은 이동 불가
        if target_piece == "":
            pygame.draw.rect(screen, LIGHT_GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        elif (turn == "white" and target_piece.islower()) or (turn == "black" and target_piece.isupper()):
            pygame.draw.rect(screen, LIGHT_GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# 킹이 잡혔는가
def is_king_captured():
    white_king_captured = all("K" not in row for row in chessboard)
    black_king_captured = all("k" not in row for row in chessboard)
    # 승리 선언
    if white_king_captured:
        return "black"
    elif black_king_captured:
        return "white"
    else:
        return None

# 게임
running = True
turn = "white"  # 백색이 선공

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            clicked_col = x // CELL_SIZE
            clicked_row = y // CELL_SIZE
            if selected_piece is None:
                piece = chessboard[clicked_row][clicked_col]
                if piece != "" and (turn == "white" and piece.isupper() or turn == "black" and piece.islower()):
                    selected_piece = piece
                    selected_row = clicked_row
                    selected_col = clicked_col
                    valid_moves = calculate_valid_moves(clicked_row, clicked_col, turn)
                else:
                    deselect_piece()
            else:
                if (clicked_row, clicked_col) == (selected_row, selected_col):
                    deselect_piece()
                elif (clicked_row, clicked_col) in valid_moves:
                    if try_move_piece(selected_row, selected_col, clicked_row, clicked_col):
                        deselect_piece()
                        turn = "white" if turn == "black" else "black"
                        winner = is_king_captured()
                        if winner:
                            print(f"{winner.capitalize()} wins!")
                            running = False
                    else:
                        deselect_piece()
                elif (turn == "white" and chessboard[clicked_row][clicked_col].isupper()) or (turn == "black" and chessboard[clicked_row][clicked_col].islower()):
                    switch_selected_piece(clicked_row, clicked_col)
                else:
                    deselect_piece()

    draw_chessboard()
    draw_pieces()
    if valid_moves:
        draw_valid_moves(valid_moves)

    pygame.display.flip()

# 게임 종료
pygame.quit()
sys.exit()

