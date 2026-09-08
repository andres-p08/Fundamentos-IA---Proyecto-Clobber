from math import inf
import copy


def movimientosPosibles(tablero, jugador, mostrar_conteo=False):
    """Devuelve las jugadas legales de jugador en el estado actual."""
    movimientos = []
    tamano = len(tablero)
    enemigo = "B" if jugador == "A" else "A"
    for f in range(1, tamano + 1):
        for c in range(1, tamano + 1):
            if tablero[f, c] == jugador:
                # Una jugada solo puede capturar una ficha enemiga adyacente.
                validos = [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]
                for x, y in validos:
                    try:
                        if tablero[x, y] == enemigo:
                            movimientos.append((f, c, x, y))
                    except LookupError:
                        pass

    # Se imprime una sola vez por intento del agente, no una vez por ficha.
    if mostrar_conteo:
        print(f"Jugadas posibles para el agente B: {len(movimientos)}")
    return movimientos

def evaluar(tablero):
    """Estima el estado: B busca más opciones y A busca reducirlas."""
    movimientos_b = movimientosPosibles(tablero, "B")
    movimientos_a = movimientosPosibles(tablero, "A")
    return len(movimientos_b) - len(movimientos_a)


def alfa_beta(tablero, profundidad, turno_agente, alfa=-inf, beta=inf):
    """Minimax con poda alfa-beta desde la perspectiva del jugador B."""
    jugador_actual = "B" if turno_agente else "A"
    movimientos = movimientosPosibles(tablero, jugador_actual)

    # No tener jugadas en el propio turno significa perder la partida.
    if not movimientos:
        return 100000 + profundidad if turno_agente else -100000 - profundidad

    # En este punto no conocemos el resultado final, así que usamos una
    # evaluación aproximada para limitar el árbol a la profundidad indicada.
    if profundidad <= 0:
        return evaluar(tablero)

    if turno_agente:
        mejor_puntaje = -inf
        for movimiento in movimientos:
            simulacion = copy.deepcopy(tablero)
            simulacion.jugada(*movimiento)
            puntaje = alfa_beta(simulacion, profundidad - 1, False, alfa, beta)
            mejor_puntaje = max(mejor_puntaje, puntaje)
            alfa = max(alfa, mejor_puntaje)

            # Si beta ya no puede mejorar esta rama, no hace falta explorarla.
            if alfa >= beta:
                break
        return mejor_puntaje

    mejor_puntaje = inf
    for movimiento in movimientos:
        simulacion = copy.deepcopy(tablero)
        simulacion.jugada(*movimiento)
        puntaje = alfa_beta(simulacion, profundidad - 1, True, alfa, beta)
        mejor_puntaje = min(mejor_puntaje, puntaje)
        beta = min(beta, mejor_puntaje)

        # Poda simétrica para el turno del jugador A, que minimiza el puntaje.
        if alfa >= beta:
            break
    return mejor_puntaje


def miniMax(tablero, profundidad, agente, jugador_max="B"):
    """Mantiene la interfaz anterior usando ahora alfa-beta con poda."""
    return alfa_beta(tablero, profundidad, agente)

def mejorMovimiento(tablero, profundidad=3):
    mejor_puntaje = -inf
    movimiento_optimo = None

    # Este es el único conteo visible: representa las alternativas reales
    # que tiene B en el intento actual, no las ramas internas del árbol.
    movimientos = movimientosPosibles(tablero, "B", mostrar_conteo=True)

    for movimiento in movimientos:
        simulacion = copy.deepcopy(tablero)
        simulacion.jugada(*movimiento)
        puntaje = alfa_beta(simulacion, profundidad - 1, False)

        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            movimiento_optimo = movimiento

    return movimiento_optimo