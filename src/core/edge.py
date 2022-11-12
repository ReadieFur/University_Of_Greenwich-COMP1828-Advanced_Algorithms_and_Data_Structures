#Avoid circular import (this import is only used for IDE type hinting).
#https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node import Node

class Edge:
    #Public get, private set.
    __neibouring_node: Node
    @property
    def neibouring_node(self) -> Node:
        """The neibouring that this edge is connected to."""
        return self.__neibouring_node

    #Public get, public set.
    __weight: int
    @property
    def weight(self) -> int:
        """The weight of the edge."""
        return self.__weight
    @weight.setter
    def weight(self, value) -> None:
        self.__weight = value

    def __init__(self, neibouring_node: Node, weight: int = 1):
        self.__neibouring_node = neibouring_node
        self.__weight = weight
