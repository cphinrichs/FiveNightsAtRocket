# Simple Checkers game with click and drag using pygame
# Pygbag-compatible version with async/await
import pygame
import asyncio

# Constants
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# Board setup
def create_board():
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                if row < 3:
                    board[row][col] = 'b'  # Black piece
                elif row > 4:
                    board[row][col] = 'r'  # Red piece
    return board

def draw_board(win, board, dragging_piece=None, dragging_pos=None):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            color = GRAY if (row + col) % 2 == 1 else WHITE
            pygame.draw.rect(win, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board[row][col]
            if piece and (dragging_piece != (row, col)):
                center = (col*SQUARE_SIZE + SQUARE_SIZE//2, row*SQUARE_SIZE + SQUARE_SIZE//2)
                pygame.draw.circle(win, BLACK if piece == 'b' else RED, center, SQUARE_SIZE//2 - 10)
    # Draw dragging piece
    if dragging_piece and dragging_pos:
        r, c = dragging_piece
        piece = board[r][c]
        pygame.draw.circle(win, BLACK if piece == 'b' else RED, dragging_pos, SQUARE_SIZE//2 - 10)
    pygame.display.update()

def get_square(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col
    return None

async def main():
    # Initialize pygame inside the async main function for Pygbag compatibility
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Checkers")
    
    board = create_board()
    dragging = False
    dragging_piece = None
    dragging_pos = None
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square = get_square(pos)
                if square:
                    r, c = square
                    if board[r][c]:
                        dragging = True
                        dragging_piece = (r, c)
                        dragging_pos = pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and dragging_piece:
                    pos = pygame.mouse.get_pos()
                    square = get_square(pos)
                    r0, c0 = dragging_piece
                    if square:
                        r1, c1 = square
                        # Only allow move to empty dark square
                        if board[r1][c1] is None and (r1 + c1) % 2 == 1:
                            board[r1][c1] = board[r0][c0]
                            board[r0][c0] = None
                    dragging = False
                    dragging_piece = None
                    dragging_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dragging_pos = pygame.mouse.get_pos()
        
        draw_board(WIN, board, dragging_piece, dragging_pos)
        clock.tick(60)
        
        # Yield control to the browser event loop (required for Pygbag)
        await asyncio.sleep(0)
    
    pygame.quit()

# Run the async main function
asyncio.run(main())
