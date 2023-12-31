
# *synconn_build* : Synthetic dataset generator for testing control-oriented neural networks for building dynamics

Applying model-based predictive control in buildings requires a control-oriented model capable of learning how various control actions influence building dynamics, such as indoor air temperature and energy use. However, there is currently a shortage of empirical or synthetic datasets with the appropriate features, variability, quality and volume to properly benchmark these control-oriented models. Addressing this need, a flexible, open-source, Python-based tool, *synconn_build*, capable of generating synthetic building operation data using EnergyPlus as the main building energy simulation engine is introduced. The uniqueness of *synconn_build* lies in its capability to automate multiple aspects of the simulation process, guided by user inputs drawn from a text-based configuration file. It generates various kinds of unique random signals for control inputs, performs co-simulation to create unique occupancy schedules, and acquires weather data. Additionally, it simplifies the typically tedious and complex task of configuring EnergyPlus files with all user inputs. Unlike other synthetic datasets for building operations, *synconn_build* offers a user-friendly generator that selectively creates data based on user inputs, preventing overwhelming data overproduction. Instead of emulating the operational schedules of real buildings, *synconn_build* generates test signals with more frequent variation to cover a broader range of operating conditions.

Link to the paper with more details: <br>
[https://doi.org/10.1016/j.mex.2023.102464](https://doi.org/10.1016/j.mex.2023.102464)<br>
[synconn_build MethodsX.pdf](https://github.com/gaurav306/synconn_build/blob/main/Paper/synconn_build%20MethodsX.pdf)

![workflow](./Paper/highlevel_workflow.png "workflow")

# Instructions
## Step 1: EnergyPlus initialization

*Synconn_build* uses EnergyPlusv22.1.0 as the main simualtion engine. It can be downloaded from (https://github.com/NREL/EnergyPlus/releases/tag/v22.1.0).

After installation the user is required to fill in correct information in [Config_input.yaml](https://github.com/gaurav306/synconn_build/blob/main/Config_input.yaml#L1) file.
```yaml
energyplus_init:
  ep_dir: E:\EnergyPlusV22-1-0\
  idd_dir: E:\EnergyPlusV22-1-0\Energy+.idd
  timestep: 4
```
* **ep_dir**: Specify the path to your EnergyPlus directory.
* **idd_dir**: Specify the path to your EnergyPlus IDD file.
* **timestep**: Define the time-step size for the simulation. The unit is hours, with options ranging from 1 (for 1 hour) to 6 (for 10 minutes).

## Step 2: Weather files configuration

The user can run this tool both with or wthout internet connection. If there is internet connection the user can procure weather files from [climate.onebuilding.org](https://climate.onebuilding.org)

Settings for weather files configuration in [Config_input.yaml](https://github.com/gaurav306/synconn_build/blob/main/Config_input.yaml#L8) are as follows:

```yaml
weather_files: 
  get_epw: online
  epw_urls:
  - https://climate.onebuilding.org/WMO_Region_6_Europe/NOR_Norway/AK_Akershus/NOR_AK_Oslo.AP-Gardermoen.013840_TMYx.zip
  - https://climate.onebuilding.org/WMO_Region_6_Europe/NOR_Norway/TR_Troms/NOR_TR_Trondheim.AP-Vaernes.012710_TMYx.zip
  offline_weather_dir: 'Offline_weather_files_input'
  epw_ddy_names:         
  - Trondheim
  - Rome
```
* **get_epw**: Specify whether the weather files should be retrieved online or offline. Your options are 'online' or 'offline'.
* **epw_urls**: If `get_epw` is set to `online`, list the URLs of your preferred EPW files here. The program will download these files and create corresponding directories based on the URLs. To access a wide variety of weather files, you can visit [climate.onebuilding.org](https://climate.onebuilding.org).
* **offline_weather_dir**: If get_epw is `offline`, specify the directory that holds your offline weather files.
* **epw_ddy_names**: If get_epw is `offline`, provide the names of the EPW and corresponding DDY files here. The program will search for these files in the `offline_weather_dir` and run simulations based on them. Remember that the EPW and DDY files should have identical names, as the directory name will be based on these file names. Ensure the names of the EPW and its corresponding DDY file are identical. For instance, specifying 'Trondheim' implies that 'Trondheim.epw' and 'Trondheim.ddy' files are available in the offline_weather_dir directory.

## Step 3: EP Simulation details
For next step the user is required to make ceratin decisions and provide information.
Settings for Step 3 in [Config_input.yaml](https://github.com/gaurav306/synconn_build/blob/main/Config_input.yaml#L29) are as follows:

```yaml
ep_simualtion_data_details:
  ep_template_file: 'src/0_5-ZONE_VRF_BASEBORD_template.idf'
  run_ep_or_justmakeidf: 1
  number_of_stochastic_EP_cases_to_generate: 1
  unique_prefix_for_each_stochastic_case: 'sample'
  running_mode: full 
  random_holidays: True
  random_occupancy: True
  random_HVAC_mode: True
  random_window_opening: True
```
* **ep_template_file**: Specify the EnergyPlus template IDF file to be used for the simulation.
* **run_ep_or_justmakeidf**: Specify whether to run the EnergyPlus simulations (`1`) or just create the IDF files (`0`).
* **number_of_stochastic_EP_cases_to_generate**: Define the number of stochastic EnergyPlus cases you want to generate.
* **unique_prefix_for_each_stochastic_case**: This can be any string and is used to distinguish between different stochastic cases.
* **running_mode**: Choose the simulation duration. If set to `debug`, the simulation runs from October 1st to December 31st. If set to `full`, the simulation runs for the full year.
* **random_holidays**: If set to `True`, holidays are randomly selected from the list in `src/random_holidays_EPobjects_list.csv`. If `False`, no holidays are considered in the simulation, and weekends are not considered as holidays.
* **random_occupancy**: If set to `True`, occupancy is randomly generated using the OB_GENERATOR. If set to `False`, occupancy is fixed to EP schedule `OCCUPY-1`.
* **random_HVAC_mode**: If set to `True`, the HVAC mode is randomly selected from the list `[0,1,2,3]`, which corresponds to `[Off, Heat, Cool, Dual]`. If set to `False`, the HVAC mode is set to `3` (Dual).
* **random_window_opening**: If set to `True`, the window-opening schedule is determined by the radnom signal generated. If set to `False`, the windows are always closed.

## Step 4: Signal generation details
*Synconn_build* allows user to use random signals for heating setpoints, HVAC mode and widnow opening signal. User can also inject noise to heating setpoints. All these four random signal are generated by [Signal_Generator.py](https://github.com/gaurav306/synconn_build/blob/main/src/Signal_Generator.py) **for every zone in the case-study building individually**. The settings required for 4 signals can be inputted in [Config_input.yaml](https://github.com/gaurav306/synconn_build/blob/main/Config_input.yaml#L64)  as follows:

```yaml
signal_generator_details:
  if_plot: 0
  frequency_categories: ['5 high', '4 high-medium', '3 medium', '2 medium-low', '1 low']
  mprs_setpoints:
    normal_or_uniform_distribution: normal
    if_multiple_frequency_signal: 1
    minmax_splits: [3,16]
    frequency: 1 low
    possible_bits: [18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22]
    stay_steps_possible: [0]
    tightness_for_frequencies: [3, 6, 9, 12, 15]

  C_H_difference: 5

  mprs_hvac_mode:
    if_multiple_frequency_signal: 1
    minmax_splits: [3,16]
    frequency: 1 low
    possible_bits: [0,1,2,3]
    stay_steps_possible: [0]
    minimum_one_mode: 12
    tightness_for_frequencies: [24, 48, 72, 96, 120]
  
  minimum_window_opening_frequency: 6 

  prbs_win_multiple_multistep:
    if_multiple_frequency_signal: 1
    minmax_splits: [3,16]
    frequency: 1 low
    possible_bits: [0.25, 0.5, 0.75, 1]
    stay_steps_possible: [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    tightness_for_frequencies: [24, 48, 72, 96, 120]

  noise_for_setpoints:
    noise_or_all_zero: 1
    mean_of_noise: 0
    std_dev_of_noise: 0.1
    if_multiple_frequency_signal: 0
    frequency: 1 low               
    possible_bits: []              
    stay_steps_possible: []        
    tightness_for_frequencies: []  
```
here **mprs_setpoints**, **mprs_hvac_mode**, **prbs_win_multiple_multistep**, **noise_for_setpoints** are the four signals generated by [Signal_Generator.py](https://github.com/gaurav306/synconn_build/blob/main/src/Signal_Generator.py).
* **if_plot**: Set to **0** to disable plotting.
* **frequency_categories**: This is fixed list of frequency of change ranging from high to low. SHOULD NOT BE CHANGED
* **mprs_setpoints**: following settings determines the randomness of signal for heating setpoints
    * **normal_or_uniform_distribution**: User can choose the type of distribution for this signal
    * **if_multiple_frequency_signal** Set to **1** to allow for random frequencies throughout the year, or **0** to maintain the same frequency.
    * **minmax_splits** Define the number of frequency splits if **if_multiple_frequency_signal** is **1**.
    * **frequency** Define the type of frequency if **if_multiple_frequency_signal** is **0**. This should be one of the **frequency_categories**.
    * **possible_bits** Define the possible values of the signal.
    * **stay_steps_possible** Define the number of steps the signal can remain at the same value.
    * **tightness_for_frequencies** Define the tightness of the signal for each frequency. Refer to the formula in the code for more details.

* **mprs_hvac_mode**
    * **if_multiple_frequency_signal**, **minmax_splits**, **frequency**, **possible_bits**, **stay_steps_possible** and **tightness_for_frequencies** are used similarly to **mprs_setpoints**.
    * **minimum_one_mode** Define the minimum number of hours for the current HVAC mode.

* **C_H_difference** Define the difference between cooling and heating setpoints.

* **minimum_window_opening_frequency** Define the minimum number of hours the window will remain closed once it is shut.

* **prbs_win_multiple_multistep** This section has similar settings to **mprs_setpoints** and **mprs_hvac_mode**.

* **noise_for_setpoints**
    * **noise_or_all_zero** Set to **1** to make the signal noisy, or to **0** to make the signal all zeros.
    * **mean_of_noise** Set the mean value of the noise.
    * **std_dev_of_noise** Set the standard deviation of the noise.
    * The remaining parameters are not significant for this section but included for consistency.


## Step 5: Run_main.py : generate dataset

[Run_main.py](https://github.com/gaurav306/synconn_build/blob/main/Run_main.py) is used to trigger other components of the tool to generate the dataset. 

```python

import os, sys, pkg_resources, subprocess
from time import sleep
import yaml

def are_python_requirements_installed(requirements_file):
    with open(requirements_file, 'r') as f:
        requirements = f.read().splitlines()
    for requirement in requirements:
        try:
            dist = pkg_resources.get_distribution(requirement)
            print("{} ({}) is installed in Python".format(dist.key, dist.version))
        except pkg_resources.DistributionNotFound:
            print("{} is NOT installed in Python.".format(requirement))
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])

def is_EnergyPlus_installed(idd_file_add):
    if os.path.isfile(idd_file_add):
        print('EnergyPlusV22-1-0 is installed')
    else:
        print('EnergyPlusV22-1-0 is NOT installed')
        sys.exit(1)

def synconn_build(yaml_configs):
    if yaml_configs['weather_files']['get_epw'] == 'online':
        epw_urls = yaml_configs['weather_files']['epw_urls']
        for epw_url in epw_urls:
            main_dir, epw_name, city_name = EP_Generator.download_epw_create_directory(epw_url, yaml_configs)
            ''''''
            for i in range(yaml_configs['ep_simualtion_data_details']['number_of_stochastic_EP_cases_to_generate']):
                EP_Generator.run_stochastic_EP(i, main_dir, epw_name, city_name, yaml_configs)
                sleep(0.5)
    
    if yaml_configs['weather_files']['get_epw'] == 'offline':
        epw_ddy_names = yaml_configs['weather_files']['epw_ddy_names']
        for epw_ddy_name in epw_ddy_names:
            main_dir, epw_name, city_name = EP_Generator.import_epw_create_directory(epw_ddy_name, yaml_configs)
            ''''''
            for i in range(yaml_configs['ep_simualtion_data_details']['number_of_stochastic_EP_cases_to_generate']):
                EP_Generator.run_stochastic_EP(i, main_dir, epw_name, city_name, yaml_configs)
                sleep(0.5)
            
        
if __name__ == '__main__':
    # Check if all python requirements are installed
    are_python_requirements_installed("requirements.txt")

    # Load configuration file as dictionary
    import src.EP_Generator as EP_Generator
    with open('Config_input.yaml', 'r') as file:   #r'../config.yaml'
        yaml_configs = yaml.safe_load(file)    

    # Check if EnergyPlusV22-1-0 is installed
    is_EnergyPlus_installed(yaml_configs['energyplus_init']['idd_dir'])

    # Run EP_gen_main
    synconn_build(yaml_configs)

```

Functions **are_python_requirements_installed()** and **is_EnergyPlus_installed()** are used to check if all python requirements are installed and if EnergyPlusV22-1-0 is installed, respectively. **are_python_requirements_installed()** takes input [requirements.txt](https://github.com/gaurav306/synconn_build/blob/main/requirements.txt) which lists all packages required by python.
Function **synconn_build()** calls EP_Generator functions to start data generation pipeline. It takes Config_input.yaml data in form of a dictionary as input. Before **synconn_build** is called, the user can do further changes to configuration dictionary as per needs.