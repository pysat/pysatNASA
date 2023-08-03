# -*- coding: utf-8 -*-
"""Module for the MAVEN kp instrument.
Created by: Teresa Esman, NPP at GSFC
Last editted: Jun 2, 2023
    May 12, 2023

Supports the Key parameter (kp) data from multiple instruments onboard the Mars Atmosphere and Volatile Evolution (MAVEN) satellite.

Accesses local data in CDF format.
Downlaods from CDAWeb.

Properties
----------
platform
    'mvn'
name
    'kp'
tag
    None supported

Warnings
--------

- Only supports level-2 sunstate 1 second data.


Examples
--------
::

    import pysat
    from pysat.utils import registry
    registry.register_by_module(pysatNASA.instruments)


    kp = pysat.Instrument(platform='MAVEN', name='kp')
    kp.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    kp.load(2020, 1, use_header = True)
"""

import datetime as dt
import functools
import numpy as np
import cdflib
import pysat
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import mvn as mm_mvn

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'mvn'
name = 'kp'
tags = {'': ''}
inst_ids = {'': ['']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}
_test_load_opt = {'': {'': {'keep_original_names': True}}}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_mvn, name=name)


def clean(self):
    """Clean MAVEN kp data to the specified level.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'. Method is
        not called by pysat if clean_level is None or 'none'.


    """
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the MAVEN and pysat methods

