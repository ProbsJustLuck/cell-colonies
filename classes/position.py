class Position:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def get_x(self) -> int:
        return self._x
    
    def get_y(self) -> int:
        return self._y