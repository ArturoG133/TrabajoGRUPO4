import pygame, sys, os

# ===================== Config "8-bit" =====================
SCALE = 4
GAME_W, GAME_H = 160, 144            # Resolución lógica retro
WIN_W, WIN_H = GAME_W * SCALE, GAME_H * SCALE
FPS = 60

# Rutas de tus archivos (ajusta si los renombraste)
BG_PATH = "fondo.png"       # Fondo que enviaste antes
SHEET_PATH = "runner_sheet.png"    # Frames del personaje (spritesheet)

# Fondo
SCROLL_BG = True
BG_SPEED = 1                         # píxeles lógicos por frame (1–2 retro)
USE_MIRROR_TILE = True               # True: fondo se repite con espejo para disimular cortes

# Runner / animación
RUNNER_TARGET_H = 24                 # altura del personaje en píxeles lógicos (8-bit look)
ANIM_FPS = 10                        # velocidad de animación (frames/segundo)
RUNNER_X = 40
GROUND_MARGIN = 12

# Slicing inicial (ajustable en vivo con teclas)
SHEET_ROWS = 1
SHEET_COLS = 6                       # prueba inicial; ajusta con W/S/A/D

# ====================== Inicialización ====================
pygame.init()
clock = pygame.time.Clock()
game_surf = pygame.Surface((GAME_W, GAME_H))
window = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Runner 8-bit (tu fondo + tu sprite)")

# ====================== Utilidades ========================
def load_image(path, alpha=True):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró '{path}'. Coloca el archivo junto a main.py.")
    img = pygame.image.load(path)
    return img.convert_alpha() if alpha else img.convert()

def scale_to_height(img, target_h):
    w, h = img.get_size()
    new_w = max(1, int(round(w * (target_h / h))))
    return pygame.transform.scale(img, (new_w, target_h))

def nearest_scale(surf, size):
    # pygame.transform.scale usa 'nearest' (sin suavizado) por defecto
    return pygame.transform.scale(surf, size)

# -------------------- Fondo (tile o tile espejo) --------------------
def prepare_background_tile():
    """Carga el fondo, lo ajusta por altura y crea un tile (opcional espejo) para scroll infinito."""
    bg = load_image(BG_PATH, alpha=False)
    factor = GAME_H / bg.get_height()
    new_w = max(1, int(round(bg.get_width() * factor)))
    bg = pygame.transform.scale(bg, (new_w, GAME_H))

    if USE_MIRROR_TILE:
        bg_flip = pygame.transform.flip(bg, True, False)
        tile_w = bg.get_width() * 2
        tile = pygame.Surface((tile_w, GAME_H)).convert()
        tile.blit(bg, (0, 0))
        tile.blit(bg_flip, (bg.get_width(), 0))
    else:
        # Tile simple (una imagen que se repite)
        tile = bg
    return tile

# -------------------- Slicing del spritesheet --------------------
def slice_grid(sheet, rows, cols):
    """Corta la hoja en una grilla rows x cols (sin márgenes/espaciado)."""
    rows = max(1, rows)
    cols = max(1, cols)
    sw, sh = sheet.get_size()
    fw = sw // cols
    fh = sh // rows
    frames = []
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * fw, r * fh, fw, fh)
            # copy() para desacoplar el subsurface
            frame = sheet.subsurface(rect).copy()
            frames.append(frame)
    return frames

def build_runner_frames(sheet, rows, cols, target_h):
    raw_frames = slice_grid(sheet, rows, cols)
    scaled = [scale_to_height(f, target_h) for f in raw_frames]
    return scaled

