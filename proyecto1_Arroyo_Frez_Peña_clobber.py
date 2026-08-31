#Nombres: Ian Arroyo | Patricio Frez | Andrés Peña
#Rut: 21906291-5 | 21473128-2 | 22059517-K
#NRC: 8328

from proyecto1_Arroyo_Frez_Peña_tablero import Board


class Clobber(Board):
    __jugadorA: str
    __jugadorB: str

    def __init__(self, tamano, jugador_a: str = "A", jugador_b: str = "B"):
        if tamano < 4 or tamano % 2 != 0:
            raise ValueError("El tamaño del tablero debe ser un número par mayor o igual a 4.")
        super().__init__(tamano)
        self.__jugadorA = jugador_a
        self.__jugadorB = jugador_b

    def jugada(self, f: int, c: int, x: int, y: int) -> bool:
        if self[f, c] == "A":
            if self.valid_move(f, c, x, y, self[f, c]):
                self[x, y] = self.__jugadorA
                self[f, c] = "·"
                return True
            return False

        elif self[f, c] == "B":
            if self.valid_move(f, c, x, y, self[f, c]):
                self[x, y] = self.__jugadorB
                self[f, c] = "·"
                return True
            return False

        return False

    def valid_move(self, f, c, x, y, color):
        diff = [f - x, c - y]
        valid_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        if diff in valid_moves:
            if color == "A":
                return self[x, y] == "B"
            elif color == "B":
                return self[x, y] == "A"
        return False

    def hay_movimientos(self):
        tamano = len(self)
        for f in range(1, tamano + 1):
            for c in range(1, tamano + 1):
                ficha_actual = self[f, c]

                # Ignoramos los espacios vacios
                if ficha_actual not in ("A", "B"):
                    continue

                # Revisamos las 4 direcciones validas
                validos = [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]

                for x, y in validos:
                    try:
                        # Revisamos jugadas validas para el jugador A y B
                        if self[f, c] == "A":
                            if self[x, y] == "B":
                                return True

                        if self[f, c] == "B":
                            if self[x, y] == "A":
                                return True

                    except LookupError:
                        pass
        return False