# Set the list_files routine
fname = ''.join(('mvn_insitu_kp-4sec_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}_r{revision:02d}.cdf'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
basic_tag = {'remote_dir': '/pub/data/maven/insitu/kp-4sec/cdfs/{year:04d}/{month:02d}',
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def filter_metadata(meta_dict):
    """Filter kp metadata to remove warnings during loading.

    Parameters
    ----------
    meta_dict : dict
        Dictionary of metadata from file

    Returns
    -------
    meta_dict : dict
        Filtered kp metadata

    """
    vars = ['LPW_Electron_density',
    'LPW_Electron_density_min',
    'LPW_Electron_density_max',
    'LPW_Electron_temperature',
    'LPW_Electron_temperature_min',
    'LPW_Electron_temperature_max',
    'LPW_Spacecraft_potential',
    'LPW_Spacecraft_potential_min',
    'LPW_Spacecraft_potential_max',
    'LPW_E_field_wave_power_2_100',
    'LPW_E_field_wave_power_2_100_data_quality',
    'LPW_E_field_wave_power_100_800',
    'LPW_E_field_wave_power_100_800_data_quality',
    'LPW_E_field_wave_power_800_1000',
    'LPW_E_field_wave_power_800_1000_data_quality',
    'LPW_EUV_irradiance_pt1_7',
    'LPW_EUV_irradiance_pt1_7_data_quality',
    'LPW_EUV_irradiance_17_22',
    'LPW_EUV_irradiance_17_22_data_quality',
    'LPW_EUV_irradiance_lyman_alpha',
    'LPW_EUV_irradiance_lyman_alpha_data_quality',
    'SWEA_Electron_density',
    'SWEA_Electron_density_quality',
    'SWEA_Electron_temperature',
    'SWEA_Electron_temperature_quality',
    'SWEA_Electron_parallel_flux_5_100',
    'SWEA_Electron_parallel_flux_5_100_data_quality',
    'SWEA_Electron_parallel_flux_100_500',
    'SWEA_Electron_parallel_flux_100_500_data_quality',
    'SWEA_Electron_parallel_flux_500_1000',
    'SWEA_Electron_parallel_flux_500_1000_data_quality',
    'SWEA_Electron_anti_parallel_flux_5_100',
    'SWEA_Electron_anti_parallel_flux_5_100_data_quality',
    'SWEA_Electron_anti_parallel_flux_100_500',
    'SWEA_Electron_anti_parallel_flux_100_500_data_quality',
    'SWEA_Electron_anti_parallel_flux_500_1000',
    'SWEA_Electron_anti_parallel_flux_500_1000_data_quality',
    'SWEA_Electron_spectrum_shape',
    'SWEA_Electron_spectrum_shape_data_quality',
    'SWIA_Hplus_density',
    'SWIA_Hplus_density_data_quality',
    'SWIA_Hplus_flow_velocity_MSO',
    'SWIA_Hplus_flow_velocity_MSO_data_quality',
    'SWIA_Hplus_temperature',
    'SWIA_Hplus_temperature_data_quality',
    'SWIA_dynamic_pressure',
    'SWIA_dynamic_pressure_data_quality',
    'STATIC_Quality',
    'STATIC_Hplus_density',
    'STATIC_Hplus_density_data_quality',
    'STATIC_Oplus_density',
    'STATIC_Oplus_density_data_quality',
    'STATIC_O2plus_density',
    'STATIC_O2plus_density_data_quality',
    'STATIC_Hplus_temperature',
    'STATIC_Hplus_temperature_data_quality',
    'STATIC_Oplus_temperature',
    'STATIC_Oplus_temperature_data_quality',
    'STATIC_O2plus_temperature',
    'STATIC_O2plus_temperature_data_quality',
    'STATIC_O2plus_flow_velocity_MAVEN_APP',
    'STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality',
    'STATIC_O2plus_flow_velocity_MSO',
    'STATIC_O2plus_flow_velocity_MSO_data_quality',
    'STATIC_Hplus_omni_directional_flux',
    'STATIC_Hplus_characteristic_energy',
    'STATIC_Hplus_characteristic_energy_DQ',
    'STATIC_HEplus_omni_directional_flux',
    'STATIC_HEplus_characteristic_energy',
    'STATIC_HEplus_characteristic_energy_DQ',
    'STATIC_Oplus_omni_directional_flux',
    'STATIC_Oplus_characteristic_energy',
    'STATIC_Oplus_characteristic_energy_DQ',
    'STATIC_O2plus_omni_directional_flux',
    'STATIC_O2plus_characteristic_energy',
    'STATIC_O2plus_characteristic_energy_DQ',
    'STATIC_Hplus_characteristic_direction_MSO',
    'STATIC_Hplus_characteristic_angular_width',
    'STATIC_Hplus_characteristic_angular_width_DQ',
    'STATIC_dominant_pickup_ion_characteristic_direction_MSO',
    'STATIC_dominant_pickup_ion_characteristic_angular_width',
    'STATIC_dominant_pickup_ion_characteristic_angular_width_DQ',
    'SEP_Ion_Energy_Flux_30_1000_FOV_1F',
    'SEP_Ion_Energy_Flux_30_1000_FOV_1F_data_quality',
    'SEP_Ion_Energy_Flux_30_1000_FOV_1R',
    'SEP_Ion_Energy_Flux_30_1000_FOV_1R_data_quality',
    'SEP_Ion_Energy_Flux_30_1000_FOV_2F',
    'SEP_Ion_Energy_Flux_30_1000_FOV_2F_data_quality',
    'SEP_Ion_Energy_Flux_30_1000_FOV_2R',
    'SEP_Ion_Energy_Flux_30_1000_FOV_2R_data_quality',
    'SEP_Electron_Energy_Flux_30_300_FOV_1F',
    'SEP_Electron_Energy_Flux_30_300_FOV_1F_data_quality',
    'SEP_Electron_Energy_Flux_30_300_FOV_1R',
    'SEP_Electron_Energy_Flux_30_300_FOV_1R_data_quality',
    'SEP_Electron_Energy_Flux_30_300_FOV_2F',
    'SEP_Electron_Energy_Flux_30_300_FOV_2F_data_quality',
    'SEP_Electron_Energy_Flux_30_300_FOV_2R',
    'SEP_Electron_Energy_Flux_30_300_FOV_2R_data_quality',
    'SEP_Look_direction_1F_MSO',
    'SEP_Look_direction_1R_MSO',
    'SEP_Look_direction_2F_MSO',
    'SEP_Look_direction_2R_MSO',
    'MAG_field_MSO',
    'MAG_field_MSO_data_quality',
    'MAG_field_GEO',
    'MAG_field_GEO_data_quality',
    'MAG_field_RMS_deviation',
    'MAG_field_RMS_deviation_data_quality',
    'NGIMS_He_density',
    'NGIMS_He_density_precision',
    'NGIMS_He_density_data_quality',
    'NGIMS_O_density',
    'NGIMS_O_density_precision',
    'NGIMS_O_density_data_quality',
    'NGIMS_CO_density',
    'NGIMS_CO_density_precision',
    'NGIMS_CO_density_data_quality',
    'NGIMS_N2_density',
    'NGIMS_N2_density_precision',
    'NGIMS_N2_density_data_quality',
    'NGIMS_NO_density',
    'NGIMS_NO_density_precision',
    'NGIMS_NO_density_data_quality',
    'NGIMS_Ar_density',
    'NGIMS_Ar_density_precision',
    'NGIMS_Ar_density_data_quality',
    'NGIMS_CO2_density',
    'NGIMS_CO2_density_precision',
    'NGIMS_CO2_density_data_quality',
    'NGIMS_Ion_density_32plus',
    'NGIMS_Ion_density_precision_32plus',
    'NGIMS_Ion_density_data_quality_32plus',
    'NGIMS_Ion_density_44plus',
    'NGIMS_Ion_density_precision_44plus',
    'NGIMS_Ion_density_data_quality_44plus',
    'NGIMS_Ion_density_30plus',
    'NGIMS_Ion_density_precision_30plus',
    'NGIMS_Ion_density_data_quality_30plus',
    'NGIMS_Ion_density_16plus',
    'NGIMS_Ion_density_precision_16plus',
    'NGIMS_Ion_density_data_quality_16plus',
    'NGIMS_Ion_density_28plus',
    'NGIMS_Ion_density_precision_28plus',
    'NGIMS_Ion_density_data_quality_28plus',
    'NGIMS_Ion_density_12plus',
    'NGIMS_Ion_density_precision_12plus',
    'NGIMS_Ion_density_data_quality_12plus',
    'NGIMS_Ion_density_17plus',
    'NGIMS_Ion_density_precision_17plus',
    'NGIMS_Ion_density_data_quality_17plus',
    'NGIMS_Ion_density_14plus',
    'NGIMS_Ion_density_precision_14plus',
    'NGIMS_Ion_density_data_quality_14plus',
    'SPICE_spacecraft_GEO',
    'SPICE_spacecraft_MSO',
    'SPICE_spacecraft_longitude_GEO',
    'SPICE_spacecraft_latitude_GEO',
    'SPICE_spacecraft_sza',
    'SPICE_spacecraft_local_time',
    'SPICE_spacecraft_altitude',
    'SPICE_spacecraft_attitude_GEO',
    'SPICE_spacecraft_attitude_MSO',
    'SPICE_app_attitude_GEO',
    'SPICE_app_attitude_MSO',
    'SPICE_Orbit_Number',
    'Inbound_Outbound_Flag',
    'SPICE_Mars_season',
    'SPICE_Mars_Sun_distance',
    'SPICE_Subsolar_Point_longitude_GEO',
    'SPICE_Subsolar_Point_latitude_GEO',
    'SPICE_Sub_Mars_Point_longitude',
    'SPICE_Sub_Mars_Point_latitude',
    'Rotation_matrix_IAU_MARS_MAVEN_MSO',
    'Rotation_matrix_SPACECRAFT_MAVEN_MSO']

    for var in vars:
        if var in meta_dict:
            meta_dict[var]['FillVal'] = np.nan

    # Deal with string arrays
    for var in meta_dict.keys():
        if 'Var_Notes' in meta_dict[var]:
            meta_dict[var]['Var_Notes'] = ' '.join(pysat.utils.listify(
                meta_dict[var]['Var_Notes']))

    return meta_dict

def init(self):
    """Initialize the Instrument object with instrument specific values.
    Runs once upon instantiation.
    Parameters
    -----------
    self : pysat.Instrument
        Instrument class object
    """

    pysat.logger.info(mm_mvn.ackn_str)
    self.acknowledgements = mm_mvn.ackn_str
    self.references = mm_mvn.references

    return

# Set the load routine
load = functools.partial(cdw.load, epoch_name='epoch',
                         pandas_format=pandas_format, use_cdflib=True)
