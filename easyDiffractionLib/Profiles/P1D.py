from __future__ import annotations

__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import TypeVar, List, Optional, Union, TYPE_CHECKING, ClassVar, Tuple

from easyCore.Datasets.xarray import xr
from easyCore.Objects.ObjectClasses import BaseObj, Parameter
from easyDiffractionLib.Profiles.common import JobSetup, _DataClassBase
from easyDiffractionLib.components.polarization import PolarizedBeam
from easyDiffractionLib.elements.Backgrounds.Background import BackgroundContainer

T = TypeVar("T")

if TYPE_CHECKING:
    from easyCore.Utils.typing import iF


class Powder1DSim(_DataClassBase):
    def __init__(self, dataset):
        super(Powder1DSim, self).__init__(dataset)
        self._simulation_prefix = "sim_"
        self.name = ""

    def add_simulation(self, simulation_name, simulation):
        self._dataset[self._simulation_prefix + simulation_name] = simulation

class Powder1DExp(_DataClassBase):
    def __init__(self, dataset, simulation_prefix):
        super(Powder1DExp, self).__init__(dataset)
        self.simulation_prefix = simulation_prefix

    @property
    def experiments(self) -> xr.Dataset:
        temp_dataset = xr.Dataset()
        for exp in self.experiment_names:
            temp_dataset[exp] = self._dataset[exp]
        return temp_dataset

    @property
    def experiment_names(self) -> List[str]:
        exps = [
            a
            for a in self._dataset.variables.keys()
            if not a.startswith(self.simulation_prefix) and not a in self._dataset.dims
        ]
        return exps


class Powder1DPolSim(Powder1DSim):
    def __init__(self, dataset):
        super(Powder1DPolSim, self).__init__(dataset)


class Powder1DPolExp(Powder1DExp):
    def __init__(self, dataset, simulation_prefix):
        super(Powder1DPolExp, self).__init__(dataset, simulation_prefix)


class Powder1DParameters(BaseObj):
    _name = "1DPowderProfile"
    _defaults = {
        "zero_shift": {
            "name": "zero_shift",
            "units": "degree",
            "value": 0.0,
            "fixed": True,
        },
        "scale": {
            "name": "scale",
            "value": 1,
            "fixed": True,
            "enabled": False,
        },
    }

    zero_shift: ClassVar[Parameter]
    scale: ClassVar[Parameter]
    backgrounds: ClassVar[BackgroundContainer]

    def __init__(
        self,
        zero_shift: Optional[Union[Parameter, float]] = None,
        scale: Optional[Union[Parameter, float]] = None,
        backgrounds: Optional[BackgroundContainer] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):
        super().__init__(
            self.__class__.__name__,
            **{k: Parameter(**self._defaults[k]) for k in self._defaults.keys()},
            backgrounds=BackgroundContainer(),
            **kwargs,
        )
        if zero_shift is not None:
            self.zero_shift = zero_shift
        if scale is not None:
            self.scale = scale
        if backgrounds is not None:
            self.backgrounds = backgrounds

        self.name = self._name
        self.interface = interface


class PolPowder1DParameters(Powder1DParameters):
    # polarization: ClassVar[Parameter]
    # efficiency: ClassVar[Parameter]
    field: ClassVar[Parameter]
    beam: ClassVar[PolarizedBeam]

    _defaults = {
        "field": {"name": "magnetic_field", "value": 1.0, "units": "T", "fixed": True},
    }
    _defaults.update(Powder1DParameters._defaults)

    def __init__(
        self,
        zero_shift: Optional[Union[Parameter, float]] = None,
        scale: Optional[Union[Parameter, float]] = None,
        backgrounds: Optional[BackgroundContainer] = None,
        beam: Optional[Union[PolarizedBeam, Tuple[float, float]]] = None,
        field: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):
        polarization = None
        if "polarization" in kwargs.keys():
            polarization = kwargs.pop("polarization")
        efficiency = None
        if "efficiency" in kwargs.keys():
            efficiency = kwargs.pop("efficiency")

        if beam is None:
            beam = PolarizedBeam(polarization=polarization, efficiency=efficiency)
        if isinstance(beam, tuple):
            beam = PolarizedBeam(*beam)
        else:
            if polarization is not None:
                beam.polarization = polarization
            if efficiency is not None:
                beam.efficiency = efficiency

        kwargs["beam"] = beam

        super().__init__(
            zero_shift=zero_shift,
            scale=scale,
            backgrounds=backgrounds,
            **kwargs,
        )
        if field is not None:
            self.field = field

        self.interface = interface

    @property
    def polarization(self):
        return self.beam.polarization

    @property
    def efficiency(self):
        return self.beam.efficiency


