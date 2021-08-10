__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import os, tempfile
from typing import Union

from easyCore.Objects.Base import BaseObj
from easyCore.Utils.UndoRedo import property_stack_deco

from easyDiffractionLib import Phase, Phases
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters as Pars1D
from easyDiffractionLib.Profiles.P1D import Powder1DParameters as Pattern1D


class Sample(BaseObj):
    def __init__(self, phases: Union[Phase, Phases] = None,
                 parameters=None, pattern=None,
                 interface=None, name: str = 'easySample'):
        if isinstance(phases, Phase):
            phases = Phases('Phases', phases)
        elif phases is None:
            phases = Phases('Phases')

        if not isinstance(phases, Phases):
            raise AttributeError('`phases` must be a Crystal or Crystals')

        if parameters is None:
            parameters = Pars1D.default()

        if pattern is None:
            pattern = Pattern1D.default()

        super(Sample, self).__init__(name, _phases=phases, _parameters=parameters, _pattern=pattern)

        self.filename = os.path.join(tempfile.gettempdir(), 'easydiffraction_temp.cif')
        print(f"Temp CIF: {self.filename}")
        self.output_index = None
        self.interface = interface

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)

    def remove_background(self, background):
        if background.linked_experiment.raw_value in self._pattern.backgrounds.linked_experiments:
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
        if not isinstance(value, Pars1D):
            raise ValueError
        self._parameters = value
        self._parameters.interface = self._interface

    def update_bindings(self):
        self.generate_bindings()

    @property
    def pattern(self):
        return self._pattern

    def as_dict(self, skip: list = None) -> dict:
        d = super(Sample, self).as_dict(skip=skip)
        del d['_phases']
        del d['_parameters']
        del d['_pattern']
        return d