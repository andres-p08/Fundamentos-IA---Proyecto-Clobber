from clobber import Clobber
if __name__ == "__main__":
    tamano = int(input("Tamaño n del tablero: "))
    tablero = Clobber(tamano)
    while True:
        print(tablero)
        print("Turno del jugador A: \nEscoja la ficha")
        tablero.jugadaA(int(input("Fila: ")), int(input("Columna: ")), int(input("\nHaga el movimiento\nFila: ")), int(input("Columna: ")))
        print(tablero)
        print("Turno del jugador B: \nEscoja la ficha")
        tablero.jugadaB(int(input("Fila: ")), int(input("Columna: ")), int(input("\nHaga el movimiento\nFila: ")), int(input("Columna: ")))