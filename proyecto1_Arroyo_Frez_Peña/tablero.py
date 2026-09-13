"""Estructura base para representar un tablero cuadrado.

Este módulo contiene solamente responsabilidades generales del tablero:
almacenamiento, validación de coordenadas, lectura, escritura e impresión.
Las reglas específicas de Clobber se implementan en ``clobber.py``.
"""


class Board:
    """Representa un tablero cuadrado indexado desde 1 hasta ``size``."""

    def __init__(self, size: int, fill: str = "·") -> None:
        """Crea un tablero cuadrado de ``size`` por ``size``.

        Args:
            size: Cantidad de filas y columnas del tablero.
            fill: Símbolo utilizado para inicializar cada casilla.

        Raises:
            TypeError: Si ``size`` no es un número entero.
            ValueError: Si ``size`` no es positivo.
        """
        if not isinstance(size, int):
            raise TypeError(
                "El tamaño del tablero debe ser un número entero."
            )
        if size <= 0:
            raise ValueError("El tamaño del tablero debe ser mayor que cero.")

        self._size = size
        self._places = [[fill for _ in range(size)] for _ in range(size)]

    def __str__(self) -> str:
        """Devuelve una representación legible del tablero.

        Las coordenadas se muestran de forma numérica desde 1 hasta ``n``, en
        concordancia con la especificación entregada para el proyecto.
        """
        width = len(str(self._size))
        header = " " * (width + 1)
        header += " ".join(
            f"{column:>{width}}" for column in range(1, self._size + 1)
        )

        rows = [header]
        for row_number, row in enumerate(self._places, start=1):
            cells = " ".join(f"{cell:>{width}}" for cell in row)
            rows.append(f"{row_number:>{width}} {cells}")

        return "\n".join(rows)

    def __repr__(self) -> str:
        """Devuelve una representación útil para depuración."""
        return f"{self.__class__.__name__}(size={self._size})"

    def __len__(self) -> int:
        """Devuelve el tamaño ``n`` de un tablero ``n x n``."""
        return self._size

    def _is_valid_coordinate(self, coordinate: int) -> bool:
        """Indica si una coordenada pertenece al rango válido ``[1, n]``."""
        return isinstance(coordinate, int) and 1 <= coordinate <= self._size

    def _validate_coordinates(self, row: int, column: int) -> None:
        """Valida coordenadas y genera una excepción si son inválidas."""
        if not self._is_valid_coordinate(row):
            raise LookupError(f"Fila fuera de rango: {row}")
        if not self._is_valid_coordinate(column):
            raise LookupError(f"Columna fuera de rango: {column}")

    def __getitem__(self, subscript: int | tuple[int, int]):
        """Permite consultar filas completas o una casilla del tablero.

        Ejemplos:
            ``board[2]`` devuelve la segunda fila.
            ``board[2, 3]`` devuelve la casilla de fila 2, columna 3.
        """
        if isinstance(subscript, tuple):
            if len(subscript) != 2:
                raise ValueError(
                    "Las coordenadas deben contener fila y columna."
                )

            row, column = subscript
            self._validate_coordinates(row, column)
            return self._places[row - 1][column - 1]

        if isinstance(subscript, int):
            if not self._is_valid_coordinate(subscript):
                raise LookupError(f"Fila fuera de rango: {subscript}")
            return self._places[subscript - 1]

        raise TypeError(
            "El índice debe ser un entero o una tupla (fila, columna)."
        )

    def __setitem__(self, key: tuple[int, int], value: str) -> None:
        """Permite modificar una casilla mediante ``board[fila, columna]``."""
        if not isinstance(key, tuple):
            raise TypeError("La posición debe ser una tupla (fila, columna).")
        if len(key) != 2:
            raise ValueError("Las coordenadas deben contener fila y columna.")

        row, column = key
        self._validate_coordinates(row, column)
        self._places[row - 1][column - 1] = value