#Nombres: Ian Arroyo | Patricio Frez | Andrés Peña
#Rut: 21906291-5 | 21473128-2 | 22059517-K
#NRC: 8328

from proyecto1_Arroyo_Frez_Peña_clobber import Clobber

def pedir_entero(mensaje):
    while True:
        try:
            valor = int(input(mensaje))
            return valor
        except ValueError:
            print("Por favor, ingrese un número entero válido.")

if __name__ == "__main__":
    while True:
        msg = "Tamaño n del tablero (debe ser un número par mayor o igual a 4): "
        tamano = pedir_entero(msg)
        try:
            tablero = Clobber(tamano)
            break
        except ValueError as error:
            print(error)
    turno = "A"
    ganador = ""
    while True:
        print(tablero)
        print(f"Turno del jugador {turno}: ")

        # Verificamos si hay movimientos disponibles
        if not tablero.hay_movimientos():
            msg = f"El jugador {turno} no tiene mas movimientos"
            print(msg)
            break
        print("Escoja la ficha")
        f = pedir_entero("Fila: ")
        c = pedir_entero("columna: ")

        # Validamos si escogio una ficha valida
        try:
            ficha_seleccionada = tablero[f, c]
        except LookupError:
            print("Coordenadas fuera de rango. Intente de nuevo.\n")
            continue
        if ficha_seleccionada != turno:
            msg = f"Solo puedes mover las fichas '{turno}'. Intente de nuevo.\n"
            print(msg)
            continue
        x = pedir_entero("\nHaga el movimiento\nFila: ")
        y = pedir_entero("Columna: ")

        # Se realiza la jugada y pasa el siguiente turno
        try:
            movimiento_valido = tablero.jugada(f, c, x, y)
        except LookupError:
            print("Coordenadas fuera de rango. Intente de nuevo.\n")
            continue
        if movimiento_valido:
            ganador = turno
            turno = "B" if turno == "A" else "A"
        else:
            print("Movimiento inválido. Intente de nuevo.\n")

    # Se muestra el resultado final
    print(tablero)
    print(f"Gana el jugador {ganador}")