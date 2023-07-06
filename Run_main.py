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
        print('EnergyPlus is installed')
    else:
        print('EnergyPlus is NOT installed')
        sys.exit(1)

def EP_gen_main(yaml_configs):
    if yaml_configs['weather_files']['get_epw'] == 'online':
        epw_urls = yaml_configs['weather_files']['epw_urls']
        for epw_url in epw_urls:
            main_dir, epw_name, city_name = download_epw_create_directory(epw_url, yaml_configs)
            ''''''
            for i in range(yaml_configs['ep_simualtion_data_details']['number_of_stochastic_EP_cases_to_generate']):
                run_stochastic_EP(i, main_dir, epw_name, city_name, yaml_configs)
                sleep(0.5)
    
    if yaml_configs['weather_files']['get_epw'] == 'offline':
        epw_ddy_names = yaml_configs['weather_files']['epw_ddy_names']
        for epw_ddy_name in epw_ddy_names:
            main_dir, epw_name, city_name = import_epw_create_directory(epw_ddy_name, yaml_configs)
            ''''''
            for i in range(yaml_configs['ep_simualtion_data_details']['number_of_stochastic_EP_cases_to_generate']):
                run_stochastic_EP(i, main_dir, epw_name, city_name, yaml_configs)
                sleep(0.5)
            
        
if __name__ == '__main__':
    # Check if all python requirements are installed
    are_python_requirements_installed("requirements.txt")

    # load configuaration file as dictionary
    from src.EP_Generator import *
    with open('Config_input.yaml', 'r') as file:   #r'../config.yaml'
        yaml_configs = yaml.safe_load(file)    

    # Check if EnergyPlus is installed
    is_EnergyPlus_installed(yaml_configs['energyplus_init']['idd_dir'])

    # Run EP_gen_main

    #yaml_configs['ep_simualtion_data_details']['unique_prefix_for_each_stochastic_case'] = 'GEO_CH_'
    #yaml_configs['ep_simualtion_data_details']['ep_template_file'] = 'src/0_5-ZONE_VRF_BASEBORD_template_GC_geo_changed.idf'
    #EP_gen_main(yaml_configs)

    #yaml_configs['ep_simualtion_data_details']['unique_prefix_for_each_stochastic_case'] = 'TEST_'
    #yaml_configs['ep_simualtion_data_details']['ep_template_file'] = 'src/0_5-ZONE_VRF_BASEBORD_template_GC.idf'
    #EP_gen_main(yaml_configs)

