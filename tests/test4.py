from easyCore import np

from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Site, Phases, Phase
from easyDiffractionLib.interface import InterfaceFactory as Calculator
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters as CWParams
from easyDiffractionLib.Profiles.P1D import Instrument1DTOFParameters as TOFParams
from easyDiffractionLib.Profiles.P1D import Powder1DParameters

import matplotlib.pyplot as plt


calculator = Calculator()
calculator.switch('CrysPy')

atom = Site.from_pars(label="Cl1",
                      specie='Cl',
                      fract_x=0.1250,
                      fract_y=0.1670,
                      fract_z=0.1070)
atom.add_adp('Uiso', Uiso=0.0)

phase = Phase(name="p1")
phase.spacegroup.space_group_HM_name = "P 42/n c m"
phase.add_atom(atom)

phases = Phases()
phases.append(phase)

parameters = CWParams.default()
parameters.length_a = 8.56
parameters.length_c = 6.12
parameters.length_b = 8.56

parameters.resolution_u = 0.1447
parameters.resolution_v = -0.4252
parameters.resolution_w = 0.3864
parameters.resolution_x = 0.0
parameters.resolution_y = 0.0

pattern = Powder1DParameters.default()
pattern.zero_shift = 0.0
pattern.scale = 100.0

S = Sample(phases=phases, parameters=parameters, pattern=pattern, calculator=calculator)

x_data = np.linspace(1, 120, 500)
y_data = calculator.fit_func(x_data)

plt.plot(x_data, y_data, label="CW")
plt.show()

phases = S.phases[0]
pattern = S.pattern

parameters = TOFParams.default()
parameters.length_a = 8.56
parameters.length_c = 6.12
parameters.length_b = 8.56
parameters.dtt1 = 6167.24700
parameters.dtt2 = -2.28000
parameters.ttheta_bank = 145.00
pattern.zero_shift = 0.0
pattern.scale = 100.0

tof_str = 'Npowder1DTOF'
interfaces = calculator.interface_compatability(tof_str)
calculator.switch(interfaces[0])

S = Sample(phases=phases, parameters=parameters, pattern=pattern, calculator=calculator)

x_data = np.linspace(5000, 60000, 500)
y_data = calculator.fit_func(x_data)

plt.plot(x_data, y_data, label="TOF")
plt.show()
