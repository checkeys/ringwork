# coding:utf-8

from rio import Session


class Window():

    def __init__(self, width: float, height: float):
        self.__width: float = width
        self.__height: float = height

    @property
    def width(self) -> float:
        return self.__width

    @property
    def height(self) -> float:
        return self.__height

    @property
    def desktop_layout(self) -> bool:
        # Determine the layout based on the window width
        return self.width > 30.0

    @classmethod
    def from_session(cls, session: Session) -> "Window":
        return cls(width=session.window_width, height=session.window_height)
