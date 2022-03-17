__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import TypeVar, List

from easyCore.Datasets.xarray import xr
from easyCore.Objects.Base import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder
from easyDiffractionLib.Elements.Backgrounds.Background import BackgroundContainer
from easyDiffractionLib.Profiles.common import JobSetup, _DataClassBase

_decoder = MontyDecoder()
T = TypeVar("T")


class Powder1DSim(_DataClassBase):
    def __init__(self, dataset):
        super(Powder1DSim, self).__init__(dataset)
        self._simulation_prefix = "sim_"
        self.name = ""

    def add_simulation(self, simulation_name, simulation):
        self._dataset[self._simulation_prefix + simulation_name] = simulation

    # @property
    # def simulations(self) -> xr.Dataset:
    #     temp_dataset = xr.Dataset()
    #     for sim in self.simulation_names:
    #         temp_dataset[sim] = self._dataset[sim]
    #     return temp_dataset
    #
    # @property
    # def simulation_names(self) -> List[str]:
    #     sims = [a for a in self._dataset.variables.keys() if a.startswith(self._simulation_prefix)]
    #     return sims


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
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "zero_shift",
            "units": "degree",
            "value": 0.0,
            "fixed": True,
        },
        "scale": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "scale",
            "value": 1,
            "fixed": True,
            "enabled": False,
        },
        "backgrounds": {
            "@module": "easyDiffractionLib.Elements.Backgrounds.Background",
            "@class": "BackgroundContainer",
            "@version": "0.0.1",
            "data": [],
        },
    }

    def __init__(
        self,
        zero_shift: Parameter,
        scale: Parameter,
        backgrounds: BackgroundContainer,
        interface=None,
    ):
        super().__init__(
            self.__class__.__name__,
            zero_shift=zero_shift,
            scale=scale,
            backgrounds=backgrounds,
        )
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(
        cls,
        zero_shift: float = _defaults["zero_shift"]["value"],
        scale: float = _defaults["scale"]["value"],
    ):
        defaults = deepcopy(cls._defaults)
        defaults["zero_shift"]["value"] = zero_shift
        zero_shift = _decoder.process_decoded(defaults["zero_shift"])
        defaults["scale"]["value"] = scale
        scale = _decoder.process_decoded(defaults["scale"])
        backgrounds = BackgroundContainer()
        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        zero_shift = _decoder.process_decoded(defaults["zero_shift"])
        scale = _decoder.process_decoded(defaults["scale"])
        backgrounds = BackgroundContainer()

        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)


class PolPowder1DParameters(Powder1DParameters):
    pass


class Instrument1DCWParameters(BaseObj):
    _name = "InstrumentalParameters"
    _defaults = {
        "wavelength": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "wavelength",
            "units": "angstrom",
            "value": 1.54056,
            "fixed": True,
        },
        "resolution_u": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "resolution_u",
            "value": 0.0002,
            "fixed": True,
        },
        "resolution_v": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "resolution_v",
            "value": -0.0002,
            "fixed": True,
        },
        "resolution_w": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "resolution_w",
            "value": 0.012,
            "fixed": True,
        },
        "resolution_x": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "resolution_x",
            "value": 0.0,
            "fixed": True,
        },
        "resolution_y": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "resolution_y",
            "value": 0.0,
            "fixed": True,
        },
        "polarization": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "polarization",
            "value": 0.0,
            "fixed": True,
        },
        "polarizing_efficiency": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "polarizing_efficiency",
            "value": 100,
            "fixed": True,
        },
    }

    def __init__(
        self,
        wavelength: Parameter,
        resolution_u: Parameter,
        resolution_v: Parameter,
        resolution_w: Parameter,
        resolution_x: Parameter,
        resolution_y: Parameter,
        polarization: Parameter,
        polarizing_efficiency: Parameter,
        interface=None,
    ):
        super().__init__(
            self.__class__.__name__,
            wavelength=wavelength,
            resolution_u=resolution_u,
            resolution_v=resolution_v,
            resolution_w=resolution_w,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            polarization=polarization,
            polarizing_efficiency=polarizing_efficiency,
        )
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(
        cls,
        wavelength: float = _defaults["wavelength"]["value"],
        resolution_u: float = _defaults["resolution_u"]["value"],
        resolution_v: float = _defaults["resolution_v"]["value"],
        resolution_w: float = _defaults["resolution_w"]["value"],
        resolution_x: float = _defaults["resolution_x"]["value"],
        resolution_y: float = _defaults["resolution_y"]["value"],
        polarization: float = _defaults["polarization"]["value"],
        polarizing_efficiency: float = _defaults["polarizing_efficiency"]["value"],
    ):
        defaults = deepcopy(cls._defaults)
        defaults["wavelength"]["value"] = wavelength
        wavelength = _decoder.process_decoded(defaults["wavelength"])
        defaults["resolution_u"]["value"] = resolution_u
        resolution_u = _decoder.process_decoded(defaults["resolution_u"])
        defaults["resolution_v"]["value"] = resolution_v
        resolution_v = _decoder.process_decoded(defaults["resolution_v"])
        defaults["resolution_w"]["value"] = resolution_w
        resolution_w = _decoder.process_decoded(defaults["resolution_w"])
        defaults["resolution_x"]["value"] = resolution_x
        resolution_x = _decoder.process_decoded(defaults["resolution_x"])
        defaults["resolution_y"]["value"] = resolution_y
        resolution_y = _decoder.process_decoded(defaults["resolution_y"])
        defaults["polarization"]["value"] = polarization
        polarization = _decoder.process_decoded(defaults["polarization"])
        defaults["polarizing_efficiency"]["value"] = polarizing_efficiency
        polarizing_efficiency = _decoder.process_decoded(defaults["polarizing_efficiency"])
        return cls(
            wavelength=wavelength,
            resolution_u=resolution_u,
            resolution_v=resolution_v,
            resolution_w=resolution_w,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            polarization=polarization,
            polarizing_efficiency=polarizing_efficiency,
        )

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        wavelength = _decoder.process_decoded(defaults["wavelength"])
        resolution_u = _decoder.process_decoded(defaults["resolution_u"])
        resolution_v = _decoder.process_decoded(defaults["resolution_v"])
        resolution_w = _decoder.process_decoded(defaults["resolution_w"])
        resolution_x = _decoder.process_decoded(defaults["resolution_x"])
        resolution_y = _decoder.process_decoded(defaults["resolution_y"])
        polarization = _decoder.process_decoded(defaults["polarization"])
        polarizing_efficiency = _decoder.process_decoded(defaults["polarizing_efficiency"])
        return cls(
            wavelength=wavelength,
            resolution_u=resolution_u,
            resolution_v=resolution_v,
            resolution_w=resolution_w,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            polarization=polarization,
            polarizing_efficiency=polarizing_efficiency,
        )


