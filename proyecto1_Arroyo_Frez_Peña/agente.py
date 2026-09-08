from tablero import Board
from math import inf
from clobber import Clobber
import copy



def movimientosPosibles(tablero, jugador):
    movimientos = []
    tamano = len(tablero)
    enemigo = "B" if jugador == "A" else "A"
    for f in range(1, tamano + 1):
                for c in range(1, tamano + 1):
                    if tablero[f, c] == jugador:

                        # Revisamos las 4 direcciones validas
                        validos = [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]
                        for x, y in validos:
                            try:
                                if tablero[x, y] == enemigo:
                                    movimientos.append((f, c, x, y))
                            except LookupError:
                                    pass
    return movimientos

def miniMax(tablero, profundidad, agente, jugador_max="B"):
    jugador_actual = jugador_max if agente else ("A" if jugador_max == "B" else "B")
    movimientos = movimientosPosibles(tablero, jugador_actual)

    if not movimientos:
        # Si el jugador actual no tiene movimientos, pierde.
        return -1 if agente else 1
    
    #CASOS RECURSIVOS:
    if agente:
        mejorPuntaje = -inf
        for mov in movimientos:
            simulacion = copy.deepcopy(tablero)
            simulacion.jugada(mov[0], mov[1], mov[2], mov[3])
            puntaje = miniMax(simulacion, profundidad - 1, False, jugador_max)
            mejorPuntaje = max(puntaje, mejorPuntaje)
        return mejorPuntaje

    else: # Minimizando (Turno del humano)
        mejorPuntaje = inf
        for mov in movimientos:
            simulacion = copy.deepcopy(tablero)
            simulacion.jugada(mov[0], mov[1], mov[2], mov[3])
            
            puntaje = miniMax(simulacion, profundidad - 1, True, jugador_max)
            mejorPuntaje = min(puntaje, mejorPuntaje)
        return mejorPuntaje

def mejorMovimiento(tablero, profundidad=3):
    mejorPuntaje = -inf
    movimiento_optimo = None
    
    movimientos = movimientosPosibles(tablero, "B")
    
    for mov in movimientos:
        simulacion = copy.deepcopy(tablero)
        simulacion.jugada(mov[0], mov[1], mov[2], mov[3])
        
        puntaje = miniMax(simulacion, profundidad - 1, False, "B")
        
        if puntaje > mejorPuntaje:
            mejorPuntaje = puntaje
            movimiento_optimo = mov

    return movimiento_optimo