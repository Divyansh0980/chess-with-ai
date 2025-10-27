
import pygame
import sys
import copy

SQ_SIZE = 80
BOARD_SIZE = SQ_SIZE * 8
FPS = 60
ANIMATION_SPEED = 10  

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (50, 205, 50, 120)
CHECK_HIGHLIGHT = (255, 0, 0, 120)
MOVE_HIGHLIGHT = (255, 255, 0, 100)
TEXT_COLOR = (10, 10, 10)

PIECE_TO_IMG = {
    'P': 'wp.png', 'R': 'wr.png', 'N': 'wn.png', 'B': 'wb.png', 'Q': 'wq.png', 'K': 'wk.png',
    'p': 'bp.png', 'r': 'br.png', 'n': 'bn.png', 'b': 'bb.png', 'q': 'bq.png', 'k': 'bk.png'
}

STARTING_BOARD = [
    ['r','n','b','q','k','b','n','r'],
    ['p','p','p','p','p','p','p','p'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['P','P','P','P','P','P','P','P'],
    ['R','N','B','Q','K','B','N','R']
]

class GameState:
    def __init__(self):
        self.board = [row[:] for row in STARTING_BOARD]
        self.white_turn = True
        self.en_passant_target = None  # (row, col) of target square
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.king_moved = {'white': False, 'black': False}
        self.rook_moved = {'white': {'kingside': False, 'queenside': False},
                          'black': {'kingside': False, 'queenside': False}}
        self.move_history = []
        self.last_move = None

    def copy(self):
        new_state = GameState()
        new_state.board = [row[:] for row in self.board]
        new_state.white_turn = self.white_turn
        new_state.en_passant_target = self.en_passant_target
        new_state.castling_rights = self.castling_rights.copy()
        new_state.king_moved = self.king_moved.copy()
        new_state.rook_moved = copy.deepcopy(self.rook_moved)
        new_state.last_move = self.last_move
        return new_state

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def is_white(p):
    return p.isupper()

def is_black(p):
    return p.islower()

def find_king(board, white):
    target = 'K' if white else 'k'
    for r in range(8):
        for c in range(8):
            if board[r][c] == target:
                return (r, c)
    return None

def is_attacked(board, r, c, by_white):
    """Check if square (r,c) is attacked by pieces of color by_white"""
    pawn_dir = 1 if by_white else -1
    pawn = 'P' if by_white else 'p'
    for dc in [-1, 1]:
        pr, pc = r + pawn_dir, c + dc
        if in_bounds(pr, pc) and board[pr][pc] == pawn:
            return True
    
    knight = 'N' if by_white else 'n'
    for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == knight:
            return True
    
    king = 'K' if by_white else 'k'
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            kr, kc = r + dr, c + dc
            if in_bounds(kr, kc) and board[kr][kc] == king:
                return True
    
    rook_queen = ['R', 'Q'] if by_white else ['r', 'q']
    bishop_queen = ['B', 'Q'] if by_white else ['b', 'q']
    
    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] != '.':
                if board[nr][nc] in rook_queen:
                    return True
                break
            nr += dr
            nc += dc
    
    for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] != '.':
                if board[nr][nc] in bishop_queen:
                    return True
                break
            nr += dr
            nc += dc
    
    return False

def is_in_check(board, white):
    king_pos = find_king(board, white)
    if not king_pos:
        return False
    return is_attacked(board, king_pos[0], king_pos[1], not white)

