#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 11:21:01 2023

@author: tesman
"""
import datetime as dt
import pysat
import xarray as xr
import pandas as pd

ackn_str = ' '.join(('Jakosky, B.M., Lin, R.P., Grebowsky, J.M. et al. The Mars Atmosphere and Volatile Evolution',
                        '(MAVEN) Mission. Space Sci Rev 195, 3–48 (2015). https://doi.org/10.1007/s11214-015-0139-x'))
references =  ' '.join(('Connerney, J., and P. Lawton, MAVEN MAG PDS Archive SIS - This document ',
   'describes the format and content of the MAVEN Magnetometer (MAG) Planetary', 
   'Data System (PDS) data archive. It includes descriptions of the Standard',
   'Data Products and associated metadata, and the volume archive format,',
   'content, and generation pipeline.',' ',
   'Connerney, J.E.P.; Espley, J.; Lawton, P.; Murphy, S.; Odom, J.; Oliversen, R.;', 
   'and Sheppard, D., The MAVEN Magnetic Field Investigation, Space Sci Rev,', 
   'Vol 195, Iss 1-4, pp.257-291, 2015. doi:10.1007/s11214-015-0169-4',
   'Jakosky, B.M., Lin, R.P., Grebowsky, J.M. et al. The Mars Atmosphere and Volatile Evolution',
   '(MAVEN) Mission. Space Sci Rev 195, 3–48 (2015). https://doi.org/10.1007/s11214-015-0139-x'))

def scrub_mvn_mag(data):
    """Make data labels and epoch compatible with SPASE and pysat.
    Parameters
    ----------
    data : pandas.Dataframe()
        Metadata object containing the default metadata loaded from the sav files.
    Returns
    -------
    data : pandas.Dataframe()
        Replacement data object with compatible variable names and epoch.
    """
    
    UTC = data['epoch'].values / 1e9 #UTC time from 01-Jan-2000 12:00:00.000, nanoseconds    
    unix_time = UTC + 946728000
    array_size = len(unix_time)
    pdata = pd.DataFrame(index = unix_time)
    for key in data.keys(): #For one dimensional arrays
        try: 
            if len(data[key]) == array_size and key not in {'OB_B','POSN','OB_BDPL'}:
                   pdata[key] = data[key]
        except TypeError: 
               pass
    
    for key in data.keys(): #For three-dimensional arrays
        for coord in {'x','y','z'}:
            try:
                if len(data[key]) == array_size and key in {'OB_B','POSN','OB_BDPL'}:
                    if coord == 'x': ind = 0
                    if coord == 'y': ind = 1
                    if coord == 'z': ind = 2
                    pdata[key+'_'+coord] = data[key].values[:,ind]
            except TypeError:
                pass
                
    xdata = xr.Dataset(pdata) #Switch to xarray type
    data = xdata.rename(dim_0 = 'time')
    return data
   
    
def generate_header(data):
    """Generate the meta header info for mvn mag.  
    
    Parameters
    ----------
    inst_id : str
        The VID of the associated dataset.
    epoch : dt.datetime
        The epoch of the datafile.  Corresponds to the first data point.
    Returns
    -------
    header : dict
        A dictionary compatible with the pysat.meta_header format.  Top-level
        metadata for the file.
        
        
        Global attributes are used to provide information about the data set as an entity. Together with variables and variable attributes, the global attributes make the data correctly and independently usable by someone not connected with the instrument team, and hence, a good archive product. The global attributes are also used by the CDAWeb Display and Retrieval system.

The required Global Attributes are listed here with example values. Note that CDF attributes are case-sensitive and must exactly follow what is shown here. Additional Global attributes can be defined but they must start with a letter and can otherwise contain letters, numbers and the unscore character (no other special characters allowed). See Global Attribute Definitions for the full set of defined Global Attributes.

     ATTRIBUTE                              EXAMPLE VALUE
--------------------------------------------------------------------

     "Project"                     { "ISTP>International " - 
                                     "Solar-Terrestrial Physics" }.
     
     This attribute identifies the name of the project and indicates ownership. 
     For ISTP missions and investigations, the value used is "ISTP>International 
     Solar-Terrestrial Physics". For the Cluster mission, the value is "STSP Cluster>Solar 
     Terrestrial Science Programmes, Cluster". 
     
     
     
     "Source_name"                 { "GEOTAIL>Geomagnetic Tail" }.
     
     This attribute identifies the mission or investigation that contains the sensors. 
     For ISTP, this is the mission name for spacecraft missions or the investigation name for 
     ground-based or theory investigations. Both a long name and a short name are provided. 
     This attribute should be single valued. 
     
     
     "Discipline"                  { "Space Physics>Magnetospheric Science" }.
     "Data_type"                   { "K0>Key Parameter" }.
     "Descriptor"                  { "EPI>Energetic Particles" -
                                     " and Ion Composition" }.
     This attribute identifies the name of the instrument or sensor 
     that collected the data
     
     "Data_version"                { "1" }.
     "Logical_file_id"             { "GE_K0_EPI_19920908_V01" }.
     "PI_name"                     { "D. Williams" }.
     "PI_affiliation"              { "JHU/APL" }.
     "TEXT"                        { "reference to journal article, URL address" }.
    
     This attribute is an NSSDC standard global attribute which is a 
     text description of the experiment whose data is included in the CDF.
     A reference to a journal article(s) or to a World Wide Web page describing 
     the experiment is essential, and constitutes the minimum requirement. 
     A written description of the data set is also desirable. This attribute 
     can have as many entries as necessary to contain the desired information.
     
     "Instrument_type"             { "Magnetic Fields (space)" }.
     "Mission_group"               { "Geotail" }.
     "Logical_source"              { "GE_K0_EPI" }.
     "Logical_source_description"  { "Geotail Magnetic Field Key Parameters" }.

