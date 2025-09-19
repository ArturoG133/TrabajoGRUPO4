    import pygame
import sys
import os

# Inicializar pygame
pygame.init()
pygame.mixer.init()

# Dimensiones de la ventana
ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego RPG Peruano - USMP FIA")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# ----------------------
# Manejo de rutas de assets
# ----------------------
if "__file__" in globals():
    BASE_DIR = os.path.dirname(__file__)
else:
    BASE_DIR = os.getcwd()

RUTA_ASSETS = os.path.join(BASE_DIR, "assets")

if not os.path.isdir(RUTA_ASSETS):
    print("Atención: no se encontró la carpeta 'assets' en:", RUTA_ASSETS)

# ----------------------
# Fuentes
# ----------------------
# Fuente para botones y textos secundarios
fuente = pygame.font.SysFont("Arial", 40)

# Fuente personalizada para el título
ruta_font = os.path.join(RUTA_ASSETS, "LetraPantallaInicial.otf")  # usa .otf si tu fuente es OpenType
if os.path.isfile(ruta_font):
    fuente_titulo = pygame.font.Font(ruta_font, 60)
else:
    print("Fuente personalizada no encontrada en:", ruta_font, "\nUsando fuente por defecto.")
    fuente_titulo = pygame.font.SysFont("Arial", 60)

# ----------------------
# Fondo
# ----------------------
fondo = pygame.image.load(os.path.join(RUTA_ASSETS, "fondo.png")).convert()
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# ----------------------
# Música de fondo
# ----------------------
try:
    pygame.mixer.music.load(os.path.join(RUTA_ASSETS, "MusicPantallaPrincipal.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # bucle infinito
except Exception as e:
    print("No se pudo cargar la música:", e)

# ----------------------
# Botón con imagen
# ----------------------
imagen_boton = pygame.image.load(os.path.join(RUTA_ASSETS, "IconoIniciar.png")).convert_alpha()

# Escalar el botón (de 64x64 px → 200x80 px en pantalla)
imagen_boton = pygame.transform.scale(imagen_boton, (200, 140))

# Rect para centrarlo debajo del título
boton_rect = imagen_boton.get_rect(center=(ANCHO//2, ALTO//2))

# ----------------------
# Funciones de dibujo
# ----------------------
def dibujar_pantalla_inicio():
    ventana.blit(fondo, (0, 0))

    # Título del juego
    titulo = fuente_titulo.render("MULLAKA", True, NEGRO)
    ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 150))

    # Botón como imagen
    ventana.blit(imagen_boton, boton_rect)

    pygame.display.flip()

# ----------------------
# Pantalla de inicio
# ----------------------
def pantalla_inicio():
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_rect.collidepoint(evento.pos):
                    print("Iniciar partida...")
                    return  # Aquí pasas al juego principal

        dibujar_pantalla_inicio()

# Ejecutar la pantalla de inicio
pantalla_inicio()

# Aquí después vendría tu bucle principal del juego

