import pygame, sys, os

# ===================== Configuración =====================
WIN_W, WIN_H = 1024, 576         # Tamaño de ventana (ajusta si quieres)
BG_SPEED = 2                     # Velocidad scroll del fondo
ANIM_FPS = 10                    # Velocidad de animación del personaje (frames/seg)
RUNNER_SCALE = 3                 # Escala del personaje (entero)
RUNNER_X = 120                   # Posición X del personaje
GROUND_MARGIN = 60               # Separación al “suelo”

# Archivos (ajusta a tus nombres exactos)
BG_PATH = "fondo.png"   # Tu fondo
SHEET_PATH = "runner_sheet.png"# Tu hoja de frames

# Grid del spritesheet (ajústalo a TU hoja)
ROWS = 1
COLS = 6

# Márgenes y separaciones en el spritesheet (px)
# Si tu hoja tiene espacios alrededor o entre frames, ponlos aquí:
M_TOP, M_RIGHT, M_BOTTOM, M_LEFT = 0, 0, 0, 0
GAP_H, GAP_V = 0, 0  # separación horizontal y vertical entre frames

# =========================================================

pygame.init()
window = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Runner (limpio)")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_image_local(name, alpha=True):
    path = os.path.join(BASE_DIR, name)
    if not os.path.isfile(path):
        # Mensaje claro en consola si no encuentra el archivo
        print("No encontré el archivo:", path)
        print("Estoy corriendo en (CWD):", os.getcwd())
        raise FileNotFoundError(f"Falta el archivo: {name}")
    img = pygame.image.load(path)
    return img.convert_alpha() if alpha else img.convert()

def slice_with_margins(sheet, rows, cols, mt, mr, mb, ml, gap_h, gap_v):
    """Corta una grilla con márgenes y separaciones. Devuelve lista de frames."""
    sw, sh = sheet.get_size()
    rows = max(1, int(rows))
    cols = max(1, int(cols))

    usable_w = sw - ml - mr - (cols - 1) * gap_h
    usable_h = sh - mt - mb - (rows - 1) * gap_v
    fw = usable_w // cols
    fh = usable_h // rows

    frames = []
    # Validaciones para evitar errores de recorte
    if fw <= 0 or fh <= 0:
        print(f"[AVISO] Tamaño de frame inválido: fw={fw}, fh={fh}. Revisa márgenes/gaps/filas/columnas.")
        return frames

    y = mt
    for r in range(rows):
        x = ml
        for c in range(cols):
            rect = pygame.Rect(x, y, fw, fh)
            # Seguridad: que el rect no se salga del sheet
            if rect.right <= sw and rect.bottom <= sh:
                frames.append(sheet.subsurface(rect).copy())
            x += fw + gap_h
        y += fh + gap_v
    if not frames:
        print("[AVISO] No se generaron frames. Revisa la configuración de slicing.")
    return frames

# ---------- Cargar fondo ----------
bg = load_image_local(BG_PATH, alpha=False)
# Ajusta el fondo a la altura de la ventana manteniendo proporción
factor = WIN_H / bg.get_height()
bg = pygame.transform.scale(bg, (max(1, int(bg.get_width() * factor)), WIN_H))
bg_w = bg.get_width()
bg_x = 0

# ---------- Cargar spritesheet y generar frames ----------
sheet = load_image_local(SHEET_PATH, alpha=True)
frames = slice_with_margins(sheet, ROWS, COLS, M_TOP, M_RIGHT, M_BOTTOM, M_LEFT, GAP_H, GAP_V)
if not frames:
    pygame.quit()
    raise SystemExit("No se pudieron crear frames. Ajusta ROWS/COLS/Márgenes/Gaps en el código.")

# Escalar frames al tamaño deseado (RUNNER_SCALE)
fw0, fh0 = frames[0].get_width(), frames[0].get_height()
frames = [pygame.transform.scale(f, (fw0 * RUNNER_SCALE, fh0 * RUNNER_SCALE)) for f in frames]

runner_y = WIN_H - frames[0].get_height() - GROUND_MARGIN
start_ticks = pygame.time.get_ticks()

# ======================= Bucle principal =======================
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # Mover fondo (scroll horizontal)
    bg_x -= BG_SPEED
    if bg_x <= -bg_w:
        bg_x += bg_w

    # Animación por tiempo
    t = pygame.time.get_ticks() - start_ticks
    idx = (t // max(1, (1000 // ANIM_FPS))) % len(frames)

    # Dibujo
    window.fill((0, 0, 0))
    # Fondo repetido
    window.blit(bg, (bg_x, 0))
    window.blit(bg, (bg_x + bg_w, 0))
    # Personaje
    window.blit(frames[idx], (RUNNER_X, runner_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
