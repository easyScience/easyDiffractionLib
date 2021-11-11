__author__ = "github.com/wardsimon"
__version__ = "0.0.2"

import time

import cryspy
import warnings
from easyCore import np, borg
# from pathos import multiprocessing as mp
import functools

warnings.filterwarnings('ignore')


class Cryspy:
    def __init__(self):
        self.pattern = None
        self.conditions = {
            'wavelength': 1.25,
            'resolution': {
                'u': 0.001,
                'v': 0.001,
                'w': 0.001,
                'x': 0.000,
                'y': 0.000
            }

        }
        self.conditions_TOF = {
            'ttheta_bank': 0,
            'dtt1':        0.1,
            'dtt2':        0,
            'resolution':  {
                'sigma0': 0,
                'sigma1': 0,
                'sigma2': 0,
                'gamma0': 0,
                'gamma1': 0,
                'gamma2': 0,
                'alpha0': 0,
                'alpha1': 0,
                'beta0':  0,
                'beta1':  0}
        }
        self.background = None
        self.storage = {}
        self.current_crystal = {}
        self.model = None
        self.phases = cryspy.PhaseL()
        self.type = 'powder1DCW'
        self.additional_data = {}
        self.polarized = False

    @property
    def cif_str(self):
        key = list(self.current_crystal.keys())[0]
        return self.storage[key].to_cif()

    @cif_str.setter
    def cif_str(self, value):
        self.createCrystal_fromCifStr(value)

    def createModel(self, model_id, model_type='powder1DCW'):
        model = {
            'background': cryspy.PdBackgroundL(),
            'phase':      self.phases
        }

        self.polarized = False
        if model_type.endswith('Pol'):
            self.polarized = True
            model_type = model_type.split('Pol')[0]

        cls = cryspy.Pd
        if model_type == 'powder1DTOF':
            cls = cryspy.TOF
            model['background'] = cryspy.TOFBackground()
        self.type = model_type
        self.model = cls(**model)

    def createPhase(self, crystal_name, key='phase'):
        phase = cryspy.Phase(label=crystal_name, scale=1, igsize=0)
        self.storage[key] = phase
        return key

    def assignPhase(self, model_name, phase_name):
        phase = self.storage[phase_name]
        self.phases.items.append(phase)

    def removePhase(self, model_name, phase_name):
        phase = self.storage[phase_name]
        del self.storage[phase_name]
        del self.storage[str(model_name) + '_scale']
        self.phases.items.pop(self.phases.items.index(phase))
        self.current_crystal.pop(int(phase_name.split('_')[0]))

    def setPhaseScale(self, model_name, scale=1):
        self.storage[str(model_name) + '_scale'] = scale

    def getPhaseScale(self, model_name, *args, **kwargs):
        return self.storage.get(str(model_name) + '_scale', 1)

    def createCrystal_fromCifStr(self, cif_str: str):
        crystal = cryspy.Crystal.from_cif(cif_str)
        key = crystal.data_name
        self.storage[key] = crystal
        self.current_crystal[key] = key
        self.createPhase(key)
        return key

    def createEmptyCrystal(self, crystal_name, key=None):
        crystal = cryspy.Crystal(crystal_name, atom_site=cryspy.AtomSiteL())
        if key is None:
            key = crystal_name
        self.storage[key] = crystal
        self.createPhase(crystal_name, key=str(key) + '_phase')
        self.current_crystal[key] = crystal_name
        return key

    def createCell(self, key='cell'):
        cell = cryspy.Cell()
        self.storage[key] = cell
        return key

    def assignCell_toCrystal(self, cell_name, crystal_name):
        crystal = self.storage[crystal_name]
        cell = self.storage[cell_name]
        crystal.cell = cell

    def createSpaceGroup(self, key='spacegroup', name_hm_alt='P 1'):
        sg_split = name_hm_alt.split(':')
        opts = {'name_hm_alt': sg_split[0]}
        # if len(sg_split) > 1:
        #     opts['it_coordinate_system_code'] = sg_split[1]
        # try:
        #     sg = cryspy.SpaceGroup(**opts)
        # except Exception as e:
        sg = cryspy.SpaceGroup(**opts)
        # print(e)
        self.storage[key] = sg
        return key

    def getSpaceGroupSymbol(self, spacegroup_name: str, *args, **kwargs):
        sg = self.storage[spacegroup_name]
        hm_alt = getattr(sg, 'name_hm_alt')
        setting = getattr(sg, 'it_coordinate_system_code')
        if setting:
            hm_alt += ':' + setting
        return hm_alt

    def assignSpaceGroup_toCrystal(self, spacegroup_name, crystal_name):
        if not crystal_name:
            return
        crystal = self.storage[crystal_name]
        space_group: cryspy.SpaceGroup = self.storage[spacegroup_name]
        setattr(crystal, 'space_group', space_group)
        for atom in crystal.atom_site.items:
            atom.define_space_group_wyckoff(space_group.space_group_wyckoff)
            atom.form_object()

    def updateSpacegroup(self, sg_key, **kwargs):
        # This has to be done as sg.name_hm_alt = 'blah' doesn't work :-(
        sg_key = self.createSpaceGroup(key=sg_key, **kwargs)
        key = list(self.current_crystal.keys())
        if len(key) > 0:
            key = key[0]
        else:
            key = ''
        self.assignSpaceGroup_toCrystal(sg_key, key)

    def createAtom(self, atom_name, **kwargs):
        atom = cryspy.AtomSite(**kwargs)
        self.storage[atom_name] = atom
        return atom_name

    def assignAtom_toCrystal(self, atom_label, crystal_name):
        crystal = self.storage[crystal_name]
        atom = self.storage[atom_label]
        wyckoff = crystal.space_group.space_group_wyckoff
        atom.define_space_group_wyckoff(wyckoff)
        atom.form_object()
        for item in crystal.items:
            if not isinstance(item, cryspy.AtomSiteL):
                continue
            item.items.append(atom)

    def removeAtom_fromCrystal(self, atom_label, crystal_name):
        crystal = self.storage[crystal_name]
        atom = self.storage[atom_label]
        for item in crystal.items:
            if not isinstance(item, cryspy.AtomSiteL):
                continue
            idx = item.items.index(atom)
            del item.items[idx]

    def createBackground(self, background_obj):
        key = 'background'
        self.storage[key] = background_obj
        return key

    def createSetup(self, key='setup', cls_type=None):

        if cls_type is None:
            cls_type = self.type

        if cls_type == 'powder1DCW':
            setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
        elif cls_type == 'powder1DTOF':
            setup = cryspy.TOFParameters(zero=0, dtt1=self.conditions_TOF['dtt1'], dtt2=self.conditions_TOF['dtt2'],
                                         ttheta_bank=self.conditions_TOF['ttheta_bank'])
        else:
            raise AttributeError('The experiment is of an unknown type')
        self.storage[key] = setup
        if self.model is not None:
            setattr(self.model, 'setup', setup)
        return key

    def genericUpdate(self, item_key, **kwargs):
        item = self.storage[item_key]
        for key, value in kwargs.items():
            setattr(item, key, kwargs[key])

    def genericReturn(self, item_key, value_key):
        item = self.storage[item_key]
        value = getattr(item, value_key)
        return value

    def createResolution(self, cls_type=None):

        if cls_type is None:
            cls_type = self.type

        if cls_type == 'powder1DCW':
            key = 'pd_instr_resolution'
            resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
        elif cls_type == 'powder1DTOF':
            key = 'tof_profile'
            resolution = cryspy.TOFProfile(**self.conditions_TOF['resolution'])
            resolution.peak_shape = 'Gauss'
        else:
            raise AttributeError('The experiment is of an unknown type')
        self.storage[key] = resolution
        if self.model is not None:
            setattr(self.model, key, resolution)
        return key

    def updateResolution(self, key, **kwargs):
        resolution = self.storage[key]
        for r_key in kwargs.keys():
            setattr(resolution, r_key, kwargs[key])

    def powder_1d_calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """

        for key_inner in ['pd_instr_resolution', 'setup']:
            if not hasattr(self.model, key_inner):
                setattr(self.model, key_inner, self.storage[key_inner])

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value / 500.0
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array + offset

        if borg.debug:
            print('CALLING FROM Cryspy\n----------------------')
        return self.do_calc_setup(scale, this_x_array)

    def powder_1d_tof_calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        setup, tof_profile, phase, tof_background, tof_meas
        """

        for key_inner in ['tof_profile', 'setup']:
            if not hasattr(self.model, key_inner):
                try:
                    setattr(self.model, key_inner, self.storage[key_inner])
                except ValueError:
                    # Try to fix cryspy....
                    s = self.storage[key_inner]
                    cls = s.__class__
                    for idx, item in enumerate(self.model.items):
                        if isinstance(item, cls) and id(item) is not id(s):
                            self.model.items[idx] = s
                            break

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value / 500.0
            offset = self.pattern.zero_shift.raw_value

        self.model['tof_parameters'].zero = offset
        this_x_array = x_array

        if borg.debug:
            print('CALLING FROM Cryspy\n----------------------')
        return self.do_calc_setup(scale, this_x_array)

    def do_calc_setup(self, scale, this_x_array):
        if len(self.pattern.backgrounds) == 0:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.pattern.backgrounds[0].calculate(this_x_array)

        num_crys = len(self.current_crystal.keys())

        if num_crys == 0:
            return bg

        crystals = [self.storage[key] for key in self.current_crystal.keys()]
        phase_scales = [self.storage[str(key) + '_scale'] for key in self.current_crystal.keys()]
        phase_lists = []
        profiles = []
        peak_dat = []
        for crystal in crystals:
            phasesL = cryspy.PhaseL()
            idx = [idx for idx, item in enumerate(self.phases.items) if item.label == crystal.data_name][0]
            phasesL.items.append(self.phases.items[idx])
            phase_lists.append(phasesL)
            profile, peak = _do_run(self.model, self.polarized, this_x_array, crystal, phasesL)
            profiles.append(profile)
            peak_dat.append(peak)
        # pool = mp.ProcessPool(num_crys)
        # print("\n\nPOOL = " + str(pool))
        # result = pool.amap(functools.partial(_do_run, self.model, self.polarized, this_x_array), crystals, phase_lists)
        # while not result.ready():
        #     time.sleep(0.01)
        # obtained = result.get()
        # profiles, peak_dat = zip(*obtained)
        # else:
        #     raise ArithmeticError

        # Do this for now
        x_str = 'ttheta'
        if self.type == 'powder1DTOF':
            x_str = 'time'
        if self.polarized:
            # TODO *REPLACE PLACEHOLDER FN*
            dependents, additional_data = self.polarized_update(lambda up, down: up + down, crystals, profiles,
                                                                peak_dat, phase_scales, x_str)
        else:
            dependents, additional_data = self.nonPolarized_update(crystals, profiles, peak_dat, phase_scales, x_str)
        self.additional_data.update(additional_data)
        self.additional_data['global_scale'] = scale
        self.additional_data['background'] = bg
        self.additional_data['ivar_run'] = this_x_array
        self.additional_data['components'] = dependents
        self.additional_data['phase_names'] = list(additional_data.keys())
        self.additional_data['type'] = self.type

        # just the sum of all phases
        dependent_output = scale * np.sum(dependents, axis=0) + bg

        if borg.debug:
            print(f"y_calc: {dependent_output}")
        return dependent_output

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        res = np.zeros_like(x_array)
        self.additional_data['ivar'] = res
        if self.type == 'powder1DCW':
            return self.powder_1d_calculate(x_array)
        if self.type == 'powder1DTOF':
            return self.powder_1d_tof_calculate(x_array)
        return res

    def get_hkl(self, x_array: np.ndarray = None, idx: int = 0, phase_name=None) -> dict:

        # Do we need to re-run a calculation to get the HKL's
        do_run = False
        old_x = self.additional_data.get('ivar', np.array(()))
        if not np.array_equal(old_x, x_array):
            do_run = True
        if do_run and x_array is not None:
            _ = self.calculate(x_array)

        # Collate and return
        if phase_name is None:
            known_phases = list(self.current_crystal.values())
            phase_name = known_phases[idx]
        phase_data = self.additional_data.get(phase_name, {})
        return phase_data.get('hkl', {
            'ttheta': np.array([]),
            'h': np.array([]),
            'k': np.array([]),
            'l': np.array([])
        })

    @staticmethod
    def nonPolarized_update(crystals, profiles, peak_dat, scales, x_str):
        dependent = np.array([profile.intensity_total for profile in profiles])

        output = {}
        for idx, profile in enumerate(profiles):
            output.update({
                crystals[idx].data_name: {
                    'hkl':           {
                        x_str: getattr(peak_dat[idx], 'numpy_' + x_str),
                        'h':   peak_dat[idx].numpy_index_h,
                        'k':   peak_dat[idx].numpy_index_k,
                        'l':   peak_dat[idx].numpy_index_l,
                    },
                    'profile':       scales[idx] * dependent[idx, :],
                    'components':    {
                        'total': dependent[idx, :]
                    },
                    'profile_scale': scales[idx],
                }
            })
        return dependent, output

    @staticmethod
    def polarized_update(func, crystals, profiles, peak_dat, scales, x_str):
        up = np.array([profile.intensity_up_total for profile in profiles])
        down = np.array([profile.intensity_down_total for profile in profiles])
        dependent = np.array([func(u, d) for u, d in zip(up, down)])

        output = {}
        for idx, profile in enumerate(profiles):
            output.update({
                crystals[idx].data_name: {
                    'hkl':           {
                        x_str: getattr(peak_dat[idx], 'numpy_' + x_str),
                        'h':   peak_dat[idx].numpy_index_h,
                        'k':   peak_dat[idx].numpy_index_k,
                        'l':   peak_dat[idx].numpy_index_l,
                    },
                    'profile':       scales[idx] * dependent[idx, :],
                    'components':    {
                        'total': dependent[idx, :],
                        'up': up[idx, :],
                        'down': down[idx, :]
                    },
                    'profile_scale': scales[idx],
                    'func': func
                }
            })
        return dependent, output

    def get_phase_components(self, phase_name):
        data = None
        if phase_name in self.additional_data['phase_names']:
            data = self.additional_data[phase_name].copy()
        return data


def _do_run(model, polarized, x_array, crystals, phase_list, ):
    idx = [idx for idx, item in enumerate(model.items) if isinstance(item, cryspy.PhaseL)][0]
    model.items[idx] = phase_list
    result1 = model.calc_profile(x_array, [crystals], flag_internal=True, flag_polarized=polarized)
    result2 = model.d_internal_val['peak_' + crystals.data_name]
    return result1, result2
