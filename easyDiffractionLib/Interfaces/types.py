from __future__ import annotations

__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from abc import abstractmethod
from typing import List, Any, Callable, Union, TYPE_CHECKING, TypeVar, Type

if TYPE_CHECKING:
    from easyCore.Objects.Inferface import ItemContainer
    from easyCore.Utils.typing import B


class _Type:
    _internal_type = True
    calculator: Any
    _identify: Callable[[Any], Union[str, int]]

    @abstractmethod
    def create(self, model: B) -> List[ItemContainer]:
        pass


T = TypeVar("T", bound=_Type)


def interfaceMixInMeta(cls):

    class_create = getattr(cls, "create", None)

    def create(self, model: B) -> List[ItemContainer]:
        cls_s: List[Type[T]] = [
            c_ for c_ in cls.__bases__ if getattr(c_, "_internal_type", False)
        ]
        r_list = []
        if class_create is not None:
            r_list += class_create(self, model)
        for cls_ in cls_s:
            r_list += cls_.create(self, model)
        return r_list

    setattr(cls, "create", create)
    return cls


class Neutron(_Type):
    pass


class XRay(_Type):
    pass


class Powder(_Type):
    pass


class SingleCrystal(_Type):
    pass


class CW(_Type):
    pass


class TOF(_Type):
    pass


class Pol(_Type):
    pass


class UPol(_Type):
    pass
