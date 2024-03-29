__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, tempfile
from typing import Union, ClassVar

from easyCore.Objects.ObjectClasses import BaseObj
from easyCore.Utils.UndoRedo import property_stack_deco
from easyCrystallography.Structures.Phase import Phases as ecPhases

from easyDiffractionLib import Phase, Phases
from easyDiffractionLib.Profiles.P1D import (
    Instrument1DCWParameters,
    Instrument1DTOFParameters,
)
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Interfaces.types import Powder, Neutron
from easyDiffractionLib.Profiles.P1D import Powder1DParameters as Pattern1D
from easyDiffractionLib.Profiles.P1D import PolPowder1DParameters as Pattern1D_Pol


class Sample(BaseObj):

    _REDIRECT = {
        "phases": lambda obj: getattr(obj, '_phases'),
        "parameters": lambda obj: getattr(obj, '_parameters'),
        "pattern": lambda obj: getattr(obj, '_pattern')
    }

    _phases: ClassVar[Phases]
    _parameters: ClassVar
    _pattern: ClassVar

    def __init__(
        self,
        phases: Union[Phase, Phases] = None,
        parameters=None,
        pattern=None,
        interface=None,
        name: str = "easySample",
    ):
        if isinstance(phases, Phase):
            phases = Phases("Phases", phases)
        elif phases is None:
            phases = Phases("Phases")
        elif isinstance(phases, Phases):
            pass
        elif isinstance(phases, list):
            phases = Phases("Phases", phases[0])
        elif isinstance(phases, ecPhases):
            if len(phases) > 0:
                phases = Phases("Phases", phases[0])
        else:
            raise AttributeError("`phases` must be a Crystal or Crystals")

        if parameters is None:
            parameters = Instrument1DCWParameters()

        if pattern is None:
            pattern = Pattern1D()

        super(Sample, self).__init__(
            name, _phases=phases, _parameters=parameters, _pattern=pattern
        )

        # Set bases for easy identification
        self._update_bases(Powder)
        self._update_bases(Neutron)

        if getattr(pattern, "__old_class__", pattern.__class__) == Pattern1D:
            from easyDiffractionLib.Interfaces.types import UPol

            self._update_bases(UPol)
        elif getattr(pattern, "__old_class__", pattern.__class__) == Pattern1D_Pol:
            from easyDiffractionLib.Interfaces.types import Pol

            self._update_bases(Pol)
        if isinstance(parameters, Instrument1DCWParameters):
            from easyDiffractionLib.Interfaces.types import CW

            self._update_bases(CW)
        elif isinstance(parameters, Instrument1DTOFParameters):
            from easyDiffractionLib.Interfaces.types import TOF

            self._update_bases(TOF)

        self.filename = os.path.join(tempfile.gettempdir(), "easydiffraction_temp.cif")
        print(f"Temp CIF: {self.filename}")
        self.output_index = None
        if interface is not None:
            self.interface = interface
        else:
            self.interface = InterfaceFactory()

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, value):
        self._interface = value
        # This is required so that the type is correctly passes.
        if value is not None:
            self.interface.generate_bindings(self)
            self.generate_bindings()

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)

    def remove_background(self, background):
        if (
            background.linked_experiment.raw_value
            in self._pattern.backgrounds.linked_experiments
        ):
            del self._pattern.backgrounds[background.linked_experiment.raw_value]
        else:
            raise ValueError

    @property
    def backgrounds(self):
        return self._pattern.backgrounds

    @property
    def phases(self):
        return self._phases

    @phases.setter
    @property_stack_deco
    def phases(self, value):
        if isinstance(value, Phase):
            self._phases.append(value)
        elif isinstance(value, Phases):
            self._phases = value
            self._borg.map.add_edge(self, value)
            self._phases.interface = self.interface
        else:
            raise ValueError

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    @property_stack_deco
    def parameters(self, value):
        if not isinstance(value, Instrument1DCWParameters):
            raise ValueError
        self._parameters = value
        self._parameters.interface = self._interface

    @property
    def pattern(self):
        return self._pattern

    @property
    def exp_type_str(self) -> str:
        from easyDiffractionLib.Interfaces.types import (
            Neutron,
            XRay,
            Powder,
            SingleCrystal,
            Pol,
            UPol,
            CW,
            TOF,
        )

        type_str = ""
        self_type = type(self)
        if issubclass(self_type, Neutron):
            type_str += "N"
        elif issubclass(self_type, XRay):
            type_str += "X"

        if issubclass(self_type, Powder):
            type_str += "powder"
        elif issubclass(self_type, SingleCrystal):
            type_str += "single"

        type_str += "1D"

        if issubclass(self_type, CW):
            type_str += "CW"
        elif issubclass(self_type, TOF):
            type_str += "TOF"

        if issubclass(self_type, Pol):
            type_str += "pol"
        elif issubclass(self_type, UPol):
            type_str += "unp"

        return type_str

    def _update_bases(self, new_base):
        base_class = getattr(self, "__old_class__", self.__class__)
        old_bases = set(self.__class__.__bases__)
        old_bases = old_bases - {
            base_class,
            *new_base.__mro__,
        }  # This should fix multiple inheritance
        self.__class__.__bases__ = (new_base, *old_bases, base_class)
