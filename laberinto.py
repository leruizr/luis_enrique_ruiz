import sys
import time

import pygame

# Representacion del laberinto: 1 = pared, 0 = camino libre, S = entrada, E = salida.
MAZE_LAYOUT = [
    "111111111111111",
    "1S0001101110011",
    "111101101011101",
    "101100000001101",
    "101011101101011",
    "110000000001101",
    "100111011010111",
    "110100101011001",
    "110111100011101",
    "110000000000011",
    "101110111011001",
    "100010101011011",
    "111010111011001",
    "1010001010110E1",
    "111111111111111",
]

CELL_SIZE = 32
FPS = 60

COLOR_BG = (18, 18, 18)
COLOR_WALL = (60, 60, 60)
COLOR_PATH = (24, 24, 24)
COLOR_ENTRY = (20, 150, 20)
COLOR_EXIT = (200, 180, 40)
COLOR_PLAYER = (50, 140, 255)
COLOR_TEXT = (230, 230, 230)


def _buscar_puntos(layout):
    """Encuentra las coordenadas (col, fila) de la entrada y la salida."""
    entrada = None
    salida = None
    for fila, line in enumerate(layout):
        for col, cell in enumerate(line):
            if cell == "S":
                entrada = (col, fila)
            elif cell == "E":
                salida = (col, fila)
    if entrada is None or salida is None:
        raise ValueError("El laberinto debe tener una entrada 'S' y una salida 'E'.")
    return entrada, salida


def _es_camino(layout, col, fila):
    """Devuelve True si la celda es transitable (camino, entrada o salida)."""
    if fila < 0 or fila >= len(layout):
        return False
    if col < 0 or col >= len(layout[0]):
        return False
    return layout[fila][col] in {"0", "S", "E"}


def _dibujar_mapa(screen, layout, fuente):
    for fila, line in enumerate(layout):
        for col, cell in enumerate(line):
            x = col * CELL_SIZE
            y = fila * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if cell == "1":
                pygame.draw.rect(screen, COLOR_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_PATH, rect)
                if cell == "S":
                    pygame.draw.rect(screen, COLOR_ENTRY, rect)
                elif cell == "E":
                    pygame.draw.rect(screen, COLOR_EXIT, rect)
    # Borde opcional de referencia
    info = fuente.render("Usa flechas para moverte", True, COLOR_TEXT)
    screen.blit(info, (10, 8))


def jugar_laberinto():
    """
    Ejecuta el minijuego del laberinto y devuelve el control al menu
    cuando la ventana se cierra o el jugador llega a la salida.
    """
    entrada, salida = _buscar_puntos(MAZE_LAYOUT)

    pygame.init()
    clock = pygame.time.Clock()
    ancho = len(MAZE_LAYOUT[0]) * CELL_SIZE
    alto = len(MAZE_LAYOUT) * CELL_SIZE
    screen = pygame.display.set_mode((ancho, alto))
    pygame.display.set_caption("Laberinto - Pygame")
    fuente = pygame.font.SysFont(None, 24)

    # El jugador arranca centrado en la celda de entrada.
    jugador_col, jugador_fila = entrada
    jugador_rect = pygame.Rect(
        jugador_col * CELL_SIZE + 6,
        jugador_fila * CELL_SIZE + 6,
        CELL_SIZE - 12,
        CELL_SIZE - 12,
    )

    inicio_tiempo = None  # Se activa en el primer movimiento válido.
    tiempo_total = None
    en_juego = True

    while en_juego:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                dx = dy = 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                if dx or dy:
                    nuevo_col = jugador_col + dx
                    nuevo_fila = jugador_fila + dy
                    if _es_camino(MAZE_LAYOUT, nuevo_col, nuevo_fila):
                        if inicio_tiempo is None:
                            inicio_tiempo = time.time()
                        jugador_col, jugador_fila = nuevo_col, nuevo_fila
                        jugador_rect.x = jugador_col * CELL_SIZE + 6
                        jugador_rect.y = jugador_fila * CELL_SIZE + 6
                        if (jugador_col, jugador_fila) == salida:
                            tiempo_total = time.time() - inicio_tiempo
                            en_juego = False
                            break

        screen.fill(COLOR_BG)
        _dibujar_mapa(screen, MAZE_LAYOUT, fuente)
        pygame.draw.rect(screen, COLOR_PLAYER, jugador_rect, border_radius=6)
        pygame.display.flip()
        clock.tick(FPS)

    # Mensaje final y pequena pausa antes de cerrar.
    if tiempo_total is None:
        tiempo_total = 0.0
    screen.fill(COLOR_BG)
    _dibujar_mapa(screen, MAZE_LAYOUT, fuente)
    msg = f"Has llegado a la salida. Tiempo: {tiempo_total:.2f} s"
    texto = fuente.render(msg, True, COLOR_TEXT)
    screen.blit(texto, (10, alto // 2 - 12))
    pygame.display.flip()
    pygame.time.delay(2500)
    pygame.quit()
    # Regreso al menú (main.py seguirá ejecutándose).


if __name__ == "__main__":
    # Permite ejecutar el módulo en solitario para pruebas rápidas.
    try:
        jugar_laberinto()
    except Exception as exc:
        print(f"Error al ejecutar el laberinto: {exc}", file=sys.stderr)
