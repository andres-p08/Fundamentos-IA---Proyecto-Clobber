from clobber import Clobber
if __name__ == "__main__":
    tamano = int(input("Tamaño n del tablero: "))
    tablero = Clobber(tamano)
    while True:
        print(tablero)
        print("Turno del jugador A: ")
        tablero.jugadaA(int(input("Eje x: ")), int(input("Eje y: ")))
        print(tablero)
        print("Turno del jugador B: ")
        tablero.jugadaB(int(input("Eje x: ")), int(input("Eje y: ")))