def get_pseudo_legal_moves(state, r, c):
    """Get moves without checking if they leave king in check"""
    board = state.board
    piece = board[r][c]
    if piece == '.':
        return []
    
    moves = []
    color_white = piece.isupper()
    p = piece.lower()

    if p == 'p':
        direction = -1 if color_white else 1
        start_row = 6 if color_white else 1
        
        if in_bounds(r + direction, c) and board[r + direction][c] == '.':
            moves.append((r + direction, c))
            if r == start_row and board[r + 2*direction][c] == '.':
                moves.append((r + 2*direction, c))
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if in_bounds(nr, nc):
                target = board[nr][nc]
                if target != '.' and (target.isupper() != color_white):
                    moves.append((nr, nc))
        
        if state.en_passant_target:
            ep_r, ep_c = state.en_passant_target
            if r + direction == ep_r and abs(c - ep_c) == 1:
                moves.append((ep_r, ep_c))
        
        return moves
    
    if p == 'n':
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc):
                target = board[nr][nc]
                if target == '.' or target.isupper() != color_white:
                    moves.append((nr, nc))
        return moves

    if p in ('b', 'r', 'q'):
        directions = []
        if p in ('r', 'q'):
            directions += [(1,0),(-1,0),(0,1),(0,-1)]
        if p in ('b', 'q'):
            directions += [(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while in_bounds(nr, nc):
                target = board[nr][nc]
                if target == '.':
                    moves.append((nr, nc))
                else:
                    if target.isupper() != color_white:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return moves

    if p == 'k':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target == '.' or target.isupper() != color_white:
                        moves.append((nr, nc))
        
        if not is_in_check(board, color_white):
            row = 7 if color_white else 0
            if r == row and c == 4:
                if state.castling_rights['K' if color_white else 'k']:
                    if (board[row][5] == '.' and board[row][6] == '.' and
                        not is_attacked(board, row, 5, not color_white) and
                        not is_attacked(board, row, 6, not color_white)):
                        moves.append((row, 6))
                
                if state.castling_rights['Q' if color_white else 'q']:
                    if (board[row][3] == '.' and board[row][2] == '.' and board[row][1] == '.' and
                        not is_attacked(board, row, 3, not color_white) and
                        not is_attacked(board, row, 2, not color_white)):
                        moves.append((row, 2))
        
        return moves

    return moves

def get_legal_moves(state, r, c):
    """Get legal moves that don't leave king in check"""
    pseudo_moves = get_pseudo_legal_moves(state, r, c)
    legal_moves = []
    
    for move in pseudo_moves:
        new_state = make_move(state, (r, c), move, validate=False)
        if not is_in_check(new_state.board, state.white_turn):
            legal_moves.append(move)
    
    return legal_moves

def make_move(state, from_pos, to_pos, validate=True):
    """Make a move and return new state"""
    r1, c1 = from_pos
    r2, c2 = to_pos
    
    new_state = state.copy()
    board = new_state.board
    piece = board[r1][c1]
    
    is_en_passant = False
    if piece.lower() == 'p' and state.en_passant_target == (r2, c2):
        is_en_passant = True
        capture_row = r1
        board[capture_row][c2] = '.'
    
    is_castling = False
    if piece.lower() == 'k' and abs(c2 - c1) == 2:
        is_castling = True
        if c2 == 6:  # Kingside
            board[r1][5] = board[r1][7]
            board[r1][7] = '.'
        else:  # Queenside
            board[r1][3] = board[r1][0]
            board[r1][0] = '.'
    
    board[r2][c2] = piece
    board[r1][c1] = '.'
    
    if piece == 'P' and r2 == 0:
        board[r2][c2] = 'Q'
    elif piece == 'p' and r2 == 7:
        board[r2][c2] = 'q'
    new_state.en_passant_target = None
    if piece.lower() == 'p' and abs(r2 - r1) == 2:
        new_state.en_passant_target = ((r1 + r2) // 2, c1)
    
    if piece == 'K':
        new_state.castling_rights['K'] = False
        new_state.castling_rights['Q'] = False
    elif piece == 'k':
        new_state.castling_rights['k'] = False
        new_state.castling_rights['q'] = False
    elif piece == 'R':
        if r1 == 7 and c1 == 7:
            new_state.castling_rights['K'] = False
        elif r1 == 7 and c1 == 0:
            new_state.castling_rights['Q'] = False
    elif piece == 'r':
        if r1 == 0 and c1 == 7:
            new_state.castling_rights['k'] = False
        elif r1 == 0 and c1 == 0:
            new_state.castling_rights['q'] = False
    
    new_state.last_move = (from_pos, to_pos)
    new_state.white_turn = not state.white_turn
    
    return new_state

def all_legal_moves(state):
    """Get all legal moves for current player"""
    moves = []
    for r in range(8):
        for c in range(8):
            piece = state.board[r][c]
            if piece != '.' and is_white(piece) == state.white_turn:
                for to_pos in get_legal_moves(state, r, c):
                    moves.append(((r, c), to_pos))
    return moves

def is_checkmate(state):
    """Check if current player is in checkmate"""
    if not is_in_check(state.board, state.white_turn):
        return False
    return len(all_legal_moves(state)) == 0

def is_stalemate(state):
    """Check if current player is in stalemate"""
    if is_in_check(state.board, state.white_turn):
        return False
    return len(all_legal_moves(state)) == 0

def eval_board(state):
    """Evaluate board position"""
    piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
    
    if is_checkmate(state):
        return 10000 if not state.white_turn else -10000
    if is_stalemate(state):
        return 0
    
    val = 0
    for row in state.board:
        for p in row:
            if p == '.':
                continue
            score = piece_values[p.lower()]
            val += score if p.isupper() else -score
    
    return val

def minimax(state, depth, alpha, beta, maximizing):
    """Minimax with alpha-beta pruning"""
    if depth == 0 or is_checkmate(state) or is_stalemate(state):
        return eval_board(state), None
    
    moves = all_legal_moves(state)
    if not moves:
        return eval_board(state), None
    
    best_move = None
    
    if maximizing:
        max_eval = -99999
        for from_pos, to_pos in moves:
            new_state = make_move(state, from_pos, to_pos)
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (from_pos, to_pos)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = 99999
        for from_pos, to_pos in moves:
            new_state = make_move(state, from_pos, to_pos)
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (from_pos, to_pos)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def load_images():
    """Load piece images"""
    imgs = {}
    for code, filename in PIECE_TO_IMG.items():
        try:
            img = pygame.image.load('images/' + filename).convert_alpha()
            imgs[code] = pygame.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))
        except:
            surf = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surf.fill((150, 150, 150))
            imgs[code] = surf
    return imgs

def create_sound(freq, duration=100):
    """Create simple sound effect"""
    try:
        sample_rate = 22050
        frames = int(duration * sample_rate / 1000)
        arr = []
        for i in range(frames):
            value = int(32767 * 0.3 * pygame.math.Vector2(1, 0).rotate(360 * freq * i / sample_rate).x)
            arr.append([value, value])
        sound = pygame.sndarray.make_sound(pygame.array.array('h', [item for sublist in arr for item in sublist]))
        return sound
    except:
        return None

def draw_board(screen):
    """Draw chess board"""
    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board, imgs, animating_piece=None):
    """Draw pieces on board"""
    for r in range(8):
        for c in range(8):
            if animating_piece and animating_piece['from'] == (r, c):
                continue
            piece = board[r][c]
            if piece != '.' and piece in imgs:
                screen.blit(imgs[piece], (c*SQ_SIZE, r*SQ_SIZE))