--------------------------------------------------------------------
        
        Medium Energy Proton and Electron Detector (MEPED)
    """
    header = {'Project': data.Project,
              'Source_name': data.Source_name,
              'Discipline':data.Discipline,
              'Data_type': data.Data_type, 
              'Descriptor': data.Descriptor,
              'Data_version': '',
              'Logical_file_id': data.Logical_file_id,
              'PI_name': data.PI_name,
              'PI_affiliation': data.PI_affiliation,
              'TEXT': data.TEXT,
              'Rules_of_use': data.Rules_of_use,
              'Instrument_type': data.Instrument_type,
              'Mission_group': data.Mission_group,
              'Logical_source': data.Logical_source,
              'Logical_source_description': data.Logical_source_description,
              'DOI':'10.17189/1414178',
              'File_naming_convention': data.File_naming_convention,
              'Time_resolution': data.Time_resolution, 
              'Generated_by': data.Generated_by,
              'Generation_date': '',
              'Generation_datetime': dt.datetime.today().isoformat(),
              'Acknowledgement': ackn_str,
              'TITLE': data.TITLE,
              'spase_DatasetResourceID': {'spase://NASA/NumericalData',
                                             '/MAVEN/MAG/SunState/Level2',
                                             '/PT1S' },
              'LINK_TEXT': data.LINK_TEXT,
              'LINK_TITLE': data.LINK_TITLE,
              'HTTP_LINK': data.HTTP_LINK}

    return header


def generate_metadata(header_data,data):
    """Generate metadata object for mvn mag data compatible with SPASE and pysat.
    Parameters
    ----------
    header_data : dict
        A dictionary compatible with the pysat.meta_header format.  Required to
        properly initialize metadata.
    Returns
    -------
    metadata : pandas.Dataframe()
        Contains data compatible with SPASE standards to initialize pysat.Meta.
        
        Variables:
            epoch, DDAY, OB_B, OB_B_range, POSN, OB_BDPL, OB_BDPL_range,compno_3, OB_B_labl, POSN_labl, OB_BDPL_labl
    """
    meta = pysat.Meta(header_data=header_data)

    meta['time'] = {meta.labels.name: 'Unix time',
                   meta.labels.units: 'seconds',
                   meta.labels.min_val: float(data.epoch.VALIDMIN)/1e9 +946728000,
                   meta.labels.max_val: float(data.epoch.VALIDMAX)/1e9 +946728000,
                   meta.labels.desc: data.epoch.CATDESC,
                   meta.labels.fill_val: float(data.epoch.FILLVAL)}
    
    meta['DDAY'] ={meta.labels.name: data.DDAY.FIELDNAM,
                   meta.labels.units: data.DDAY.UNITS,
                   meta.labels.min_val: float(data.DDAY.VALIDMIN),
                   meta.labels.max_val: float(data.DDAY.VALIDMAX),
                   meta.labels.desc: data.DDAY.CATDESC,
                   meta.labels.fill_val: float(data.DDAY.FILLVAL)}
   
    meta['OB_B_x']={meta.labels.name: 'Outboard Magnetic Field x',
                    meta.labels.units: data.OB_B.UNITS,
                    meta.labels.desc: data.OB_B.CATDESC,
                    meta.labels.min_val: float(data.OB_B.VALIDMIN),
                    meta.labels.max_val: float(data.OB_B.VALIDMAX),
                    meta.labels.fill_val: float(data.OB_B.FILLVAL)}
    meta['OB_B_y']={meta.labels.name: 'Outboard Magnetic Field y',
                    meta.labels.units: data.OB_B.UNITS,
                    meta.labels.desc: data.OB_B.CATDESC,
                    meta.labels.min_val: float(data.OB_B.VALIDMIN),
                    meta.labels.max_val: float(data.OB_B.VALIDMAX),
                    meta.labels.fill_val: float(data.OB_B.FILLVAL)}
    meta['OB_B_z']={meta.labels.name: 'Outboard Magnetic Field z',
                    meta.labels.units: data.OB_B.UNITS,
                    meta.labels.desc: data.OB_B.CATDESC,
                    meta.labels.min_val: float(data.OB_B.VALIDMIN),
                    meta.labels.max_val: float(data.OB_B.VALIDMAX),
                    meta.labels.fill_val: float(data.OB_B.FILLVAL)}
    
    meta['OB_B_range']={meta.labels.name: data.OB_B_range.long_name,
                        meta.labels.units: data.OB_B_range.UNITS,
                        meta.labels.desc: data.OB_B_range.CATDESC,
                        meta.labels.min_val: float(data.OB_B_range.VALIDMIN),
                        meta.labels.max_val: float(data.OB_B_range.VALIDMAX),
                        meta.labels.fill_val: float(data.OB_B_range.FILLVAL)}
    
    meta['POSN_x']={meta.labels.name: 'Spacecraft Position x',
                    meta.labels.units: data.POSN.UNITS,
                    meta.labels.desc: 'Spacecraft position x',
                    meta.labels.min_val: float(data.POSN.VALIDMIN),
                    meta.labels.max_val: float(data.POSN.VALIDMAX),
                    meta.labels.fill_val:float(data.POSN.FILLVAL)}
    meta['POSN_y']={meta.labels.name: 'Spacecraft Position y',
                    meta.labels.units: data.POSN.UNITS,
                    meta.labels.desc: 'Spacecraft position y',
                    meta.labels.min_val: float(data.POSN.VALIDMIN),
                    meta.labels.max_val: float(data.POSN.VALIDMAX),
                    meta.labels.fill_val:float(data.POSN.FILLVAL)}
    meta['POSN_z']={meta.labels.name: 'Spacecraft Position z',
                    meta.labels.units: data.POSN.UNITS,
                    meta.labels.desc: 'Spacecraft position z',
                    meta.labels.min_val: float(data.POSN.VALIDMIN),
                    meta.labels.max_val: float(data.POSN.VALIDMAX),
                    meta.labels.fill_val:float(data.POSN.FILLVAL)}
    
    meta['OB_BDPL_x']={meta.labels.name: data.OB_BDPL_labl.values[0],
                       meta.labels.units: data.OB_BDPL.UNITS,
                       meta.labels.desc: data.OB_BDPL.CATDESC + ' x',
                       meta.labels.min_val: float(data.OB_BDPL.VALIDMIN),
                       meta.labels.max_val: float(data.OB_BDPL.VALIDMAX),
                       meta.labels.fill_val: float(data.OB_BDPL.FILLVAL)}
    meta['OB_BDPL_y']={meta.labels.name: data.OB_BDPL_labl.values[1],
                       meta.labels.units: data.OB_BDPL.UNITS,
                       meta.labels.desc: data.OB_BDPL.CATDESC + ' y',
                       meta.labels.min_val: float(data.OB_BDPL.VALIDMIN),
                       meta.labels.max_val: float(data.OB_BDPL.VALIDMAX),
                       meta.labels.fill_val: float(data.OB_BDPL.FILLVAL)}
    meta['OB_BDPL_z']={meta.labels.name: data.OB_BDPL_labl.values[2],
                       meta.labels.units: data.OB_BDPL.UNITS,
                       meta.labels.desc: data.OB_BDPL.CATDESC + ' z',
                       meta.labels.min_val: float(data.OB_BDPL.VALIDMIN),
                       meta.labels.max_val: float(data.OB_BDPL.VALIDMAX),
                       meta.labels.fill_val: float(data.OB_BDPL.FILLVAL)}
    
    meta['OB_BDPL_range']={meta.labels.name: data.OB_BDPL_range.FIELDNAM,
                           meta.labels.desc: data.OB_BDPL_range.CATDESC,
                           meta.labels.min_val: float(data.OB_BDPL.VALIDMIN),
                           meta.labels.max_val: float(data.OB_BDPL.VALIDMAX),
                           meta.labels.fill_val: float(data.OB_BDPL.FILLVAL),
                           meta.labels.units: data.OB_BDPL.UNITS}
     
    return meta

"""Provides metadata specific routines for MGS KP data."""
def scrub_mvn_kp(data):
    """Make data labels and epoch compatible with SPASE and pysat.
    Parameters
    ----------
    data : pandas.Dataframe()
        Metadata object containing the default metadata loaded from the sav files.
    Returns
    -------
    data : pandas.Datafram()
        Replacement data object with compatible variable names and epoch.
    """
   
    # Now we make our Epoch variable
    unix_time = data['epoch'].values/1e3 - 62167204800 #originally time from 0-0-0 0:00:00.000 ms  

    #KP data from the MAVEN SDC is in the format yyyy-mm-ddThh:mm:ss    
    array_size = len(unix_time)
    pdata = pd.DataFrame(index = unix_time)
    p2data = pd.DataFrame(index = unix_time)
    p3data = pd.DataFrame(index = unix_time)
    for key in data.keys():
        try:
            if len(data[key]) == array_size and key not in {'SWIA_Hplus_flow_velocity_MSO','SWIA_Hplus_flow_velocity_MSO_data_quality',
                                                            'SWIA_Hplus_flow_velocity_MSO_dq_labl', 'STATIC_O2plus_flow_velocity_MAVEN_APP',
                                                            'STATIC_O2plus_flow_velocity_MAVEN_APP_labl', 'STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality',
                                                            'SPICE_spacecraft_GEO',
                                                            'STATIC_O2plus_flow_velocity_MSO','MAG_field_GEO','MAG_field_MSO_data_quality',
                                                            'STATIC_O2plus_flow_velocity_MSO_data_quality',
                                                            'SPICE_app_attitude_MSO','SEP_Look_direction_1R_MSO',
                                                            'STATIC_Hplus_characteristic_direction_MSO',
                                                            'STATIC_dominant_pickup_ion_characteristic_direction_MSO',
                                                            'MAG_field_MSO_dq_labl','MAG_field_MSO','MAG_field_GEO_labl', 'SEP_Look_direction_1F_MSO',
                                                            'MAG_field_GEO_dq_labl','SEP_Look_direction_2F_MSO','MAG_field_GEO_data_quality',
                                                            'SPICE_spacecraft_GEO_labl','SEP_Look_direction_2R_MSO',
                                                            'SPICE_spacecraft_MSO_labl','SPICE_spacecraft_MSO','SPICE_spacecraft_attitude_MSO',
                                                            'SPICE_spacecraft_attitude_GEO_labl','SPICE_spacecraft_attitude_GEO',
                                                            'SPICE_spacecraft_attitude_MSO_labl','SPICE_app_attitude_GEO',
                                                            'Rotation_matrix_SPACECRAFT_MAVEN_MSO','Rotation_matrix_IAU_MARS_MAVEN_MSO'}:
                    if pdata.shape[1] < 100:
                        pdata[key] = data[key]
                    else: 
                        p2data[key] = data[key]
        except TypeError: 
               pass
    
    for key in data.keys():
        for coord in {'x','y','z'}:
            try:
                if len(data[key]) == array_size and key in {'SWIA_Hplus_flow_velocity_MSO','SWIA_Hplus_flow_velocity_MSO_data_quality',
                                                            'STATIC_O2plus_flow_velocity_MAVEN_APP','STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality',
                                                            'SPICE_spacecraft_GEO','STATIC_O2plus_flow_velocity_MSO',
                                                            'STATIC_O2plus_flow_velocity_MSO_dq_labl','MAG_field_GEO',
                                                            'STATIC_Hplus_MSO_characteristic_direction_labl','MAG_field_GEO_data_quality',
                                                            'MAG_field_MSO_data_quality','MAG_field_MSO',
                                                            'STATIC_O2plus_flow_velocity_MSO_data_quality','SPICE_app_attitude_MSO',
                                                            'SEP_Look_direction_1R_MSO',
                                                            'STATIC_Hplus_characteristic_direction_MSO',
                                                            'STATIC_dominant_pickup_ion_characteristic_direction_MSO',
                                                            'SEP_Look_direction_1F_MSO','SEP_Look_direction_2F_MSO','SEP_Look_direction_2R_MSO',
                                                            'SPICE_spacecraft_MSO','SPICE_spacecraft_attitude_MSO',
                                                            'SPICE_spacecraft_attitude_GEO_labl','SPICE_spacecraft_attitude_GEO',
                                                            'SPICE_spacecraft_attitude_MSO_labl','SPICE_app_attitude_GEO'}:
                    if coord == 'x': ind = 0
                    if coord == 'y': ind = 1
                    if coord == 'z': ind = 2
                    p3data[key+'_'+coord] = data[key].values[:,ind]
            except TypeError:
                pass
    xdata = xr.Dataset(pdata)
    p2data = xr.Dataset(p2data)
    p3data = xr.Dataset(p3data)
    xdata = xdata.merge(p2data)
    xdata = xdata.merge(p3data)
    data = xdata.rename(dim_0 = 'time')
    return data
   
def generate_header_kp(data):
    """Generate the meta header info for mvn kp data.
    Parameters
    ----------
    inst_id : str
        The VID of the associated dataset.
    epoch : dt.datetime
        The epoch of the datafile.  Corresponds to the first data point.
    Returns
    -------
    header : dict
        A dictionary compatible with the pysat.meta_header format.  Top-level
        metadata for the file.
        
        Global attributes are used to provide information about the data set as an entity. 
        Together with variables and variable attributes, the global attributes make the data correctly and 
        independently usable by someone not connected with the instrument team, and hence, a good archive product. 
        The global attributes are also used by the CDAWeb Display and Retrieval system.
    """
    header = {'Project': data.Project,
              'Source_name': data.Source_name,
              'Discipline':data.Discipline,
              'Data_type': data.Data_type, 
              'Descriptor': data.Descriptor,
              'Data_version': '',
              'Logical_file_id': data.Logical_file_id,
              'PI_name': data.PI_name,
              'PI_affiliation': data.PI_affiliation,
              'TEXT': data.TEXT,
              'Rules_of_use': data.Rules_of_use,
              'Instrument_type': data.Instrument_type,
              'Mission_group': data.Mission_group,
              'Logical_source': data.Logical_source,
              'Logical_source_description': data.Logical_source_description,
              'DOI':'10.17189/1414178',
              'File_naming_convention': data.File_naming_convention,
              'Time_resolution': data.Time_resolution, 
              'Generated_by': data.Generated_by,
              'Generation_date': '',
              'Generation_datetime': dt.datetime.today().isoformat(),
              'Acknowledgement': ackn_str,
              'TITLE': data.TITLE,
              'spase_DatasetResourceID': {'spase://NASA/NumericalData',
                                             '/MAVEN/InSitu/KeyParameter/PT4S'},
              'LINK_TEXT': data.LINK_TEXT,
              'LINK_TITLE': data.LINK_TITLE,
              'HTTP_LINK': data.HTTP_LINK}

    return header


def generate_metadata_kp(header_data,data):
    """Generate metadata object for mvn kp data compatible with SPASE and pysat.
    Parameters
    ----------
    header_data : dict
        A dictionary compatible with the pysat.meta_header format.  Required to
        properly initialize metadata.
    Returns
    -------
    metadata : pandas.Dataframe()
        Contains data compatible with SPASE standards to initialize pysat.Meta.
        
        Variables:
            
    """
    meta = pysat.Meta(header_data=header_data)
    meta['LPW_Electron_density'] = {meta.labels.name: 'LPW_Electron_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Derived from the LP sweep and when available from the plasma line',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron density (LPW) '}
     
    meta['LPW_Electron_density_min'] = {meta.labels.name: 'LPW_Electron_density_min',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron density min (LPW)'}
     
    meta['LPW_Electron_density_max'] = {meta.labels.name: 'LPW_Electron_density_max',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron density max (LPW)'}
     
    meta['LPW_Electron_temperature'] = {meta.labels.name: 'LPW_Electron_temperature',
    meta.labels.units: 'K',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Derived from the LP sweep',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron temperature (LPW)'}
     
    meta['LPW_Electron_temperature_min'] = {meta.labels.name: 'LPW_Electron_temperature_min',
    meta.labels.units: 'K',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron temperature min (LPW)'}
     
    meta['LPW_Electron_temperature_max'] = {meta.labels.name: 'LPW_Electron_temperature_max',
    meta.labels.units: 'K',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron temperature max (LPW)'}
     
    meta['LPW_Spacecraft_potential'] = {meta.labels.name: 'LPW_Spacecraft_potential',
    meta.labels.units: 'V',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Measured from the probe potentials',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Spacecraft potential (LPW)'}
     
    meta['LPW_Spacecraft_potential_min'] = {meta.labels.name: 'LPW_Spacecraft_potential_min',
    meta.labels.units: 'V',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Spacecraft potential min (LPW)'}
     
    meta['LPW_Spacecraft_potential_max'] = {meta.labels.name: 'LPW_Spacecraft_potential_max',
    meta.labels.units: 'V',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Spacecraft potential max (LPW)'}
     
    meta['LPW_E_field_wave_power_2_100'] = {meta.labels.name: 'LPW_E_field_wave_power_2_100',
    meta.labels.units: '(V/m)^2/Hz',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Integrated wave power from the onboard calculated FFT, frequencies important for wave heating',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'E-field wave power 2-100 Hz (LPW)'}
     
    meta['LPW_E_field_wave_power_2_100_data_quality'] = {meta.labels.name: 'LPW_E_field_wave_power_2_100_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Range: 0-100, where 100 is the highest confidence level, use data with quality flag of 50 or above',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> E-field wave power 2-100 Hz data quality (LPW)'}
     
    meta['LPW_E_field_wave_power_100_800'] = {meta.labels.name: 'LPW_E_field_wave_power_100_800',
    meta.labels.units: '(V/m)^2/Hz',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Integrated wave power from the onboard calculated FFT',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'E-field wave power 100-800 Hz (LPW)'}
     
    meta['LPW_E_field_wave_power_100_800_data_quality'] = {meta.labels.name: 'LPW_E_field_wave_power_100_800_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Range: 0-100, where 100 is the highest confidence level, use data with quality flag of 50 or above',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> E-field wave power 100-800 Hz data quality (LPW)'}
     
    meta['LPW_E_field_wave_power_800_1000'] = {meta.labels.name: 'LPW_E_field_wave_power_800_1000',
    meta.labels.units: '(V/m)^2/Hz',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Integrated wave power from the onboard calculated FFT',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'E-field wave power 800-1000 Hz (LPW)'}
     
    meta['LPW_E_field_wave_power_800_1000_data_quality'] = {meta.labels.name: 'LPW_E_field_wave_power_800_1000_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Range: 0-100, where 100 is the highest confidence level, use data with quality flag of 50 or above',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> E-field wave power 800-1000 Hz data quality (LPW)'}
     
    meta['LPW_EUV_irradiance_pt1_7'] = {meta.labels.name: 'LPW_EUV_irradiance_pt1_7',
    meta.labels.units: 'W/m^2',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'EUV irradiance wave power 0.1-7.0 nm bandpass (LPW-EUV)'}
     
    meta['LPW_EUV_irradiance_pt1_7_data_quality'] = {meta.labels.name: 'LPW_EUV_irradiance_pt1_7_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '0 = good solar, 1 = occultation, 2 = no pointing info, 3 = Sun NOT fully in FOV, 4 = Sun NOT in FOV, 5 = windowed, 6 = eclipse, 7 = spare',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> EUV irradiance wave power 0.1-7.0 nm data quality (LPW-EUV)'}
     
    meta['LPW_EUV_irradiance_17_22'] = {meta.labels.name: 'LPW_EUV_irradiance_17_22',
    meta.labels.units: 'W/m^2',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'EUV irradiance wave power 17-22 nm bandpass (LPW-EUV)'}
     
    meta['LPW_EUV_irradiance_17_22_data_quality'] = {meta.labels.name: 'LPW_EUV_irradiance_17_22_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '0 = good solar, 1 = occultation, 2 = no pointing info, 3 = Sun NOT fully in FOV, 4 = Sun NOT in FOV, 5 = windowed, 6 = eclipse, 7 = spare',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> EUV irradiance wave power 17-22 nm data quality (LPW-EUV)'}
     
    meta['LPW_EUV_irradiance_lyman_alpha'] = {meta.labels.name: 'LPW_EUV_irradiance_lyman_alpha',
    meta.labels.units: 'W/m^2',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'EUV irradiance wave power Lyman-alpha bandpass (LPW-EUV)'}
     
    meta['LPW_EUV_irradiance_lyman_alpha_data_quality'] = {meta.labels.name: 'LPW_EUV_irradiance_lyman_alpha_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '0 = good solar, 1 = occultation, 2 = no pointing info, 3 = Sun NOT fully in FOV, 4 = Sun NOT in FOV, 5 = windowed, 6 = eclipse, 7 = spare',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> EUV irradiance wave power Lyman-alpha data quality (LPW-EUV)'}
     
    meta['SWEA_Electron_density'] = {meta.labels.name: 'SWEA_Electron_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Density of solar wind or magnetosheath electrons based on moments of the electron distribution after correcting for the spacecraft potential',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Solar wind electron density (SWEA)'}
     
    meta['SWEA_Electron_density_quality'] = {meta.labels.name: 'SWEA_Electron_density_quality',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Statistical uncertainty,  (1 sigma),  not including systematic error',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Solar wind electron density data quality (SWEA)'}
     
    meta['SWEA_Electron_temperature'] = {meta.labels.name: 'SWEA_Electron_temperature',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Temperature of solar wind or magnetosheath electrons based on moments of the electron distribution after correcting for the spacecraft potential',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Solar wind electron temperature (SWEA)'}
     
    meta['SWEA_Electron_temperature_quality'] = {meta.labels.name: 'SWEA_Electron_temperature_quality',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Statistical uncertainty,  (1 sigma),  not including systematic error',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Solar wind electron temperature data quality (SWEA)'}
     
    meta['SWEA_Electron_parallel_flux_5_100'] = {meta.labels.name: 'SWEA_Electron_parallel_flux_5_100',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Electron energy flux parallel to the magnetic field vector (0-90 degrees pitch angle)',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux parallel 5-100 eV (SWEA)'}
     
    meta['SWEA_Electron_parallel_flux_5_100_data_quality'] = {meta.labels.name: 'SWEA_Electron_parallel_flux_5_100_data_quality',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux parallel 5-100 eV data quality (SWEA)'}
     
    meta['SWEA_Electron_parallel_flux_100_500'] = {meta.labels.name: 'SWEA_Electron_parallel_flux_100_500',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Electron energy flux parallel to the magnetic field vector (0-90 degrees pitch angle)',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux parallel 100-500 eV (SWEA)'}
     
    meta['SWEA_Electron_parallel_flux_100_500_data_quality'] = {meta.labels.name: 'SWEA_Electron_parallel_flux_100_500_data_quality',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux parallel 100-500 eV data quality (SWEA)'}
     
    meta['SWEA_Electron_parallel_flux_500_1000'] = {meta.labels.name: 'SWEA_Electron_parallel_flux_500_1000',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Electron energy flux parallel to the magnetic field vector (0-90 degrees pitch angle)',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux parallel 500-1000 eV (SWEA)'}
     
    meta['SWEA_Electron_parallel_flux_500_1000_data_quality'] = {meta.labels.name: 'SWEA_Electron_parallel_flux_500_1000_data_quality',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux parallel 500-1000 eV data quality (SWEA)'}
     
    meta['SWEA_Electron_anti_parallel_flux_5_100'] = {meta.labels.name: 'SWEA_Electron_anti_parallel_flux_5_100',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Electron energy flux anti-parallel to the magnetic field vector (90-180 degrees pitch angle)',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux anti-parallel 5-100 eV (SWEA)'}
     
    meta['SWEA_Electron_anti_parallel_flux_5_100_data_quality'] = {meta.labels.name: 'SWEA_Electron_anti_parallel_flux_5_100_data_quality',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux anti-parallel 5-100 eV data quality (SWEA)'}
     
    meta['SWEA_Electron_anti_parallel_flux_100_500'] = {meta.labels.name: 'SWEA_Electron_anti_parallel_flux_100_500',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Electron energy flux anti-parallel to the magnetic field vector (90-180 degrees pitch angle)',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux anti-parallel 100-500 eV (SWEA)'}
     
    meta['SWEA_Electron_anti_parallel_flux_100_500_data_quality'] = {meta.labels.name: 'SWEA_Electron_anti_parallel_flux_100_500_data_quality',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux anti-parallel 100-500 eV data quality (SWEA)'}
     
    meta['SWEA_Electron_anti_parallel_flux_500_1000'] = {meta.labels.name: 'SWEA_Electron_anti_parallel_flux_500_1000',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Electron energy flux anti-parallel to the magnetic field vector (90-180 degrees pitch angle)',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux anti-parallel 500-1000 eV (SWEA)'}
     
    meta['SWEA_Electron_anti_parallel_flux_500_1000_data_quality'] = {meta.labels.name: 'SWEA_Electron_anti_parallel_flux_500_1000_data_quality',
    meta.labels.units: 'eV/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux anti-parallel 500-1000 eV data quality (SWEA)'}
     
    meta['SWEA_Electron_spectrum_shape'] = {meta.labels.name: 'SWEA_Electron_spectrum_shape',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Energy spectrum shape parameter used to distingush between ionospheric photoelectrons  and solar wind electrons',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron spectrum shape parameter (SWEA)'}
     
    meta['SWEA_Electron_spectrum_shape_data_quality'] = {meta.labels.name: 'SWEA_Electron_spectrum_shape_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron spectrum shape parameter data quality (SWEA)'}
     
    meta['SWIA_Hplus_density'] = {meta.labels.name: 'SWIA_Hplus_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Total ion density from onboard moment calculation, assuming 100% protons (SWIA)'}
     
    meta['SWIA_Hplus_density_data_quality'] = {meta.labels.name: 'SWIA_Hplus_density_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Quality flag (0 = bad, 1 = good) indicating whether the distribution is well-measured and decommutation parameters are definite',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Total ion density data quality (SWIA)'}
     
    
    
    
    
    
    meta['SWIA_Hplus_flow_velocity_MSO_x'] = {meta.labels.name: 'SWIA_Hplus_flow_velocity_MSO_x',
    meta.labels.units: 'km_s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Bulk ion flow velocity X component from onboard moment calculation, assuming 100% protons (SWIA)'}
    
    meta['SWIA_Hplus_flow_velocity_MSO_y'] = {meta.labels.name: 'SWIA_Hplus_flow_velocity_MSO_y',
    meta.labels.units: 'km_s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Bulk ion flow velocity Y component from onboard moment calculation, assuming 100% protons (SWIA)'}
    
    meta['SWIA_Hplus_flow_velocity_MSO_z'] = {meta.labels.name: 'SWIA_Hplus_flow_velocity_MSO_z',
    meta.labels.units: 'km_s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Bulk ion flow velocity Z component from onboard moment calculation, assuming 100% protons (SWIA)'}
     
    meta['SWIA_Hplus_flow_velocity_MSO_data_quality_x'] = {meta.labels.name: 'SWIA_Hplus_flow_velocity_MSO_data_quality_x',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Quality flag (0 = bad, 1 = good) indicating whether the distribution is well-measured and decommutation parameters are definite',
    meta.labels.desc: '---> Bulk ion flow velocity X data quality (SWIA)'}
    
    meta['SWIA_Hplus_flow_velocity_MSO_data_quality_y'] = {meta.labels.name: 'SWIA_Hplus_flow_velocity_MSO_data_quality_y',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Quality flag (0 = bad, 1 = good) indicating whether the distribution is well-measured and decommutation parameters are definite',
    meta.labels.desc: '---> Bulk ion flow velocity Y data quality (SWIA)'}
    
    meta['SWIA_Hplus_flow_velocity_MSO_data_quality_z'] = {meta.labels.name: 'SWIA_Hplus_flow_velocity_MSO_data_quality_z',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Quality flag (0 = bad, 1 = good) indicating whether the distribution is well-measured and decommutation parameters are definite',
    meta.labels.desc: '---> Bulk ion flow velocity Z data quality (SWIA)'}
     
    meta['SWIA_Hplus_temperature'] = {meta.labels.name: 'SWIA_Hplus_temperature',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Scalar ion temperature from onboard moment calculation, assuming 100% protons (SWIA)'}
     
    meta['SWIA_Hplus_temperature_data_quality'] = {meta.labels.name: 'SWIA_Hplus_temperature_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Quality flag (0 = bad, 1 = good) indicating whether the distribution is well-measured and decommutation parameters are definite',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Scalar ion temperature data quality (SWIA)'}
     
    meta['SWIA_dynamic_pressure'] = {meta.labels.name: 'SWIA_dynamic_pressure',
    meta.labels.units: 'nPa',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion dynamic pressure computed on ground from density and velocity moments, assuming 100% protons (SWIA)'}
     
    meta['SWIA_dynamic_pressure_data_quality'] = {meta.labels.name: 'SWIA_dynamic_pressure_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Quality flag (0 = bad, 1 = good) indicating whether the distribution is well-measured and decommutation parameters are definite',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion dynamic pressure data quality (SWIA)'}
     
    meta['STATIC_Quality'] = {meta.labels.name: 'STATIC_Quality',
    meta.labels.units: ' ',
    meta.labels.min_val: 0.0,
    meta.labels.max_val: 999999999.0,
    meta.labels.notes: 'Integer flag bits, Valid=0, Flag=1, See KP SIS for bit descriptions (formatted as a float in order to include NaN values for data gaps) ',
    meta.labels.fill_val: -2147483648.0,
    meta.labels.desc: 'STATIC Data quality'}
     
    meta['STATIC_Hplus_density'] = {meta.labels.name: 'STATIC_Hplus_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'H+ number density below TBD altitude determined from APID c6 (32 energy x 64 mass) while in Ram or Conic modes',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ density (STATIC)'}
     
    meta['STATIC_Hplus_density_data_quality'] = {meta.labels.name: 'STATIC_Hplus_density_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> H+ density data quality (STATIC)'}
     
    meta['STATIC_Oplus_density'] = {meta.labels.name: 'STATIC_Oplus_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O+ number density below TBD altitude determined from APID c6 (32 energy x 64 mass) while in Ram or Conic modes',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O+ density (STATIC)'}
     
    meta['STATIC_Oplus_density_data_quality'] = {meta.labels.name: 'STATIC_Oplus_density_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O+ density data quality (STATIC)'}
     
    meta['STATIC_O2plus_density'] = {meta.labels.name: 'STATIC_O2plus_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O2+ number density below TBD altitude determined from APID c6 (32 energy x 64 mass) while in Ram or Conic modes',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ density (STATIC)'}
     
    meta['STATIC_O2plus_density_data_quality'] = {meta.labels.name: 'STATIC_O2plus_density_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ density data quality (STATIC)'}
     
    meta['STATIC_Hplus_temperature'] = {meta.labels.name: 'STATIC_Hplus_temperature',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'H+ RAM temperature below TBD altitude determined from APID c6 (32 energy x 64 mass) while in Ram or Conic modes',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ temperature (STATIC)'}
     
    meta['STATIC_Hplus_temperature_data_quality'] = {meta.labels.name: 'STATIC_Hplus_temperature_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> H+ temperature data quality (STATIC)'}
     
    meta['STATIC_Oplus_temperature'] = {meta.labels.name: 'STATIC_Oplus_temperature',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O+ RAM temperature below TBD altitude determined from APID c6 (32 energy x 64 mass) while in Ram or Conic modes',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O+ temperature (STATIC)'}
     
    meta['STATIC_Oplus_temperature_data_quality'] = {meta.labels.name: 'STATIC_Oplus_temperature_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O+ temperature data quality (STATIC)'}
     
    meta['STATIC_O2plus_temperature'] = {meta.labels.name: 'STATIC_O2plus_temperature',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O2+ RAM temperature below TBD altitude determined from APID c6 (32 energy x 64 mass) while in Ram or Conic modes',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ temperature (STATIC)'}
     
    meta['STATIC_O2plus_temperature_data_quality'] = {meta.labels.name: 'STATIC_O2plus_temperature_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ temperature data quality (STATIC)'}
    
    
    
    meta['STATIC_O2plus_flow_velocity_MAVEN_APP_x'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MAVEN_APP_x',
    meta.labels.units: 'km/s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ MAVEN_APP X component of velocity below TBD altitude determined from APID c6 while in Ram or Conic mode (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MAVEN_APP_y'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MAVEN_APP_y',
    meta.labels.units: 'km/s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ MAVEN_APP Y component of velocity below TBD altitude determined from APID c6 while in Ram or Conic mode (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MAVEN_APP_z'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MAVEN_APP_z',
    meta.labels.units: 'km/s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ MAVEN_APP Z component of velocity below TBD altitude determined from APID c6 while in Ram or Conic mode (STATIC)'}

    meta['STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality_x'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality_x',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.desc: '---> O2+ MAVEN_APP X component of velocity data quality (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality_y'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality_y',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ MAVEN_APP Y component of velocity data quality (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality_z'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MAVEN_APP_data_quality_z',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.desc: '---> O2+ MAVEN_APP Z component of velocity data quality (STATIC)'}
     
    meta['STATIC_O2plus_flow_velocity_MSO_x'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MSO_x',
    meta.labels.units: 'km/s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ MSO X component of velocity below TBD altitude while in Ram or Conic mode (STATIC)'}
     
    meta['STATIC_O2plus_flow_velocity_MSO_y'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MSO_y',
    meta.labels.units: 'km/s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ MSO Y component of velocity below TBD altitude while in Ram or Conic mode (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MSO_z'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MSO_z',
    meta.labels.units: 'km/s',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ MSO Y component of velocity below TBD altitude while in Ram or Conic mode (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MSO_data_quality_x'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MSO_data_quality_x',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ MSO X component of velocity data quality (STATIC)'}
     
    meta['STATIC_O2plus_flow_velocity_MSO_data_quality_y'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MSO_data_quality_y',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ MSO Y component of velocity data quality (STATIC)'}
    
    meta['STATIC_O2plus_flow_velocity_MSO_data_quality_z'] = {meta.labels.name: 'STATIC_O2plus_flow_velocity_MSO_data_quality_z',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ MSO Z component of velocity data quality (STATIC)'}
    
   
   
    meta['STATIC_Hplus_omni_directional_flux'] = {meta.labels.name: 'STATIC_Hplus_omni_directional_flux',
    meta.labels.units: '(cm^2 s)^-1',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'H+ omni-directional flux above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ omni-directional flux (STATIC)'}
     
    meta['STATIC_Hplus_characteristic_energy'] = {meta.labels.name: 'STATIC_Hplus_characteristic_energy',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'H+ omni-directional characteristic energy above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ characteristic energy (STATIC)'}
     
    meta['STATIC_Hplus_characteristic_energy_DQ'] = {meta.labels.name: 'STATIC_Hplus_characteristic_energy_DQ',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> H+ characteristic energy data quality (STATIC)'}
     
    meta['STATIC_HEplus_omni_directional_flux'] = {meta.labels.name: 'STATIC_HEplus_omni_directional_flux',
    meta.labels.units: '(cm^2 s)^-1',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'HE+ omni-directional flux above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'He+ omni-directional flux (STATIC)'}
     
    meta['STATIC_HEplus_characteristic_energy'] = {meta.labels.name: 'STATIC_HEplus_characteristic_energy',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'HE+ omni-directional characteristic energy above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'He+ characteristic energy (STATIC)'}
     
    meta['STATIC_HEplus_characteristic_energy_DQ'] = {meta.labels.name: 'STATIC_HEplus_characteristic_energy_DQ',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> He+ characteristic energy data quality (STATIC)'}
     
    meta['STATIC_Oplus_omni_directional_flux'] = {meta.labels.name: 'STATIC_Oplus_omni_directional_flux',
    meta.labels.units: '(cm^2 s)^-1',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O+ omni-directional flux above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O+ omni-directional flux (STATIC)'}
     
    meta['STATIC_Oplus_characteristic_energy'] = {meta.labels.name: 'STATIC_Oplus_characteristic_energy',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O+ omni-directional characteristic energy above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O+ characteristic energy (STATIC)'}
     
    meta['STATIC_Oplus_characteristic_energy_DQ'] = {meta.labels.name: 'STATIC_Oplus_characteristic_energy_DQ',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O+ characteristic energy data quality (STATIC)'}
     
    meta['STATIC_O2plus_omni_directional_flux'] = {meta.labels.name: 'STATIC_O2plus_omni_directional_flux',
    meta.labels.units: '(cm^2 s)^-1',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O2+ omni-directional flux above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ omni-directional flux (STATIC)'}
     
    meta['STATIC_O2plus_characteristic_energy'] = {meta.labels.name: 'STATIC_O2plus_characteristic_energy',
    meta.labels.units: 'eV',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'O2+ omni-directional characteristic energy above TBD altitude determined from APID c6 while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O2+ characteristic energy (STATIC)'}
     
    meta['STATIC_O2plus_characteristic_energy_DQ'] = {meta.labels.name: 'STATIC_O2plus_characteristic_energy_DQ',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O2+ characteristic energy data quality (STATIC)'}
     
    
    meta['STATIC_Hplus_characteristic_direction_MSO_x'] = {meta.labels.name: 'STATIC_Hplus_characteristic_direction_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ MSO X-direction of flux above TBD altitude determined from TBD APID while in Pickup and Scan mode (STATIC)'}
    
    meta['STATIC_Hplus_characteristic_direction_MSO_y'] = {meta.labels.name: 'STATIC_Hplus_characteristic_direction_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ MSO Y-direction of flux above TBD altitude determined from TBD APID while in Pickup and Scan mode (STATIC)'}
    
    meta['STATIC_Hplus_characteristic_direction_MSO_z'] = {meta.labels.name: 'STATIC_Hplus_characteristic_direction_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ MSO Z-direction of flux above TBD altitude determined from TBD APID while in Pickup and Scan mode (STATIC)'}
     
    
    
    
    
    
    
    meta['STATIC_Hplus_characteristic_angular_width'] = {meta.labels.name: 'STATIC_Hplus_characteristic_angular_width',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'H+ flux angular width above TBD altitude determined from TBD APID while in Pickup and Scan mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'H+ characteristic width (STATIC)'}
     
    meta['STATIC_Hplus_characteristic_angular_width_DQ'] = {meta.labels.name: 'STATIC_Hplus_characteristic_angular_width_DQ',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> H+ characteristic width data quality (STATIC)'}
     
    
    meta['STATIC_dominant_pickup_ion_characteristic_direction_MSO_z'] = {meta.labels.name: 'STATIC_dominant_pickup_ion_characteristic_direction_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Dominant pickup ion MSO Z direction of flux above TBD altitude determined from APID D0 and CE while in Pickup, Eclipse and Protect mode'}
     
    meta['STATIC_dominant_pickup_ion_characteristic_direction_MSO_x'] = {meta.labels.name: 'STATIC_dominant_pickup_ion_characteristic_direction_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Dominant pickup ion MSO X direction of flux above TBD altitude determined from APID D0 and CE while in Pickup, Eclipse and Protect mode'}
    
    meta['STATIC_dominant_pickup_ion_characteristic_direction_MSO_y'] = {meta.labels.name: 'STATIC_dominant_pickup_ion_characteristic_direction_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Dominant pickup ion MSO Y direction of flux above TBD altitude determined from APID D0 and CE while in Pickup, Eclipse and Protect mode'}
     
    
    

    
    meta['STATIC_dominant_pickup_ion_characteristic_angular_width'] = {meta.labels.name: 'STATIC_dominant_pickup_ion_characteristic_angular_width',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Dominant pickup ion flux angular width above TBD altitude determined from APID D0 and CE while in Pickup, Eclipse and Protect mode',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Dominant pickup ion characteristic angular width (STATIC)'}
     
    meta['STATIC_dominant_pickup_ion_characteristic_angular_width_DQ'] = {meta.labels.name: 'STATIC_dominant_pickup_ion_characteristic_angular_width_DQ',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number of counts in the measurement',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Dominant pickup ion characteristic angular width DQ (STATIC)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_1F'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_1F',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of ions, integrated over the energy range 0.03-1.0 MeV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion energy flux (30-1000 keV), FOV 1-F (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_1F_data_quality'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_1F_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total ion flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion energy flux (30-1000 keV), FOV 1-F data quality (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_1R'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_1R',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of ions, integrated over the energy range 0.03-1.0 MeV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion energy flux (30-1000 keV), FOV 1-R (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_1R_data_quality'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_1R_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total ion flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion energy flux (30-1000 keV), FOV 1-R data quality (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_2F'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_2F',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of ions, integrated over the energy range 0.03-1.0 MeV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion energy flux (30-1000 keV), FOV 2-F (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_2F_data_quality'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_2F_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total ion flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion energy flux (30-1000 keV), FOV 2-F data quality (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_2R'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_2R',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of ions, integrated over the energy range 0.03-1.0 MeV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion energy flux (30-1000 keV), FOV 2-R (SEP)'}
     
    meta['SEP_Ion_Energy_Flux_30_1000_FOV_2R_data_quality'] = {meta.labels.name: 'SEP_Ion_Energy_Flux_30_1000_FOV_2R_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total ion flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion energy flux (30-1000 keV), FOV 2-R data quality (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_1F'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_1F',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of electrons, integrated over the energy range 30-300 keV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux (30-300 keV), FOV 1-F (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_1F_data_quality'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_1F_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total electron flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux (30-300 keV), FOV 1-F data quality (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_1R'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_1R',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of electrons, integrated over the energy range 30-300 keV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux (30-300 keV), FOV 1-R (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_1R_data_quality'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_1R_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total electron flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux (30-300 keV), FOV 1-R data quality (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_2F'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_2F',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of electrons, integrated over the energy range 30-300 keV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux (30-300 keV), FOV 2-F (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_2F_data_quality'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_2F_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total electron flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux (30-300 keV), FOV 2-F data quality (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_2R'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_2R',
    meta.labels.units: 'n/(cm^2 s sr)',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Number flux of electrons, integrated over the energy range 30-300 keV',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Electron energy flux (30-300 keV), FOV 2-R (SEP)'}
     
    meta['SEP_Electron_Energy_Flux_30_300_FOV_2R_data_quality'] = {meta.labels.name: 'SEP_Electron_Energy_Flux_30_300_FOV_2R_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Standard uncertainty in total electron flux, based on Poisson statistics',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Electron energy flux (30-300 keV), FOV 2-R data quality (SEP)'}
     
    
    
    
    
    
    
    
    
    meta['SEP_Look_direction_1F_MSO_x'] = {meta.labels.name: 'SEP_Look_direction_1F_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'SEP look direction 1-F MSO X'}
    
    meta['SEP_Look_direction_1F_MSO_y'] = {meta.labels.name: 'SEP_Look_direction_1F_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'SEP look direction 1-F MSO Y'}
    
    meta['SEP_Look_direction_1F_MSO_z'] = {meta.labels.name: 'SEP_Look_direction_1F_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 1-F MSO Z'}
     
    meta['SEP_Look_direction_1R_MSO_x'] = {meta.labels.name: 'SEP_Look_direction_1R_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 1-R MSO X'}
    
    meta['SEP_Look_direction_1R_MSO_y'] = {meta.labels.name: 'SEP_Look_direction_1R_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 1-R MSO Y'}
    
    meta['SEP_Look_direction_1R_MSO_z'] = {meta.labels.name: 'SEP_Look_direction_1R_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 1-R MSO Z'}
     
    meta['SEP_Look_direction_2F_MSO_x'] = {meta.labels.name: 'SEP_Look_direction_2F_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 2-F MSO X'}
    
    meta['SEP_Look_direction_2F_MSO_y'] = {meta.labels.name: 'SEP_Look_direction_2F_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 2-F MSO Y'}
    
    meta['SEP_Look_direction_2F_MSO_z'] = {meta.labels.name: 'SEP_Look_direction_2F_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 2-F MSO Z'}
     
    meta['SEP_Look_direction_2R_MSO_x'] = {meta.labels.name: 'SEP_Look_direction_2R_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 2-R MSO X'}
    
    meta['SEP_Look_direction_2R_MSO_y'] = {meta.labels.name: 'SEP_Look_direction_2R_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 2-R MSO Y'}
    
    meta['SEP_Look_direction_2R_MSO_z'] = {meta.labels.name: 'SEP_Look_direction_2R_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'SEP look direction 2-R MSO Z'}
     
    meta['MAG_field_MSO_x'] = {meta.labels.name: 'MAG_field_MSO_x',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Magnetic field vector component in the X direction in MSO coordinates (MAG)'}
     
    meta['MAG_field_MSO_y'] = {meta.labels.name: 'MAG_field_MSO_y',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Magnetic field vector component in the Y direction in MSO coordinates (MAG)'}
    
    meta['MAG_field_MSO_z'] = {meta.labels.name: 'MAG_field_MSO_z',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Magnetic field vector component in the Z direction in MSO coordinates (MAG)'}
    
    
    meta['MAG_field_MSO_data_quality_x'] = {meta.labels.name: 'MAG_field_MSO_data_quality_x',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Unused column',
    meta.labels.desc: '---> Magnetic field X vector component in MSO coordinates data quality (MAG)'}
    
    meta['MAG_field_MSO_data_quality_y'] = {meta.labels.name: 'MAG_field_MSO_data_quality_y',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Unused column',
    meta.labels.desc: '---> Magnetic field Y vector component in MSO coordinates data quality (MAG)'}
    
    meta['MAG_field_MSO_data_quality_z'] = {meta.labels.name: 'MAG_field_MSO_data_quality_z',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Unused column',
    meta.labels.desc: '---> Magnetic field Z vector component in MSO coordinates data quality (MAG)'}
     
    meta['MAG_field_GEO_x'] = {meta.labels.name: 'MAG_field_GEO_x',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Magnetic field vector component in the X direction in GEO coordinates (MAG)'}
    
    meta['MAG_field_GEO_y'] = {meta.labels.name: 'MAG_field_GEO_y',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.desc: 'Magnetic field vector component in the Y direction in GEO coordinates (MAG)'}
    
    meta['MAG_field_GEO_z'] = {meta.labels.name: 'MAG_field_GEO_z',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Magnetic field vector component in the Z direction in GEO coordinates (MAG)'}
     
    meta['MAG_field_GEO_data_quality_x'] = {meta.labels.name: 'MAG_field_GEO_data_quality_x',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Unused column',
    meta.labels.desc: '---> Magnetic field X vector component in GEO coordinates data quality (MAG)'}
    
    meta['MAG_field_GEO_data_quality_y'] = {meta.labels.name: 'MAG_field_GEO_data_quality_y',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Unused column',
    meta.labels.desc: '---> Magnetic field Y vector component in GEO coordinates data quality (MAG)'}
    
    meta['MAG_field_GEO_data_quality_z'] = {meta.labels.name: 'MAG_field_GEO_data_quality_z',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Unused column',
    meta.labels.desc: '---> Magnetic field Z vector component in GEO coordinates data quality (MAG)'}
     
    

    meta['MAG_field_RMS_deviation'] = {meta.labels.name: 'MAG_field_RMS_deviation',
    meta.labels.units: 'nT',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Deviations from the mean magnetic field magnitude (MAG)'}
     
    meta['MAG_field_RMS_deviation_data_quality'] = {meta.labels.name: 'MAG_field_RMS_deviation_data_quality',
    meta.labels.units: ' ',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Unused column',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Deviations from the mean magnetic field magnitude data quality (MAG)'}
     
    meta['NGIMS_He_density'] = {meta.labels.name: 'NGIMS_He_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'He density (NGIMS)'}
     
    meta['NGIMS_He_density_precision'] = {meta.labels.name: 'NGIMS_He_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> He density precision (NGIMS)'}
     
    meta['NGIMS_He_density_data_quality'] = {meta.labels.name: 'NGIMS_He_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] He density data quality (NGIMS)'}
     
    meta['NGIMS_O_density'] = {meta.labels.name: 'NGIMS_O_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'O density (NGIMS)'}
     
    meta['NGIMS_O_density_precision'] = {meta.labels.name: 'NGIMS_O_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> O density precision (NGIMS)'}
     
    meta['NGIMS_O_density_data_quality'] = {meta.labels.name: 'NGIMS_O_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] O density data quality (NGIMS)'}
     
    meta['NGIMS_CO_density'] = {meta.labels.name: 'NGIMS_CO_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'CO density (NGIMS)'}
     
    meta['NGIMS_CO_density_precision'] = {meta.labels.name: 'NGIMS_CO_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> CO density precision (NGIMS)'}
     
    meta['NGIMS_CO_density_data_quality'] = {meta.labels.name: 'NGIMS_CO_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] CO density data quality (NGIMS)'}
     
    meta['NGIMS_N2_density'] = {meta.labels.name: 'NGIMS_N2_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'N2 density (NGIMS)'}
     
    meta['NGIMS_N2_density_precision'] = {meta.labels.name: 'NGIMS_N2_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> N2 density precision (NGIMS)'}
     
    meta['NGIMS_N2_density_data_quality'] = {meta.labels.name: 'NGIMS_N2_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] N2 density data quality (NGIMS)'}
     
    meta['NGIMS_NO_density'] = {meta.labels.name: 'NGIMS_NO_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'NO density (NGIMS)'}
     
    meta['NGIMS_NO_density_precision'] = {meta.labels.name: 'NGIMS_NO_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> NO density precision (NGIMS)'}
     
    meta['NGIMS_NO_density_data_quality'] = {meta.labels.name: 'NGIMS_NO_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] NO density data quality (NGIMS)'}
     
    meta['NGIMS_Ar_density'] = {meta.labels.name: 'NGIMS_Ar_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ar density (NGIMS)'}
     
    meta['NGIMS_Ar_density_precision'] = {meta.labels.name: 'NGIMS_Ar_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ar density precision (NGIMS)'}
     
    meta['NGIMS_Ar_density_data_quality'] = {meta.labels.name: 'NGIMS_Ar_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] Ar density data quality (NGIMS)'}
     
    meta['NGIMS_CO2_density'] = {meta.labels.name: 'NGIMS_CO2_density',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'CO2 density (NGIMS)'}
     
    meta['NGIMS_CO2_density_precision'] = {meta.labels.name: 'NGIMS_CO2_density_precision',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> CO2 density precision (NGIMS)'}
     
    meta['NGIMS_CO2_density_data_quality'] = {meta.labels.name: 'NGIMS_CO2_density_data_quality',
    meta.labels.units: '-',
    meta.labels.notes: 'NIV - Neutral Inbound Verified, NIU - Neutral Inbound Unverified, NOV - Neutral Outbound Verified, NOU - Neutral Outbound Unverified',
    meta.labels.desc: '---> [DOES NOT PLOT] CO2 density data quality (NGIMS)'}
     
    meta['NGIMS_Ion_density_32plus'] = {meta.labels.name: 'NGIMS_Ion_density_32plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 32+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_32plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_32plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 32+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_32plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_32plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 32+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_44plus'] = {meta.labels.name: 'NGIMS_Ion_density_44plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 44+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_44plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_44plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 44+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_44plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_44plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 44+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_30plus'] = {meta.labels.name: 'NGIMS_Ion_density_30plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 30+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_30plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_30plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 30+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_30plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_30plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 30+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_16plus'] = {meta.labels.name: 'NGIMS_Ion_density_16plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 16+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_16plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_16plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 16+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_16plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_16plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 16+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_28plus'] = {meta.labels.name: 'NGIMS_Ion_density_28plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 28+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_28plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_28plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 28+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_28plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_28plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 28+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_12plus'] = {meta.labels.name: 'NGIMS_Ion_density_12plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 12+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_12plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_12plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 12+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_12plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_12plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 12+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_17plus'] = {meta.labels.name: 'NGIMS_Ion_density_17plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 17+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_17plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_17plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 17+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_17plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_17plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 17+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_14plus'] = {meta.labels.name: 'NGIMS_Ion_density_14plus',
    meta.labels.units: 'cm^-3',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Abundance or upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Ion density - amu 14+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_precision_14plus'] = {meta.labels.name: 'NGIMS_Ion_density_precision_14plus',
    meta.labels.units: '%',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: '% Error (1 sigma), if -1, the value is an upper limit',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: '---> Ion density precision - amu 14+ (NGIMS)'}
     
    meta['NGIMS_Ion_density_data_quality_14plus'] = {meta.labels.name: 'NGIMS_Ion_density_data_quality_14plus',
    meta.labels.units: '-',
    meta.labels.notes: 'SCP - SpaceCraft Potential available and used as computed by STATIC, SC0 - SpaceCraft potential not available',
    meta.labels.desc: '---> [DOES NOT PLOT] Ion density data quality - amu 14+ (NGIMS)'}
     
    
    
    
    
    
    meta['SPICE_spacecraft_GEO_x'] = {meta.labels.name: 'SPICE_spacecraft_GEO_x',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'X-component of spacecraft position in Mars planetocentric (geographic) GEO coordinates'}
    
    meta['SPICE_spacecraft_GEO_y'] = {meta.labels.name: 'SPICE_spacecraft_GEO_y',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Y-component of spacecraft position in Mars planetocentric (geographic) GEO coordinates'}
    
    meta['SPICE_spacecraft_GEO_z'] = {meta.labels.name: 'SPICE_spacecraft_GEO_z',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Z-component of spacecraft position in Mars planetocentric (geographic) GEO coordinates'}
     
    meta['SPICE_spacecraft_MSO_x'] = {meta.labels.name: 'SPICE_spacecraft_MSO_x',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'X-component of spacecraft position in MSO coordinates'}
    
    meta['SPICE_spacecraft_MSO_y'] = {meta.labels.name: 'SPICE_spacecraft_MSO_y',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Y-component of spacecraft position in MSO coordinates'}
    
    meta['SPICE_spacecraft_MSO_z'] = {meta.labels.name: 'SPICE_spacecraft_MSO_z',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Z-component of spacecraft position in MSO coordinates'}
    
    
    
    meta['SPICE_spacecraft_longitude_GEO'] = {meta.labels.name: 'SPICE_spacecraft_longitude_GEO',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Longitudinal component of MAVEN\'s location with respect to Mars',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Spacecraft longitude GEO (SPICE)'}
     
    meta['SPICE_spacecraft_latitude_GEO'] = {meta.labels.name: 'SPICE_spacecraft_latitude_GEO',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Latitudinal (areodetic) component of MAVEN\'s location with respect to IAU Mars ellipsoid, equatorial radius of 3396.2 km, polar radius of',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Spacecraft latitude GEO (SPICE)'}
     
    meta['SPICE_spacecraft_sza'] = {meta.labels.name: 'SPICE_spacecraft_sza',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Angle measured from MAVEN to the geometric center of the Sun\'s disc, as described using a horizontal coordinate system',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Spacecraft solar zenith angle (SPICE)'}
     
    meta['SPICE_spacecraft_local_time'] = {meta.labels.name: 'SPICE_spacecraft_local_time',
    meta.labels.units: 'hours',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Angle measured from MAVEN to the geometric center of the Sun\'s disc, as described using a horizontal coordinate system',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Spacecraft local time (SPICE)'}
     
    meta['SPICE_spacecraft_altitude'] = {meta.labels.name: 'SPICE_spacecraft_altitude',
    meta.labels.units: 'km',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Altitude (areodetic) with respect to IAU Mars ellipsoid, equatorial radius of 3396.2 km, ',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Spacecraft altitude w.r.t. aeroid (SPICE)'}
     
    
    meta['SPICE_spacecraft_attitude_GEO_x'] = {meta.labels.name: 'SPICE_spacecraft_attitude_GEO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'X-component of spacecraft attitude in GEO coordinates'}
    
    meta['SPICE_spacecraft_attitude_GEO_y'] = {meta.labels.name: 'SPICE_spacecraft_attitude_GEO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Y-component of spacecraft attitude in GEO coordinates'}
    
    meta['SPICE_spacecraft_attitude_GEO_z'] = {meta.labels.name: 'SPICE_spacecraft_attitude_GEO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Z-component of spacecraft attitude in GEO coordinates'}
     
    meta['SPICE_spacecraft_attitude_MSO_x'] = {meta.labels.name: 'SPICE_spacecraft_attitude_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'X-component of spacecraft attitude in MSO coordinates'}
    
    meta['SPICE_spacecraft_attitude_MSO_y'] = {meta.labels.name: 'SPICE_spacecraft_attitude_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Y-component of spacecraft attitude in MSO coordinates'}
    
    meta['SPICE_spacecraft_attitude_MSO_z'] = {meta.labels.name: 'SPICE_spacecraft_attitude_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Z-component of spacecraft attitude in MSO coordinates'}
     

    meta['SPICE_app_attitude_GEO_x'] = {meta.labels.name: 'SPICE_app_attitude_GEO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'X-component of pointing direction of Articulated Payload Platform (z-axis of MAVEN_APP_BP frame) in GEO coordinates',
    meta.labels.desc: 'X-component of articulated payload platform (app) attitude in GEO coordinates'}
    
    meta['SPICE_app_attitude_GEO_y'] = {meta.labels.name: 'SPICE_app_attitude_GEO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Y-component of pointing direction of Articulated Payload Platform (z-axis of MAVEN_APP_BP frame) in GEO coordinates',
    meta.labels.desc: 'Y-component of articulated payload platform (app) attitude in GEO coordinates'}
    
    meta['SPICE_app_attitude_GEO_z'] = {meta.labels.name: 'SPICE_app_attitude_GEO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.notes: 'Z-component of pointing direction of Articulated Payload Platform (z-axis of MAVEN_APP_BP frame) in GEO coordinates',
    meta.labels.desc: 'Z-component of articulated payload platform (app) attitude in GEO coordinates'}
    
    
    meta['SPICE_app_attitude_MSO_x'] = {meta.labels.name: 'SPICE_app_attitude_MSO_x',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'X-component of articulated payload platform (app) attitude in MSO coordinates'}
    
    meta['SPICE_app_attitude_MSO_y'] = {meta.labels.name: 'SPICE_app_attitude_MSO_y',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Y-component of articulated payload platform (app) attitude in MSO coordinates'}
     
    meta['SPICE_app_attitude_MSO_z'] = {meta.labels.name: 'SPICE_app_attitude_MSO_z',
    meta.labels.units: 'unit vector',
    meta.labels.min_val: -999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'same as IAU_MARS in SPICE',
    meta.labels.desc: 'Z-component of articulated payload platform (app) attitude in MSO coordinates'}
    
    meta['SPICE_Orbit_Number'] = {meta.labels.name: 'SPICE_Orbit_Number',
    meta.labels.units: ' ',
    meta.labels.min_val: 1.0,
    meta.labels.max_val: 10000000.0,
    meta.labels.notes: 'Orbit number increments each time MAVEN reaches geometric periapsis',
    meta.labels.fill_val: -2147483648.0,
    meta.labels.desc: 'Orbit number (SPICE)'}
     
    meta['Inbound_Outbound_Flag'] = {meta.labels.name: 'Inbound_Outbound_Flag',
    meta.labels.units: ' ',
    meta.labels.notes: 'Inbound (\'I\') is from geometric apoapsis to next geometric periapsis in time, outbound (\'O\') is the reverse',
    meta.labels.desc: '---> [DOES NOT PLOT] Inbound/Outbound Flag (SPICE)'}
     
    meta['SPICE_Mars_season'] = {meta.labels.name: 'SPICE_Mars_season',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Martian solar longitude. Ls = 0 (northern spring equinox), Ls = 90 (northern summer solstice), etc.',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Mars Season (Ls) (SPICE)'}
     
    meta['SPICE_Mars_Sun_distance'] = {meta.labels.name: 'SPICE_Mars_Sun_distance',
    meta.labels.units: 'AU',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Mars-Sun distance (SPICE)'}
     
    meta['SPICE_Subsolar_Point_longitude_GEO'] = {meta.labels.name: 'SPICE_Subsolar_Point_longitude_GEO',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'GEO longitude of the sub-solar point',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Subsolar Point longitude GEO (SPICE)'}
     
    meta['SPICE_Subsolar_Point_latitude_GEO'] = {meta.labels.name: 'SPICE_Subsolar_Point_latitude_GEO',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'GEO latitude of the sub-solar point',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Subsolar Point latitude GEO (SPICE)'}
     
    meta['SPICE_Sub_Mars_Point_longitude'] = {meta.labels.name: 'SPICE_Sub_Mars_Point_longitude',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Solar longitude of the center of the Sun as seen from Mars',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Sub-Mars Point on the Sun, Longitude (SPICE)'}
     
    meta['SPICE_Sub_Mars_Point_latitude'] = {meta.labels.name: 'SPICE_Sub_Mars_Point_latitude',
    meta.labels.units: 'deg',
    meta.labels.min_val: -999999995904.0,
    meta.labels.max_val: 999999995904.0,
    meta.labels.notes: 'Solar latitude of the center of the Sun as seen from Mars',
    meta.labels.fill_val: -9.999999848243207e+30,
    meta.labels.desc: 'Sub-Mars Point on the Sun, Latitude (SPICE)'}
     
    meta['Rotation_matrix_IAU_MARS_MAVEN_MSO'] = {meta.labels.name: 'Rotation_matrix_IAU_MARS_MAVEN_MSO',
    meta.labels.units: ' ',
    meta.labels.min_val: -1000000000000.0,
    meta.labels.max_val: 1000000000000.0,
    meta.labels.notes: 'From IAU_MARS frame to MAVEN_MSO frame',
    meta.labels.fill_val: -1e+31,
    meta.labels.desc: 'Rotation matrix (IAU_MARS -> MAVEN_MSO) (SPICE)'}
     
    meta['Rotation_matrix_SPACECRAFT_MAVEN_MSO'] = {meta.labels.name: 'Rotation_matrix_SPACECRAFT_MAVEN_MSO',
    meta.labels.units: ' ',
    meta.labels.min_val: -1000000000000.0,
    meta.labels.max_val: 1000000000000.0,
    meta.labels.notes: 'From MAVEN_SPACECRAFT frame to MAVEN_MSO frame',
    meta.labels.fill_val: -1e+31,
    meta.labels.desc: '---> Rotation matrix (MAVEN_SPACECRAFT -> MAVEN_MSO) (SPICE)'}
     
       
    return meta
