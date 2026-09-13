"""Interfaz de consola para jugar Clobber contra el agente inteligente.

El jugador humano controla las fichas A y comienza la partida.

El agente controla las fichas B y selecciona sus movimientos utilizando
Minimax con poda Alfa-Beta.
"""

import argparse

import agente
from clobber import Clobber


def leer_argumentos():
    """Lee los parámetros entregados mediante la consola.

    El tamaño del tablero puede indicarse mediante:

        python game.py --size 4

    Si no se entrega el parámetro, el programa lo solicita posteriormente.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Clobber: jugador A contra agente B "
            "con Minimax y poda Alfa-Beta."
        )
    )

    parser.add_argument(
        "--size",
        type=int,
        default=None,
        help=(
            "Tamaño del tablero. Debe ser un número par "
            "mayor o igual a 4."
        ),
    )

    return parser.parse_args()


def pedir_entero(mensaje):
    """Solicita un número entero hasta recibir una entrada válida.

    Args:
        mensaje: Texto mostrado al usuario.

    Returns:
        Número entero ingresado.
    """
    while True:
        try:
            return int(
                input(mensaje)
            )
        except ValueError:
            print(
                "Entrada inválida. "
                "Debe ingresar un número entero."
            )


def pedir_tamano_tablero():
    """Solicita un tamaño válido para el tablero de Clobber.

    Returns:
        Tamaño par mayor o igual a 4.
    """
    while True:
        tamano = pedir_entero(
            "Tamaño del tablero "
            "(par y mayor o igual a 4): "
        )

        try:
            # Se crea temporalmente un tablero para reutilizar la
            # validación implementada en la propia clase Clobber.
            Clobber(tamano)

            return tamano

        except (TypeError, ValueError) as error:
            print(error)


def pedir_movimiento_humano(tablero):
    """Solicita una jugada válida para el jugador humano A.

    Args:
        tablero: Estado actual de Clobber.

    Returns:
        Tupla con:
        (fila_origen, columna_origen, fila_destino, columna_destino).
    """
    while True:
        print(
            "\nSeleccione la ficha A que desea mover."
        )

        fila_origen = pedir_entero(
            "Fila de origen: "
        )
        columna_origen = pedir_entero(
            "Columna de origen: "
        )

        print(
            "\nSeleccione la ficha B que desea capturar."
        )

        fila_destino = pedir_entero(
            "Fila de destino: "
        )
        columna_destino = pedir_entero(
            "Columna de destino: "
        )

        if tablero.is_valid_move(
            fila_origen,
            columna_origen,
            fila_destino,
            columna_destino,
            Clobber.PLAYER_A,
        ):
            return (
                fila_origen,
                columna_origen,
                fila_destino,
                columna_destino,
            )

        print(
            "\nMovimiento inválido. "
            "Intente nuevamente."
        )


def jugar_partida(tamano):
    """Ejecuta una partida completa de Clobber.

    El humano controla A y el agente controla B.

    Args:
        tamano: Tamaño del tablero.

    Returns:
        Símbolo del jugador ganador.
    """
    tablero = Clobber(tamano)

    # De acuerdo con las reglas del proyecto,
    # el jugador A realiza la primera jugada.
    jugador_actual = Clobber.PLAYER_A

    while True:
        print()
        print(tablero)

        print(
            f"Turno del jugador {jugador_actual}."
        )

        # -----------------------------------------------------------
        # CONDICIÓN TERMINAL
        # -----------------------------------------------------------
        # En Clobber pierde el jugador que comienza su turno sin una
        # captura legal.
        # -----------------------------------------------------------
        if not tablero.has_moves(
            jugador_actual
        ):
            ganador = Clobber.opponent(
                jugador_actual
            )

            print(
                f"\nEl jugador {jugador_actual} "
                "no tiene movimientos legales."
            )

            return ganador

        # -----------------------------------------------------------
        # TURNO DEL JUGADOR HUMANO A
        # -----------------------------------------------------------
        if jugador_actual == Clobber.PLAYER_A:
            movimiento = pedir_movimiento_humano(
                tablero
            )

            tablero.play(
                *movimiento,
                player=Clobber.PLAYER_A,
            )

        # -----------------------------------------------------------
        # TURNO DEL AGENTE B
        # -----------------------------------------------------------
        else:
            print(
                "\nEl agente B está buscando "
                "su mejor movimiento..."
            )

            movimiento = agente.mejor_movimiento(
                tablero
            )

            # Esta condición funciona como protección adicional.
            # Normalmente nunca se alcanza porque anteriormente ya
            # verificamos que el jugador tenga movimientos legales.
            if movimiento is None:
                return Clobber.PLAYER_A

            tablero.play(
                *movimiento,
                player=Clobber.PLAYER_B,
            )

            print(
                "\nEl agente B mueve "
                f"({movimiento[0]}, {movimiento[1]}) "
                "-> "
                f"({movimiento[2]}, {movimiento[3]})."
            )

        # Después de una jugada válida cambia el turno.
        jugador_actual = Clobber.opponent(
            jugador_actual
        )


def main():
    """Ejecuta el programa principal."""
    argumentos = leer_argumentos()

    tamano = argumentos.size

    # Si el usuario no indicó --size,
    # se solicita el tamaño mediante teclado.
    if tamano is None:
        tamano = pedir_tamano_tablero()

    try:
        # La clase Clobber valida:
        #
        # n >= 4
        # n par
        Clobber(tamano)

    except (TypeError, ValueError) as error:
        raise SystemExit(
            f"Error de configuración: {error}"
        ) from error

    print(
        "\n=============================="
    )
    print(
        "           CLOBBER"
    )
    print(
        "=============================="
    )

    print(
        f"Tablero: {tamano} x {tamano}"
    )
    print(
        "Jugador humano: A"
    )
    print(
        "Agente Minimax + Alfa-Beta: B"
    )

    ganador = jugar_partida(
        tamano
    )

    print(
        "\n=============================="
    )
    print(
        f"Ganador: jugador {ganador}"
    )
    print(
        "=============================="
    )


if __name__ == "__main__":
    main()