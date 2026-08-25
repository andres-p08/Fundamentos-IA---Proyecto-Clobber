import math


class Board:
    __places: list[list[str]]  # Tablero en sí
    __size: int  # Tamaño del tablero
    
    def __init__(self, n):
        """Crea un tablero"""
        self.__places = []
        for i in range(n):
            fila = []
            for j in range(n):
                if (i + j) % 2 == 0:
                    fila.append("A")
                else:
                    fila.append("B")
            self.__places.append(fila)
            
        self.__size = n

    def __str__(self) -> str:
        """Función que es llamada cuando se hace str(self)"""
        # Cantidad de caracteres para la columna con número de fila
        offset = math.ceil(math.log10(self.__size))
        # Primera línea
        board = " "*offset + " "
        board += " ".join(chr(ord('A') + i) for i in range(self.__size)) + "\n"
        for i, line in enumerate(self.__places, 1):
            # Falta arreglar el ancho del primer número
            board += f"{i} " + " ".join(line) + '\n'
        return board

    def __repr__(self) -> str:
        """Función para cuando se llama repr(self)"""
        return f"Board({self.__size})"

    def __len__(self) -> int:
        """Función para cuando se llama len(self)"""
        return self.__size

    def __check_valid_range(self, r: int) -> bool:
        """Valida que el valor esté dentro del rango del tablero
        
        Esto considera que las posiciones van de 1 a n
        """
        # Nombre con dos guiones bajos al inicio se interpreta como privada
        # En relidad, Python le cambia internamente el nombre, porque no tiene
        # el concepto real de atributo o método privado
        if 1 > r or r > self.__size:
            return False
        return True

    def __getitem__(self, subscript: int | tuple):
        """Implementa self[subscript]
        
        En este caso, `subscript` puede ser un entero (fila) o una tupla
        (coordenadas).
        
        Levanta excepciones, si no se usa bien.
        """
        if isinstance(subscript, tuple):
            # Si es una tupla
            # Si son más o menos que filas y columnas
            if len(subscript) != 2:
                raise ValueError("Cooordinates with too many dimensions")
            # Si la fila está fuera de rangoo
            if not self.__check_valid_range(subscript[0]):
                raise LookupError(f"Row out of range: {subscript[0]}")
            # Si la columna está fuera de rango
            if not  self.__check_valid_range(subscript[1]):
                raise LookupError(f"Column out of range: {subscript[1]}")
            return self.__places[subscript[0] - 1][subscript[1] - 1]
        elif isinstance(subscript, int):
            # Si es un entero
            if not self.__check_valid_range(subscript):
                raise LookupError(f"Row out of range: {subscript}")
            return self.__places[subscript - 1]
        else:
            # Si el índice no es del tipo correcto
            raise TypeError("Subscript must be integer or coordinates")
    
    def __setitem__(self, key: tuple, value: str) ->  None:
        """Implementa self[key] = value
        
        El "índice" `key` tiene que ser un par de coordenadas
        """
        if not isinstance(key, tuple):
            raise TypeError(f"Subscript must be coordinates (tuple), not {type(key)}")
        if len(key) != 2:
            raise ValueError("Cooordinates with too many dimensions")
        # Si la fila está fuera de rangoo
        if not self.__check_valid_range(key[0]):
            raise LookupError(f"Row out of range: {key[0]}")
        # Si la columna está fuera de rango
        if not  self.__check_valid_range(key[1]):
            raise LookupError(f"Column out of range: {key[1]}")
        self.__places[key[0] - 1][key[1] - 1] = value