from board import Board
class Clobber(Board):
    __jugadorA:  str
    __jugadorB:  str

    def __init__(self, tamano, jugadorA: str = "A", jugadorB: str = "B"):
        super().__init__(tamano)
        self.__jugadorA = jugadorA
        self.__jugadorB = jugadorB

    def pedirTamano(self):
        self.tamano = int(input("Tamaño n del tablero: "))

    def jugadaA(self, r: int, c: int) -> bool:
        if self.valid_moveA(r, c):
            self[r, c] = self.__jugadorA
            return True
        else:
            return False

    def jugadaB(self, r:int, c:int):
        if self.valid_moveB(r, c):
            self[r, c] = self.__jugadorB
            return True
        else:
            return False

    def valid_moveA(self, r, c):
        return self[r, c] == "B"

    def valid_moveB(self, r, c):
            return self[r, c] == "A"