def highlight_squares(screen, squares, color=HIGHLIGHT):
    """Highlight squares"""
    surf = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
    surf.fill(color)
    for r, c in squares:
        screen.blit(surf, (c*SQ_SIZE, r*SQ_SIZE))

def coords_to_square(pos):
    """Convert pixel coordinates to board square"""
    return pos[1] // SQ_SIZE, pos[0] // SQ_SIZE

def menu(screen, font):
    """Display game menu"""
    modes = ["Player vs Player", "Player vs Computer"]
    levels = ["Easy", "Medium", "Hard"]
    sides = ["White", "Black"]
    mode_idx, level_idx, side_idx = 0, 0, 0

    while True:
        screen.fill((200, 200, 200))
        
        title = font.render("Chess Game", True, TEXT_COLOR)
        mode_text = font.render(f"Mode: {modes[mode_idx]} (UP/DOWN)", True, TEXT_COLOR)
        level_text = font.render(f"Difficulty: {levels[level_idx]} (LEFT/RIGHT)", True, TEXT_COLOR)
        side_text = font.render(f"Your Side: {sides[side_idx]} (SPACE)", True, TEXT_COLOR)
        start_text = font.render("Press ENTER to Start", True, (20, 20, 20))
        
        screen.blit(title, (BOARD_SIZE//2 - title.get_width()//2, 50))
        screen.blit(mode_text, (80, 150))
        screen.blit(level_text, (80, 210))
        screen.blit(side_text, (80, 270))
        screen.blit(start_text, (80, 350))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return modes[mode_idx], levels[level_idx], sides[side_idx]
                elif event.key == pygame.K_UP:
                    mode_idx = (mode_idx - 1) % 2
                elif event.key == pygame.K_DOWN:
                    mode_idx = (mode_idx + 1) % 2
                elif event.key == pygame.K_LEFT:
                    level_idx = (level_idx - 1) % 3
                elif event.key == pygame.K_RIGHT:
                    level_idx = (level_idx + 1) % 3
                elif event.key == pygame.K_SPACE:
                    side_idx = (side_idx + 1) % 2

def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption("Enhanced Chess Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    mode, difficulty, side = menu(screen, font)
    ai_depth = {"Easy": 1, "Medium": 2, "Hard": 3}[difficulty]
    
    move_sound = create_sound(440, 50)
    capture_sound = create_sound(330, 80)
    
    state = GameState()
    imgs = load_images()
    selected = None
    valid_moves = []
    user_is_white = (side == "White")
    vs_ai = (mode == "Player vs Computer")
    
    animating = False
    anim_piece = None
    anim_from = None
    anim_to = None
    anim_progress = 0
    
    game_over = False
    result_text = ""
    
    running = True
    while running:
        clock.tick(FPS)
        
        if animating:
            anim_progress += ANIMATION_SPEED
            if anim_progress >= SQ_SIZE:
                animating = False
                anim_piece = None
        
        if not game_over and vs_ai and state.white_turn != user_is_white and not animating:
            _, move = minimax(state, ai_depth, -99999, 99999, state.white_turn)
            if move:
                from_pos, to_pos = move
                
                if state.board[to_pos[0]][to_pos[1]] != '.':
                    if capture_sound:
                        capture_sound.play()
                else:
                    if move_sound:
                        move_sound.play()
                
                animating = True
                anim_from = from_pos
                anim_to = to_pos
                anim_piece = state.board[from_pos[0]][from_pos[1]]
                anim_progress = 0
                
                state = make_move(state, from_pos, to_pos)
                
                if is_checkmate(state):
                    game_over = True
                    result_text = "White wins!" if not state.white_turn else "Black wins!"
                elif is_stalemate(state):
                    game_over = True
                    result_text = "Stalemate!"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    continue
                if animating:
                    continue
                if vs_ai and state.white_turn != user_is_white:
                    continue
                
                r, c = coords_to_square(pygame.mouse.get_pos())
                if not in_bounds(r, c):
                    continue
                
                piece = state.board[r][c]
                
                if piece != '.' and is_white(piece) == state.white_turn:
                    selected = (r, c)
                    valid_moves = get_legal_moves(state, r, c)
                elif selected and (r, c) in valid_moves:
                    from_pos = selected
                    to_pos = (r, c)
                    
                    if state.board[to_pos[0]][to_pos[1]] != '.':
                        if capture_sound:
                            capture_sound.play()
                    else:
                        if move_sound:
                            move_sound.play()
                    
                    animating = True
                    anim_from = from_pos
                    anim_to = to_pos
                    anim_piece = state.board[from_pos[0]][from_pos[1]]
                    anim_progress = 0
                    
                    state = make_move(state, from_pos, to_pos)
                    selected = None
                    valid_moves = []
                    
                    if is_checkmate(state):
                        game_over = True
                        result_text = "White wins!" if not state.white_turn else "Black wins!"
                    elif is_stalemate(state):
                        game_over = True
                        result_text = "Stalemate!"
                else:
                    selected = None
                    valid_moves = []
        
        draw_board(screen)
        
        if state.last_move and not animating:
            highlight_squares(screen, [state.last_move[0], state.last_move[1]], MOVE_HIGHLIGHT)
        
        if selected and not animating:
            highlight_squares(screen, [selected] + valid_moves)
        
        if is_in_check(state.board, state.white_turn):
            king_pos = find_king(state.board, state.white_turn)
            if king_pos:
                highlight_squares(screen, [king_pos], CHECK_HIGHLIGHT)
        
        draw_pieces(screen, state.board, imgs, {'from': anim_from} if animating else None)
        
        if animating and anim_piece and anim_from and anim_to:
            from_x, from_y = anim_from[1] * SQ_SIZE, anim_from[0] * SQ_SIZE
            to_x, to_y = anim_to[1] * SQ_SIZE, anim_to[0] * SQ_SIZE
            progress_ratio = anim_progress / SQ_SIZE
            current_x = from_x + (to_x - from_x) * progress_ratio
            current_y = from_y + (to_y - from_y) * progress_ratio
            screen.blit(imgs[anim_piece], (current_x, current_y))
        
        status = "White" if state.white_turn else "Black"
        if is_in_check(state.board, state.white_turn):
            status += " - CHECK!"
        status_text = small_font.render(status, True, (255, 255, 255))
        status_bg = pygame.Surface((status_text.get_width() + 20, status_text.get_height() + 10))
        status_bg.fill((0, 0, 0))
        status_bg.set_alpha(180)
        screen.blit(status_bg, (10, 10))
        screen.blit(status_text, (20, 15))
        
        if game_over:
            result_surface = font.render(result_text, True, (255, 255, 255))
            bg = pygame.Surface((result_surface.get_width() + 40, result_surface.get_height() + 20))
            bg.fill((0, 0, 0))
            bg.set_alpha(200)
            bg_x = BOARD_SIZE // 2 - bg.get_width() // 2
            bg_y = BOARD_SIZE // 2 - bg.get_height() // 2
            screen.blit(bg, (bg_x, bg_y))
            screen.blit(result_surface, (bg_x + 20, bg_y + 10))
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
