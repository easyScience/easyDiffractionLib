__author__ = "github.com/wardsimon"
__version__ = "0.0.2"


import cryspy
import warnings
from easyCore import np, borg
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
        self.background = None
        self.hkl_dict = {
            'ttheta': np.empty(0),
            'h': np.empty(0),
            'k': np.empty(0),
            'l': np.empty(0)
        }
        self.storage = {}
        self.current_crystal = {}
        self.model = None

    @property
    def cif_str(self):
        key = list(self.current_crystal.keys())[0]
        return self.storage[key].to_cif()

    @cif_str.setter
    def cif_str(self, value):
        self.createCrystal_fromCifStr(value)

    def createModel(self, model_id, model_type=None):
        self.model = cryspy.Pd(background=cryspy.PdBackgroundL(), phase=cryspy.PhaseL())

    def createPhase(self, crystal_name, key='phase'):
        phase = cryspy.Phase(label=crystal_name, scale=1, igsize=0)
        self.storage[key] = phase
        return key

    def assignPhase(self, model_name, phase_name):
        phase = self.storage[phase_name]
        self.model.phase.items.append(phase)

    def removePhase(self, model_name, phase_name):
        phase = self.storage[phase_name]
        self.model.phase.items.pop(phase)

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
        if len(sg_split) > 1:
            opts['it_coordinate_system_code'] = sg_split[1]
        try:
            sg = cryspy.SpaceGroup(**opts)
        except Exception as e:
            sg = cryspy.SpaceGroup(name_hm_alt=sg_split[0])
            print(e)
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

    def createSetup(self, key='setup'):
        setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
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

    def createResolution(self):
        key = 'pd_instr_resolution'
        resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
        self.storage[key] = resolution
        if self.model is not None:
            setattr(self.model, 'pd_instr_resolution', resolution)
        return key

    def updateResolution(self, key, **kwargs):
        resolution = self.storage[key]
        for r_key in kwargs.keys():
            setattr(resolution, r_key, kwargs[key])

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """

        for key_inner, key_outer in zip(['pd_instr_resolution', 'setup'], ['resolution', 'setup']):
            if not hasattr(self.model, key_inner):
                setattr(self.model, key_inner, self.storage[key_outer])

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value / 500.0
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array + offset

        if borg.debug:
            print('CALLING FROM Cryspy\n----------------------')
        # USe the default for now
        crystal = self.storage[list(self.current_crystal.keys())[-1]]

        if len(self.pattern.backgrounds) == 0:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.pattern.backgrounds[0].calculate(this_x_array)

        if crystal is None:
            return bg

        profile = self.model.calc_profile(this_x_array, [crystal], True, False)
        self.hkl_dict = {
            'ttheta': self.model.d_internal_val['peak_' + crystal.data_name].numpy_ttheta,
            'h': self.model.d_internal_val['peak_'+crystal.data_name].numpy_index_h,
            'k': self.model.d_internal_val['peak_'+crystal.data_name].numpy_index_k,
            'l': self.model.d_internal_val['peak_'+crystal.data_name].numpy_index_l,
        }
        res = scale * np.array(profile.intensity_total) + bg
        if borg.debug:
            print(f"y_calc: {res}")
        return res

    def get_hkl(self, tth: np.array = None) -> dict:

        hkl_dict = self.hkl_dict

        if tth is not None:
            # crystal = cryspy.Crystal.from_cif(self.cif_str)
            # phase_list = cryspy.PhaseL()
            # phase = cryspy.Phase(label=crystal.data_name, scale=1, igsize=0)
            # phase_list.items.append(phase)
            # setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
            # background = cryspy.PdBackgroundL()
            # resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
            # pd = cryspy.Pd(setup=setup, resolution=resolution, phase=phase_list, background=background)
            crystal = self.storage[list(self.current_crystal.keys())[-1]]
            _ = self.model.calc_profile(tth, [crystal], True, False)

            hkl_dict = {
                'ttheta': self.model.d_internal_val['peak_' + crystal.data_name].numpy_ttheta,
                'h': self.model.d_internal_val['peak_' + crystal.data_name].numpy_index_h,
                'k': self.model.d_internal_val['peak_' + crystal.data_name].numpy_index_k,
                'l': self.model.d_internal_val['peak_' + crystal.data_name].numpy_index_l,
            }

        return hkl_dict