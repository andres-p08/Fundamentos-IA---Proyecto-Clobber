"""Lógica y reglas del juego Clobber.

El tablero de Clobber comienza completamente ocupado con fichas A y B en un
patrón alternado. En cada turno, un jugador debe capturar ortogonalmente una
ficha adversaria adyacente. Si al comenzar su turno no tiene capturas legales,
pierde la partida.
"""

from tablero import Board


class Clobber(Board):
    """Implementa el estado y las reglas del juego Clobber."""

    EMPTY = "·"
    PLAYER_A = "A"
    PLAYER_B = "B"
    DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

    def __init__(self, size: int) -> None:
        """Crea la configuración inicial de Clobber.

        Para el proyecto, el tablero debe ser ``n x n``, con ``n`` par y
        ``n >= 4``. La casilla (1, 1) contiene A y las fichas se alternan.

        Args:
            size: Tamaño del tablero.

        Raises:
            TypeError: Si ``size`` no es entero.
            ValueError: Si ``size`` no cumple las restricciones del juego.
        """
        if not isinstance(size, int):
            raise TypeError(
                "El tamaño del tablero debe ser un número entero."
            )
        if size < 4 or size % 2 != 0:
            raise ValueError(
                "El tamaño del tablero debe ser un número par mayor o "
                "igual a 4."
            )

        super().__init__(size, fill=self.EMPTY)
        self._initialize_pieces()

    def _initialize_pieces(self) -> None:
        """Ubica A y B alternadamente en todas las casillas del tablero."""
        for row in range(1, len(self) + 1):
            for column in range(1, len(self) + 1):
                if (row + column) % 2 == 0:
                    self[row, column] = self.PLAYER_A
                else:
                    self[row, column] = self.PLAYER_B

    @classmethod
    def opponent(cls, player: str) -> str:
        """Devuelve el símbolo del adversario de ``player``."""
        if player == cls.PLAYER_A:
            return cls.PLAYER_B
        if player == cls.PLAYER_B:
            return cls.PLAYER_A
        raise ValueError("El jugador debe ser 'A' o 'B'.")

    def is_valid_move(
        self,
        source_row: int,
        source_column: int,
        target_row: int,
        target_column: int,
        player: str | None = None,
    ) -> bool:
        """Indica si un movimiento es una captura legal de Clobber.

        Una jugada legal debe:
        1. partir desde una ficha propia;
        2. desplazarse exactamente una casilla en dirección ortogonal;
        3. terminar sobre una ficha adversaria.

        Args:
            source_row: Fila de origen.
            source_column: Columna de origen.
            target_row: Fila de destino.
            target_column: Columna de destino.
            player: Jugador que intenta mover. Si se omite, se infiere desde
                la casilla de origen.

        Returns:
            ``True`` si la jugada es legal; ``False`` en caso contrario.
        """
        try:
            source_piece = self[source_row, source_column]
            target_piece = self[target_row, target_column]
        except LookupError:
            return False

        if player is None:
            player = source_piece

        if player not in (self.PLAYER_A, self.PLAYER_B):
            return False
        if source_piece != player:
            return False

        row_difference = abs(source_row - target_row)
        column_difference = abs(source_column - target_column)
        is_orthogonally_adjacent = row_difference + column_difference == 1

        return (
            is_orthogonally_adjacent
            and target_piece == self.opponent(player)
        )

    def play(
        self,
        source_row: int,
        source_column: int,
        target_row: int,
        target_column: int,
        player: str | None = None,
    ) -> bool:
        """Aplica una jugada legal y devuelve si pudo ejecutarse.

        La ficha atacante ocupa el destino y la casilla de origen queda vacía.
        """
        if not self.is_valid_move(
            source_row,
            source_column,
            target_row,
            target_column,
            player,
        ):
            return False

        moving_piece = self[source_row, source_column]
        self[target_row, target_column] = moving_piece
        self[source_row, source_column] = self.EMPTY
        return True

    def legal_moves(self, player: str) -> list[tuple[int, int, int, int]]:
        """Genera todas las capturas legales disponibles para ``player``.

        Cada movimiento se representa como una tupla:
        ``(fila_origen, columna_origen, fila_destino, columna_destino)``.
        """
        if player not in (self.PLAYER_A, self.PLAYER_B):
            raise ValueError("El jugador debe ser 'A' o 'B'.")

        moves = []

        for row in range(1, len(self) + 1):
            for column in range(1, len(self) + 1):
                if self[row, column] != player:
                    continue

                for row_delta, column_delta in self.DIRECTIONS:
                    target_row = row + row_delta
                    target_column = column + column_delta

                    if self.is_valid_move(
                        row,
                        column,
                        target_row,
                        target_column,
                        player,
                    ):
                        moves.append(
                            (row, column, target_row, target_column)
                        )

        return moves

    def has_moves(self, player: str) -> bool:
        """Indica si ``player`` posee al menos una captura legal."""
        return bool(self.legal_moves(player))

    # ------------------------------------------------------------------
    # Alias en español para mantener el código fácil de leer en el curso
    # y conservar compatibilidad con la versión inicial del proyecto.
    # ------------------------------------------------------------------
    def jugada(self, f: int, c: int, x: int, y: int) -> bool:
        """Alias de ``play`` conservado por compatibilidad."""
        return self.play(f, c, x, y)

    def valid_move(
        self,
        f: int,
        c: int,
        x: int,
        y: int,
        color: str,
    ) -> bool:
        """Alias de ``is_valid_move`` conservado por compatibilidad."""
        return self.is_valid_move(f, c, x, y, color)

    def hay_movimientos(self, jugador: str) -> bool:
        """Alias de ``has_moves`` que evalúa al jugador indicado."""
        return self.has_moves(jugador)

    def movimientos_legales(
        self,
        jugador: str,
    ) -> list[tuple[int, int, int, int]]:
        """Alias de ``legal_moves`` para uso desde el agente."""
        return self.legal_moves(jugador)