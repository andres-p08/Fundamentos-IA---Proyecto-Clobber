"""Agente inteligente para el juego Clobber.

El agente controla al jugador B y utiliza Minimax con poda Alfa-Beta.

La búsqueda no posee límite de profundidad: continúa hasta alcanzar estados
terminales del juego. Por lo tanto, si la búsqueda termina, la acción elegida
corresponde a una acción óptima según Minimax.

La función heurística se utiliza únicamente para ordenar las jugadas antes de
explorarlas. Esto puede mejorar la eficiencia de la poda Alfa-Beta, pero no
modifica el valor Minimax obtenido.
"""

from copy import deepcopy
from math import inf

from clobber import Clobber


# El agente corresponde al jugador MAX.
JUGADOR_AGENTE = Clobber.PLAYER_B

# El humano corresponde al jugador MIN.
JUGADOR_HUMANO = Clobber.PLAYER_A

# Contador utilizado para mostrar cuántos estados fueron revisados.
tableros_revisados = 0


def estimacion(tablero):
    """Calcula una estimación heurística del estado del tablero.

    La función compara la movilidad del agente B con la movilidad del
    jugador A:

        movimientos de B - movimientos de A

    Un valor positivo representa un estado aparentemente favorable para B.
    Un valor negativo representa un estado aparentemente favorable para A.

    Esta estimación NO reemplaza los valores terminales de Minimax.
    Solamente se utiliza para ordenar las jugadas y favorecer podas tempranas.

    Args:
        tablero: Estado actual del juego.

    Returns:
        Diferencia entre la cantidad de movimientos legales de B y A.
    """
    movimientos_agente = len(
        tablero.movimientos_legales(JUGADOR_AGENTE)
    )
    movimientos_humano = len(
        tablero.movimientos_legales(JUGADOR_HUMANO)
    )

    return movimientos_agente - movimientos_humano


def ordenar_movimientos(tablero, jugador, movimientos):
    """Ordena las jugadas usando la función heurística.

    Alfa-Beta obtiene el mismo valor Minimax independientemente del orden en
    que se exploren las jugadas. Sin embargo, un buen orden puede provocar
    podas antes y reducir la cantidad de estados revisados.

    Para B, que es MAX, se exploran primero los estados con mayor estimación.
    Para A, que es MIN, se exploran primero los estados con menor estimación.

    Args:
        tablero: Estado actual del juego.
        jugador: Jugador que realizará los movimientos.
        movimientos: Lista de movimientos legales.

    Returns:
        Lista de movimientos ordenada heurísticamente.
    """
    movimientos_evaluados = []

    for movimiento in movimientos:
        simulacion = deepcopy(tablero)

        simulacion.play(
            *movimiento,
            player=jugador,
        )

        valor = estimacion(simulacion)

        movimientos_evaluados.append(
            (valor, movimiento)
        )

    if jugador == JUGADOR_AGENTE:
        movimientos_evaluados.sort(
            key=lambda elemento: elemento[0],
            reverse=True,
        )
    else:
        movimientos_evaluados.sort(
            key=lambda elemento: elemento[0]
        )

    return [
        movimiento
        for _, movimiento in movimientos_evaluados
    ]


