from typing import Union

from PyQt5.QtCore import QPointF


class Position:
    def __init__(self, x: Union[int, float], y: Union[int, float], z: Union[int, float, None] = None):
        self._x = x
        self._y = y
        self._z = z

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        self._y = value

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        self._x = value

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: int) -> None:
        self._z = value

    def __str__(self):
        return f"{self._x}x {self._y}y {self._z}z"

    @classmethod
    def fromQPointF(cls, point: QPointF):
        return cls(x=point.x(), y=point.y())