class Instrument1DCWParameters(BaseObj):
    _name = "InstrumentalParameters"
    _defaults = {
        "wavelength": {
            "name": "wavelength",
            "units": "angstrom",
            "value": 1.54056,
            "fixed": True,
        },
        "resolution_u": {
            "name": "resolution_u",
            "value": 0.0002,
            "fixed": True,
        },
        "resolution_v": {
            "name": "resolution_v",
            "value": -0.0002,
            "fixed": True,
        },
        "resolution_w": {
            "name": "resolution_w",
            "value": 0.012,
            "fixed": True,
        },
        "resolution_x": {
            "name": "resolution_x",
            "value": 0.0,
            "fixed": True,
        },
        "resolution_y": {
            "name": "resolution_y",
            "value": 0.0,
            "fixed": True,
        },
        "reflex_asymmetry_p1": {
            "name": "reflex_asymmetry_p1",
            "value": 0.0,
            "fixed": True,
        },
        "reflex_asymmetry_p2": {
            "name": "reflex_asymmetry_p2",
            "value": 0.0,
            "fixed": True,
        },
        "reflex_asymmetry_p3": {
            "name": "reflex_asymmetry_p3",
            "value": 0.0,
            "fixed": True,
        },
        "reflex_asymmetry_p4": {
            "name": "reflex_asymmetry_p4",
            "value": 0.0,
            "fixed": True,
        }
    }

    wavelength: ClassVar[Parameter]
    resolution_u: ClassVar[Parameter]
    resolution_v: ClassVar[Parameter]
    resolution_w: ClassVar[Parameter]
    resolution_x: ClassVar[Parameter]
    resolution_y: ClassVar[Parameter]
    reflex_asymmetry_p1: ClassVar[Parameter]
    reflex_asymmetry_p2: ClassVar[Parameter]
    reflex_asymmetry_p3: ClassVar[Parameter]
    reflex_asymmetry_p4: ClassVar[Parameter]

    def __init__(
        self,
        wavelength: Optional[Union[Parameter, float]] = None,
        resolution_u: Optional[Union[Parameter, float]] = None,
        resolution_v: Optional[Union[Parameter, float]] = None,
        resolution_w: Optional[Union[Parameter, float]] = None,
        resolution_x: Optional[Union[Parameter, float]] = None,
        resolution_y: Optional[Union[Parameter, float]] = None,
        reflex_asymmetry_p1: Optional[Union[Parameter, float]] = None,
        reflex_asymmetry_p2: Optional[Union[Parameter, float]] = None,
        reflex_asymmetry_p3: Optional[Union[Parameter, float]] = None,
        reflex_asymmetry_p4: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
    ):
        super(Instrument1DCWParameters, self).__init__(
            name=self.__class__.__name__,
            **{k: Parameter(**self._defaults[k]) for k in self._defaults.keys()},
        )

        if wavelength is not None:
            self.wavelength = wavelength
        if resolution_u is not None:
            self.resolution_u = resolution_u
        if resolution_v is not None:
            self.resolution_v = resolution_v
        if resolution_v is not None:
            self.resolution_v = resolution_v
        if resolution_w is not None:
            self.resolution_w = resolution_w
        if resolution_x is not None:
            self.resolution_x = resolution_x
        if resolution_y is not None:
            self.resolution_y = resolution_y
        if reflex_asymmetry_p1 is not None:
            self.reflex_asymmetry_p1 = reflex_asymmetry_p1
        if reflex_asymmetry_p2 is not None:
            self.reflex_asymmetry_p2 = reflex_asymmetry_p2
        if reflex_asymmetry_p3 is not None:
            self.reflex_asymmetry_p3 = reflex_asymmetry_p3
        if reflex_asymmetry_p4 is not None:
            self.reflex_asymmetry_p4 = reflex_asymmetry_p4
        self.name = self._name
        self.interface = interface