# -------------------- Main --------------------
def main():
    global SHEET_ROWS, SHEET_COLS, ANIM_FPS, RUNNER_TARGET_H, USE_MIRROR_TILE, SCROLL_BG

    font = pygame.font.SysFont("Courier", 8, bold=True)

    # Cargar fondo
    try:
        bg_tile = prepare_background_tile()
    except Exception as e:
        print(e)
        pygame.quit()
        sys.exit(1)

    # Cargar spritesheet del runner
    runner_sheet = None
    try:
        # Si tu archivo es PNG con transparencia, mejor: el loader maneja alpha.
        # Para JPG funcionará igual pero sin transparencia.
        runner_sheet = load_image(SHEET_PATH, alpha=True)
    except Exception as e:
        print(e)
        pygame.quit()
        sys.exit(1)

    def rebuild_frames():
        return build_runner_frames(runner_sheet, SHEET_ROWS, SHEET_COLS, RUNNER_TARGET_H)

    runner_frames = rebuild_frames()
    if not runner_frames:
        print("No se pudieron crear frames desde el spritesheet.")
        pygame.quit()
        sys.exit(1)

    tile_w = bg_tile.get_width()
    bg_x = 0
    runner_y = GAME_H - RUNNER_TARGET_H - GROUND_MARGIN
    start_ticks = pygame.time.get_ticks()
    paused_scroll = not SCROLL_BG

    running = True
    while running:
        dt_ms = clock.tick(FPS)

        # ---------- Input ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_a, pygame.K_LEFT):   # -cols
                    SHEET_COLS = max(1, SHEET_COLS - 1)
                    runner_frames = rebuild_frames()
                    start_ticks = pygame.time.get_ticks()
                elif event.key in (pygame.K_d, pygame.K_RIGHT):  # +cols
                    SHEET_COLS = min(24, SHEET_COLS + 1)
                    runner_frames = rebuild_frames()
                    start_ticks = pygame.time.get_ticks()
                elif event.key in (pygame.K_w, pygame.K_UP):     # -rows
                    SHEET_ROWS = max(1, SHEET_ROWS - 1)
                    runner_frames = rebuild_frames()
                    start_ticks = pygame.time.get_ticks()
                elif event.key in (pygame.K_s, pygame.K_DOWN):   # +rows
                    SHEET_ROWS = min(12, SHEET_ROWS + 1)
                    runner_frames = rebuild_frames()
                    start_ticks = pygame.time.get_ticks()
                elif event.key == pygame.K_q:                    # -anim fps
                    ANIM_FPS = max(2, ANIM_FPS - 1)
                elif event.key == pygame.K_e:                    # +anim fps
                    ANIM_FPS = min(30, ANIM_FPS + 1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):  # -altura
                    RUNNER_TARGET_H = max(10, RUNNER_TARGET_H - 1)
                    runner_frames = rebuild_frames()
                    runner_y = GAME_H - RUNNER_TARGET_H - GROUND_MARGIN
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):  # +altura
                    RUNNER_TARGET_H = min(40, RUNNER_TARGET_H + 1)
                    runner_frames = rebuild_frames()
                    runner_y = GAME_H - RUNNER_TARGET_H - GROUND_MARGIN
                elif event.key == pygame.K_SPACE:               # pausar/continuar scroll
                    paused_scroll = not paused_scroll
                elif event.key == pygame.K_f:                   # alternar espejo del fondo
                    USE_MIRROR_TILE = not USE_MIRROR_TILE
                    bg_tile = prepare_background_tile()
                    tile_w = bg_tile.get_width()
                    bg_x = 0

        # ---------- Update ----------
        if not paused_scroll:
            bg_x -= BG_SPEED
            while bg_x <= -tile_w:
                bg_x += tile_w

        # Animación por tiempo
        t = pygame.time.get_ticks() - start_ticks
        frame_index = (t // max(1, (1000 // ANIM_FPS))) % len(runner_frames)
        runner_img = runner_frames[frame_index]

        # ---------- Draw (baja resolución) ----------
        game_surf.fill((16, 24, 32))

        # Fondo: repetir tile las veces necesarias para cubrir pantalla lógica
        repeats = (GAME_W // tile_w) + 3
        for i in range(repeats):
            x = bg_x + i * tile_w
            game_surf.blit(bg_tile, (x, 0))

        # Suelo simple
        pygame.draw.line(game_surf, (80, 96, 112),
                         (0, GAME_H - GROUND_MARGIN), (GAME_W, GAME_H - GROUND_MARGIN))

        # Runner
        game_surf.blit(runner_img, (RUNNER_X, runner_y))

        # HUD (ayuda)
        hud1 = f"Filas: {SHEET_ROWS}  Cols: {SHEET_COLS}  Frames: {SHEET_ROWS*SHEET_COLS}"
        hud2 = f"AnimFPS: {ANIM_FPS}  Altura: {RUNNER_TARGET_H}px   (W/S rows, A/D cols, Q/E fps, +/- altura)"
        hud3 = f"Fondo: {'Espejo' if USE_MIRROR_TILE else 'Normal'}  Scroll: {'ON' if not paused_scroll else 'PAUSA'}  [F alterna, ESP pausa]"
        game_surf.blit(font.render(hud1, True, (120, 200, 160)), (4, 4))
        game_surf.blit(font.render(hud2, True, (200, 180, 80)), (4, 14))
        game_surf.blit(font.render(hud3, True, (150, 160, 220)), (4, 24))

        # Escalar a ventana (nearest)
        frame = nearest_scale(game_surf, (WIN_W, WIN_H))
        window.blit(frame, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