class Instrument1DTOFParameters(BaseObj):
    _name = "InstrumentalParameters"
    _defaults = {
        "ttheta_bank": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "ttheta_bank",
            "units": "deg",
            "value": 145.00,
            "fixed": True,
        },
        "dtt1": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "dtt1",
            "units": "deg",
            "value": 6167.24700,
            "fixed": True,
        },
        "dtt2": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "dtt2",
            "units": "deg",
            "value": -2.28000,
            "fixed": True,
        },
        "sigma0": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "sigma0",
            "value": 0.409,
            "fixed": True,
        },
        "sigma1": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "sigma1",
            "value": 8.118,
            "fixed": True,
        },
        "sigma2": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "sigma2",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma0": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "gamma0",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma1": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "gamma1",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma2": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "gamma2",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "alpha0": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "alpha0",
            "value": 0.0,
            "fixed": True,
        },
        "alpha1": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "alpha1",
            "value": 0.29710,
            "fixed": True,
        },
        "beta0": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "beta0",
            "value": 0.04182,
            "fixed": True,
        },
        "beta1": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "beta1",
            "value": 0.00224,
            "fixed": True,
        },
        "polarization": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "polarization",
            "value": 0.0,
            "fixed": True,
        },
        "polarizing_efficiency": {
            "@module": "easyCore.Objects.Base",
            "@class": "Parameter",
            "@version": "0.0.1",
            "name": "polarizing_efficiency",
            "value": 100,
            "fixed": True,
        },
    }

    def __init__(
        self,
        ttheta_bank: Parameter,
        dtt1: Parameter,
        dtt2: Parameter,
        sigma0: Parameter,
        sigma1: Parameter,
        sigma2: Parameter,
        gamma0: Parameter,
        gamma1: Parameter,
        gamma2: Parameter,
        alpha0: Parameter,
        alpha1: Parameter,
        beta0: Parameter,
        beta1: Parameter,
        polarization: Parameter,
        polarizing_efficiency: Parameter,
        interface=None,
    ):
        super().__init__(
            self.__class__.__name__,
            ttheta_bank=ttheta_bank,
            dtt1=dtt1,
            dtt2=dtt2,
            sigma0=sigma0,
            sigma1=sigma1,
            sigma2=sigma2,
            gamma0=gamma0,
            gamma1=gamma1,
            gamma2=gamma2,
            alpha0=alpha0,
            alpha1=alpha1,
            beta0=beta0,
            beta1=beta1,
            polarization=polarization,
            polarizing_efficiency=polarizing_efficiency,
        )
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(
        cls,
        ttheta_bank: float = _defaults["ttheta_bank"]["value"],
        dtt1: float = _defaults["dtt1"]["value"],
        dtt2: float = _defaults["dtt2"]["value"],
        sigma0: float = _defaults["sigma0"]["value"],
        sigma1: float = _defaults["sigma1"]["value"],
        sigma2: float = _defaults["sigma2"]["value"],
        gamma0: float = _defaults["gamma0"]["value"],
        gamma1: float = _defaults["gamma1"]["value"],
        gamma2: float = _defaults["gamma2"]["value"],
        alpha0: float = _defaults["alpha0"]["value"],
        alpha1: float = _defaults["alpha1"]["value"],
        beta0: float = _defaults["beta0"]["value"],
        beta1: float = _defaults["beta1"]["value"],
        polarization: float = _defaults["polarization"]["value"],
        polarizing_efficiency: float = _defaults["polarizing_efficiency"]["value"],
    ):
        defaults = deepcopy(cls._defaults)
        defaults["ttheta_bank"]["value"] = ttheta_bank
        ttheta_bank = _decoder.process_decoded(defaults["ttheta_bank"])
        defaults["dtt1"]["value"] = dtt1
        dtt1 = _decoder.process_decoded(defaults["dtt1"])
        defaults["dtt2"]["value"] = dtt2
        dtt2 = _decoder.process_decoded(defaults["dtt2"])
        defaults["sigma0"]["value"] = sigma0
        sigma0 = _decoder.process_decoded(defaults["sigma0"])
        defaults["sigma1"]["value"] = sigma1
        sigma1 = _decoder.process_decoded(defaults["sigma1"])
        defaults["sigma2"]["value"] = sigma2
        sigma2 = _decoder.process_decoded(defaults["sigma2"])
        defaults["gamma0"]["value"] = gamma0
        gamma0 = _decoder.process_decoded(defaults["gamma0"])
        defaults["gamma1"]["value"] = gamma1
        gamma1 = _decoder.process_decoded(defaults["gamma1"])
        defaults["gamma2"]["value"] = gamma2
        gamma2 = _decoder.process_decoded(defaults["gamma2"])
        defaults["alpha0"]["value"] = alpha0
        alpha0 = _decoder.process_decoded(defaults["alpha0"])
        defaults["alpha1"]["value"] = alpha1
        alpha1 = _decoder.process_decoded(defaults["alpha1"])
        defaults["beta0"]["value"] = beta0
        beta0 = _decoder.process_decoded(defaults["beta0"])
        defaults["beta1"]["value"] = beta1
        beta1 = _decoder.process_decoded(defaults["beta1"])
        defaults["polarization"]["value"] = polarization
        polarization = _decoder.process_decoded(defaults["polarization"])
        defaults["polarizing_efficiency"]["value"] = polarizing_efficiency
        polarizing_efficiency = _decoder.process_decoded(defaults["polarizing_efficiency"])

        return cls(
            ttheta_bank=ttheta_bank,
            dtt1=dtt1,
            dtt2=dtt2,
            sigma0=sigma0,
            sigma1=sigma1,
            sigma2=sigma2,
            gamma0=gamma0,
            gamma1=gamma1,
            gamma2=gamma2,
            alpha0=alpha0,
            alpha1=alpha1,
            beta0=beta0,
            beta1=beta1,
            polarization=polarization,
            polarizing_efficiency=polarizing_efficiency,
        )

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        ttheta_bank = _decoder.process_decoded(defaults["ttheta_bank"])
        dtt1 = _decoder.process_decoded(defaults["dtt1"])
        dtt2 = _decoder.process_decoded(defaults["dtt2"])
        sigma0 = _decoder.process_decoded(defaults["sigma0"])
        sigma1 = _decoder.process_decoded(defaults["sigma1"])
        sigma2 = _decoder.process_decoded(defaults["sigma2"])
        gamma0 = _decoder.process_decoded(defaults["gamma0"])
        gamma1 = _decoder.process_decoded(defaults["gamma1"])
        gamma2 = _decoder.process_decoded(defaults["gamma2"])
        alpha0 = _decoder.process_decoded(defaults["alpha0"])
        alpha1 = _decoder.process_decoded(defaults["alpha1"])
        beta0 = _decoder.process_decoded(defaults["beta0"])
        beta1 = _decoder.process_decoded(defaults["beta1"])
        polarization = _decoder.process_decoded(defaults["polarization"])
        polarizing_efficiency = _decoder.process_decoded(defaults["polarizing_efficiency"])

        return cls(
            ttheta_bank=ttheta_bank,
            dtt1=dtt1,
            dtt2=dtt2,
            sigma0=sigma0,
            sigma1=sigma1,
            sigma2=sigma2,
            gamma0=gamma0,
            gamma1=gamma1,
            gamma2=gamma2,
            alpha0=alpha0,
            alpha1=alpha1,
            beta0=beta0,
            beta1=beta1,
            polarization=polarization,
            polarizing_efficiency=polarizing_efficiency,
        )


class Instrument1DCWPolParameters(Instrument1DCWParameters):
    pass


Unpolarized1DClasses = JobSetup(
    [Powder1DSim, Powder1DExp], Powder1DParameters, Instrument1DCWParameters
)

Unpolarized1DTOFClasses = JobSetup(
    [Powder1DSim, Powder1DExp], Powder1DParameters, Instrument1DTOFParameters
)