class Instrument1DTOFParameters(BaseObj):
    _name = "InstrumentalParameters"
    _defaults = {
        "ttheta_bank": {
            "name": "ttheta_bank",
            "units": "deg",
            "value": 145.00,
            "fixed": True,
        },
        "dtt1": {
            "name": "dtt1",
            "units": "deg",
            "value": 6167.24700,
            "fixed": True,
        },
        "dtt2": {
            "name": "dtt2",
            "units": "deg",
            "value": -2.28000,
            "fixed": True,
        },
        "sigma0": {
            "name": "sigma0",
            "value": 0.409,
            "fixed": True,
        },
        "sigma1": {
            "name": "sigma1",
            "value": 8.118,
            "fixed": True,
        },
        "sigma2": {
            "name": "sigma2",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma0": {
            "name": "gamma0",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma1": {
            "name": "gamma1",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma2": {
            "name": "gamma2",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "alpha0": {
            "name": "alpha0",
            "value": 0.0,
            "fixed": True,
        },
        "alpha1": {
            "name": "alpha1",
            "value": 0.29710,
            "fixed": True,
        },
        "beta0": {
            "name": "beta0",
            "value": 0.04182,
            "fixed": True,
        },
        "beta1": {
            "name": "beta1",
            "value": 0.00224,
            "fixed": True,
        },
    }

    ttheta_bank: ClassVar[Parameter]
    dtt1: ClassVar[Parameter]
    dtt2: ClassVar[Parameter]
    sigma0: ClassVar[Parameter]
    sigma1: ClassVar[Parameter]
    sigma2: ClassVar[Parameter]
    gamma0: ClassVar[Parameter]
    gamma1: ClassVar[Parameter]
    gamma2: ClassVar[Parameter]
    alpha0: ClassVar[Parameter]
    alpha1: ClassVar[Parameter]
    beta0: ClassVar[Parameter]
    beta1: ClassVar[Parameter]

    def __init__(
        self,
        ttheta_bank: Optional[Union[Parameter, float]] = None,
        dtt1: Optional[Union[Parameter, float]] = None,
        dtt2: Optional[Union[Parameter, float]] = None,
        sigma0: Optional[Union[Parameter, float]] = None,
        sigma1: Optional[Union[Parameter, float]] = None,
        sigma2: Optional[Union[Parameter, float]] = None,
        gamma0: Optional[Union[Parameter, float]] = None,
        gamma1: Optional[Union[Parameter, float]] = None,
        gamma2: Optional[Union[Parameter, float]] = None,
        alpha0: Optional[Union[Parameter, float]] = None,
        alpha1: Optional[Union[Parameter, float]] = None,
        beta0: Optional[Union[Parameter, float]] = None,
        beta1: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
    ):
        super().__init__(
            self.__class__.__name__,
            **{k: Parameter(**self._defaults[k]) for k in self._defaults.keys()},
        )

        if ttheta_bank is not None:
            self.ttheta_bank = ttheta_bank
        if dtt1 is not None:
            self.dtt1 = dtt1
        if dtt2 is not None:
            self.dtt2 = dtt2
        if sigma0 is not None:
            self.sigma0 = sigma0
        if sigma1 is not None:
            self.sigma1 = sigma1
        if sigma2 is not None:
            self.sigma2 = sigma2
        if gamma0 is not None:
            self.gamma0 = gamma0
        if gamma1 is not None:
            self.gamma1 = gamma1
        if gamma2 is not None:
            self.gamma2 = gamma2
        if alpha0 is not None:
            self.alpha0 = alpha0
        if alpha1 is not None:
            self.alpha1 = alpha1
        if beta0 is not None:
            self.beta0 = beta0
        if beta1 is not None:
            self.beta1 = beta1

        self.name = self._name
        self.interface = interface


class Instrument1DCWPolParameters(Instrument1DCWParameters):
    pass


Unpolarized1DClasses = JobSetup(
    [Powder1DSim, Powder1DExp], Powder1DParameters, Instrument1DCWParameters
)

Unpolarized1DTOFClasses = JobSetup(
    [Powder1DSim, Powder1DExp], Powder1DParameters, Instrument1DTOFParameters
)

Polarized1DClasses = JobSetup(
    [Powder1DSim, Powder1DExp], PolPowder1DParameters, Instrument1DCWParameters
)

Polarized1DTOFClasses = JobSetup(
    [Powder1DSim, Powder1DExp], PolPowder1DParameters, Instrument1DTOFParameters
)

class PDFParameters(Instrument1DCWParameters):
# class PDFParameters(BaseObj):
    _name = "PDFProfile"
    _defaults = {
        "qmax": {
            "name": "Q_max",
            "units": "1/Angstrom",
            "value": 30.0,
            "fixed": True,
        },
        "qdamp": {
            "name": "Q_damp",
            "value": 0.01,
            "fixed": True,
            "enabled": False,
        },
    }

    qmax: ClassVar[Parameter]
    qdamp: ClassVar[Parameter]

    def __init__(
        self,
        qmax: Optional[Union[Parameter, float]] = None,
        qdamp: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):
        super(Instrument1DCWParameters, self).__init__(self.__class__.__name__)

        if qmax is not None:
            self.qmax = qmax
        if qdamp is not None:
            self.qdamp = qdamp

        self.name = self._name
        self.interface = interface