def alfa_beta(tablero, le_toca_al_agente, alfa, beta):
    """Calcula el valor Minimax utilizando poda Alfa-Beta.

    B corresponde al jugador MAX y A al jugador MIN.

    La búsqueda continúa hasta alcanzar estados terminales. En Clobber,
    un jugador pierde si comienza su turno sin movimientos legales.

    Args:
        tablero: Estado actual de Clobber.
        le_toca_al_agente: True si juega B; False si juega A.
        alfa: Mejor valor asegurado hasta ahora para MAX.
        beta: Mejor valor asegurado hasta ahora para MIN.

    Returns:
        1 si B puede forzar una victoria.
        -1 si A puede forzar una victoria.
    """
    global tableros_revisados

    tableros_revisados += 1

    # Se determina qué jugador tiene el turno actual.
    if le_toca_al_agente:
        jugador_actual = JUGADOR_AGENTE
    else:
        jugador_actual = JUGADOR_HUMANO

    movimientos = tablero.movimientos_legales(
        jugador_actual
    )

    # ---------------------------------------------------------------
    # CASO BASE
    # ---------------------------------------------------------------
    # En Clobber, si un jugador comienza su turno sin movimientos
    # legales, pierde inmediatamente.
    #
    # Si B no puede mover:
    #     pierde el agente -> valor -1.
    #
    # Si A no puede mover:
    #     pierde el humano -> gana B -> valor +1.
    # ---------------------------------------------------------------
    if not movimientos:
        if le_toca_al_agente:
            return -1

        return 1

    # La heurística solamente cambia el orden de exploración.
    movimientos = ordenar_movimientos(
        tablero,
        jugador_actual,
        movimientos,
    )

    # ---------------------------------------------------------------
    # CASO RECURSIVO: TURNO DEL AGENTE B -> MAX
    # ---------------------------------------------------------------
    if le_toca_al_agente:
        mejor_puntaje = -inf

        for movimiento in movimientos:
            simulacion = deepcopy(tablero)

            simulacion.play(
                *movimiento,
                player=JUGADOR_AGENTE,
            )

            puntaje = alfa_beta(
                simulacion,
                False,
                alfa,
                beta,
            )

            mejor_puntaje = max(
                puntaje,
                mejor_puntaje,
            )

            alfa = max(
                alfa,
                mejor_puntaje,
            )

            # Si alfa es mayor o igual que beta, las siguientes ramas
            # no pueden modificar la decisión de este nodo.
            if alfa >= beta:
                break

    # ---------------------------------------------------------------
    # CASO RECURSIVO: TURNO DEL HUMANO A -> MIN
    # ---------------------------------------------------------------
    else:
        mejor_puntaje = inf

        for movimiento in movimientos:
            simulacion = deepcopy(tablero)

            simulacion.play(
                *movimiento,
                player=JUGADOR_HUMANO,
            )

            puntaje = alfa_beta(
                simulacion,
                True,
                alfa,
                beta,
            )

            mejor_puntaje = min(
                puntaje,
                mejor_puntaje,
            )

            beta = min(
                beta,
                mejor_puntaje,
            )

            # Si alfa es mayor o igual que beta, las siguientes ramas
            # ya no necesitan ser exploradas.
            if alfa >= beta:
                break

    return mejor_puntaje


def mejor_movimiento(tablero):
    """Busca la mejor jugada disponible para el agente B.

    Cada posible movimiento del agente se prueba sobre una copia del tablero.
    Luego Alfa-Beta analiza las respuestas óptimas de ambos jugadores hasta
    alcanzar estados terminales.

    Args:
        tablero: Estado actual de Clobber.

    Returns:
        Movimiento óptimo para B representado como:
        (fila_origen, columna_origen, fila_destino, columna_destino).

        Retorna None si B no posee movimientos legales.
    """
    global tableros_revisados

    movimientos = tablero.movimientos_legales(
        JUGADOR_AGENTE
    )

    if not movimientos:
        return None

    mejor_puntaje = -inf
    movimiento_elegido = None

    # Reiniciamos el contador para esta decisión del agente.
    tableros_revisados = 0

    movimientos = ordenar_movimientos(
        tablero,
        JUGADOR_AGENTE,
        movimientos,
    )

    for movimiento in movimientos:
        simulacion = deepcopy(tablero)

        simulacion.play(
            *movimiento,
            player=JUGADOR_AGENTE,
        )

        # Después de que B juega, corresponde el turno de A.
        #
        # Igual que en el ejemplo de clases, cada alternativa de la raíz
        # inicia la búsqueda con alfa = -infinito y beta = +infinito.
        puntaje = alfa_beta(
            simulacion,
            False,
            -inf,
            inf,
        )

        print(
            f"Movimiento {movimiento} "
            f"-> valor Minimax: {puntaje}"
        )

        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            movimiento_elegido = movimiento

    print(
        "Número de tableros revisados: "
        f"{tableros_revisados}"
    )

    print(
        "Valor Minimax de la jugada elegida: "
        f"{mejor_puntaje}"
    )

    return movimiento_elegido