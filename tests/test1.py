__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore import np

from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Phase
from easyDiffractionLib.interface import InterfaceFactory as Calculator
# from easyDiffractionLib.Elements.Experiments.Experiment import Pars1D
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters

import matplotlib.pyplot as plt


calculator = Calculator()

phase = Phase.from_cif_file('tests/SrTiO3.cif')

sample = Sample(phases=phase,
                parameters=Instrument1DCWParameters.default(),
                calculator=calculator)
# S.phase.cell.length_a = 5
# S.parameters.wavelength = 1.25
# print(S)
x_data = np.linspace(5, 150, 100)
y_data = calculator.fit_func(x_data)

# plt.plot(x_data, y_data, label="CFL")
# plt.show()

sample.parameters.wavelength = 2.5
y_data = calculator.fit_func(x_data)
# plt.plot(x_data, y_data, label="CFL")
# plt.show()

sample.phases[0].cell.length_a = 10
y_data = calculator.fit_func(x_data)
# plt.plot(x_data, y_data, label="CFL")
# plt.show()

calculator.switch('CrysFML')
sample = Sample(phases=phase,
                parameters=Instrument1DCWParameters.default(),
                calculator=calculator)
# ._updateInterface()

# S.phase.cell.length_a = 5
# S.parameters.wavelength = 1.25
# print(S)
x_data = np.linspace(5, 150, 100)
y_data = calculator.fit_func(x_data)

plt.plot(x_data, y_data, label="CFL")
plt.show()

# sample.parameters.wavelength = 2.5
#y_data = calculator.fit_func(x_data)
#plt.plot(x_data, y_data, label="CFL")
#plt.show()

sample.phases[0].cell.length_a = 10
y_data = calculator.fit_func(x_data)
plt.plot(x_data, y_data, label="CFL")
plt.show()
