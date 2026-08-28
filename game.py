from clobber import Clobber
if __name__ == "__main__":
    tamano = int(input("Tamaño n del tablero: "))
    tablero = Clobber(tamano)
    turno = "A"
    ganador = ""
    hay_movimientos = True
    while True:
        print(tablero)
        print(f"Turno del jugador {turno}: ")

        # Verificamos si hay movimientos disponibles
        if not tablero.hayMovimientos():
            print(f"El jugador {turno} no tiene mas movimientos")
            break
        print("Escoja la ficha")
        f = int(input("Fila: "))
        c = int(input("Columna: "))

        # Validamos si escogio una ficha valida
        try:
            ficha_seleccionada = tablero[f, c]
        except LookupError:
            print("Coordenadas fuera de rango. Intente de nuevo.\n")
            continue
        if ficha_seleccionada != turno:
            print(f"Solo puedes mover las fichas '{turno}'. Intente de nuevo.\n")
            continue
        x = int(input("\nHaga el movimiento\nFila: "))
        y = int(input("Columna: "))

        # Se realiza la jugada y pasa el siguiente turno
        if tablero.jugada(f, c, x, y):
            ganador = turno
            
            turno = "B" if turno == "A" else "A"
        else:
            print("Movimiento inválido. Intente de nuevo.\n")

# Se muestra el resultado final
print(tablero)
print(f"Gana el jugador {ganador}")