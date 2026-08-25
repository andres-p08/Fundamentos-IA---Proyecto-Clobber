from board import Board
class Clobber(Board):
    __jugadorA:  str
    __jugadorB:  str

    VALIDOS = [(1,0),(-1,0),(0,1),(0,-1)]

    def __init__(self, tamano, jugadorA: str = "A", jugadorB: str = "B"):
        super().__init__(tamano)
        self.__jugadorA = jugadorA
        self.__jugadorB = jugadorB

    def pedirTamano(self):
        self.tamano = int(input("Tamaño n del tablero: "))

    def jugadaA(self, f: int, c: int, x: int, y: int) -> bool:
        if self[f, c] == "A":
            if self.valid_moveA(f, c, x, y):
                self[x, y] = self.__jugadorA
                self[f, c] = "·"
                return True
            else:
                return False

    def jugadaB(self, f: int, c: int, x: int, y: int) -> bool:
        if self[f, c] == "B":
            if self.valid_moveB(x, y):
                self[x, y] = self.__jugadorB
                self[f, c] = "·"
                return True
            else:
                return False

    def valid_moveA(self, f, c, x, y):
        if [f-x, c-y] == [1,0] or [f-x, c-y] == [-1,0] or [f-x, c-y] == [0,1] or [f-x, c-y] == [0,-1]:
            return self[x, y] == "B"
        else: 
            return False

    def valid_moveB(self, f, c, x, y):
        if [f-x, c-y] == [1,0] or [f-x, c-y] == [-1,0] or [f-x, c-y] == [0,1] or [f-x, c-y] == [0,-1]:
            return self[x, y] == "A"