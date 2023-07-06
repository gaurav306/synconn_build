import io
import os, sys, glob
import shutil
import zipfile
import requests
import src.EP_Generator_utils as EP_Generator_utils
from eppy.modeleditor import IDF
from src.Signal_Generator import generate_signal_for_EP
from src.OB_GEN.OB_Generator import ob_gen


def download_epw_create_directory(epw_url, configs):
    epw_name = os.path.basename(epw_url).replace('.zip','')
    r = requests.get(epw_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    city_name = epw_name.split('_')[0] + '_' + epw_name.split('_')[1] + '_' + epw_name.split('.')[-1].split('_')[0]
    print('City name: ', city_name)
    main_dir = 'Dataset_outout/'+ city_name
    z.extractall(main_dir)
    os.remove(main_dir + '/' +epw_name+'.clm')
    os.remove(main_dir + '/' +epw_name+'.pvsyst')
    os.remove(main_dir + '/' +epw_name+'.rain')
    os.remove(main_dir + '/' +epw_name+'.stat')
    os.remove(main_dir + '/' +epw_name+'.wea')

    return main_dir, epw_name, city_name

def import_epw_create_directory(epw_ddy_name, configs):

    offlineweather_dir = configs['weather_files']['offline_weather_dir']
    isExist_epw = os.path.exists(r'%s/%s.epw' % (str(offlineweather_dir), str(epw_ddy_name)))
    isExist_ddy = os.path.exists(r'%s/%s.ddy' % (str(offlineweather_dir), str(epw_ddy_name)))
    
    if not isExist_epw or not isExist_ddy:
        print('EPW/DDY files does not exist! Check if both of the file names:%s.epw/.ddy, is correct and exists in folder: Offline_weather_files_input' % str(epw_ddy_name))
        sys.exit(1)

    city_name = epw_ddy_name
    print('City name: ', city_name)
    main_dir = 'Dataset_outout/'+ city_name
    os.makedirs(main_dir, exist_ok=True)
    
    src = r'%s/%s.epw' % (str(offlineweather_dir), str(epw_ddy_name))
    dst = main_dir + r'/%s.epw' % str(epw_ddy_name)
    shutil.copyfile(src, dst)

    src = r'%s/%s.ddy' % (str(offlineweather_dir), str(epw_ddy_name))
    dst = main_dir + r'/%s.ddy' % str(epw_ddy_name)
    shutil.copyfile(src, dst)

    return main_dir, epw_ddy_name, city_name

def check_if_enough_OB_files(configs):
    #check if there are enough OB files to run the simulation
    OB_files_dir = r'../OB_GEN'
    number_of_OB_files = 0
    files = glob.glob(OB_files_dir+"/*.csv")
    prefix = OB_files_dir+'\\OB_interval_%smin_sched_' %str(int(60 / int(configs['energyplus_init']['timestep'])))
    for file in files:
        if file.startswith(prefix):
            number_of_OB_files = number_of_OB_files + 1
    
    '''
    number_of_OB_files_should_be = int(configs['ep_simualtion_data_details']['number_of_stochastic_EP_cases_to_generate'])
    if number_of_OB_files_should_be > number_of_OB_files:
        print('There are not enough OB files in the folder: %s' % OB_files_dir)
        sys.exit(1)
    else:
        print('There are enough OB files in the folder: %s - %s' % (str(OB_files_dir), str(number_of_OB_files)))
    '''
    
def edit_copy_EPlus_bat(filename_source, filename_target, text, replace_text):
    with open(filename_source, 'r') as file :
        filedata = file.read()
    filedata = filedata.replace(text, replace_text)
    with open(filename_target, 'w') as file:
        file.write(filedata)

def run_stochastic_EP(sim_number, main_dir, epw_name, city_name, configs):
    #sim_number = 0
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<sim_number:',sim_number)
    
    iddfile                 = configs['energyplus_init']['idd_dir']
    TempIDF                 = configs['ep_simualtion_data_details']['ep_template_file']
    energyplus_install_dir  = configs['energyplus_init']['ep_dir']
    
    epw_relative_filepath = main_dir + '/' +epw_name+'.epw'
    prefix = city_name+'_%s_' % sim_number

    ddy_file     = main_dir + '/' +epw_name+'.ddy'
    IDF.setiddname(iddfile)
    idf_data    = IDF(TempIDF)
    ddy_data    = IDF(ddy_file)

    interval = int(60 / int(configs['energyplus_init']['timestep']))

    prefix_for_output = configs['ep_simualtion_data_details']['unique_prefix_for_each_stochastic_case']
    type_of_sim = prefix_for_output + '_%s_%s' % (str(sim_number),str(interval))
    #type_of_sim = prefix_for_output + 'sim_%s' % (str(sim_number))
    
    sim_dir = main_dir + '/' + type_of_sim
    sim_temp_dir = main_dir + '/' + type_of_sim + '/temp'

    #create directories
    print("Creating directories for simulation: ", sim_dir)
    os.makedirs(sim_dir, exist_ok=True)
    os.makedirs(sim_temp_dir, exist_ok=True)

    #make Signals_inputs.csv in temp folder
    signals_file = sim_temp_dir + r'/Signals_inputs_%s.csv' % sim_number
    print("Generating Signals_inputs.csv for simulation: ", signals_file)
    generate_signal_for_EP(signals_file, configs)
    
    #copy OB_schedule.csv to temp folder
    print("Creating OB_schedule.csv and copy to temp folder")
    ob_gen(configs)
    interval = int(60 / int(configs['energyplus_init']['timestep']))
    ob_file_name = r'OB_interval_%smin_sched.csv' % (str(interval))
    #ob_file_name = r'OB_interval_%smin_sched_%s.csv' % (str(interval),str(sim_number))
    src = r'src/OB_GEN/' + ob_file_name
    dst = sim_temp_dir + '/' + ob_file_name
    shutil.copyfile(src, dst)

    edit_copy_EPlus_bat('src/RunEPlus_template.bat',
                    sim_temp_dir + r'/RunEPlus.bat',
                    '%%Ep_dir%%', 
                    configs['energyplus_init']['ep_dir'])

    #copy epw file to temp folder
    src = main_dir + r'/%s.epw' % epw_name  
    dst = sim_temp_dir + r'/%s.epw' % epw_name
    shutil.copyfile(src, dst)

    # change the idf file temp
    idf_data =  EP_Generator_utils.running_mode(configs['ep_simualtion_data_details']['running_mode'], idf_data)
    timestep_config = configs['energyplus_init']['timestep']
    idf_data =  EP_Generator_utils.change_timestep(True, idf_data, timestep_config)
    idf_data = EP_Generator_utils.change_FileSchedule_names(True, idf_data, ob_file_name, 'Signals_inputs_%s.csv' % sim_number)
    idf_data = EP_Generator_utils.add_ddy_objects(True ,True ,idf_data, ddy_data)
    
    if configs['ep_simualtion_data_details']['random_holidays']:
        idf_data = EP_Generator_utils.add_holidays(True, idf_data)
    else:
        idf_data = EP_Generator_utils.add_holidays(False, idf_data)
    
    if configs['ep_simualtion_data_details']['random_occupancy']:
        idf_data = EP_Generator_utils.stochastic_occupancy(True, idf_data)
    else:
        idf_data = EP_Generator_utils.stochastic_occupancy(False, idf_data)
    
    if configs['ep_simualtion_data_details']['random_window_opening']:
        idf_data = EP_Generator_utils.random_window_opening(True, idf_data)
    else:
        idf_data = EP_Generator_utils.random_window_opening(False, idf_data)
    
    
    idf_relative_filepath = sim_temp_dir + '/' +city_name+'_EnergyPlus_file_%s.idf' % sim_number
    idf_data.saveas(idf_relative_filepath)


    if configs['ep_simualtion_data_details']['run_ep_or_justmakeidf']:
        bat_idf_name = city_name+'_EnergyPlus_file_%s' % sim_number
        bat_epw_name = epw_name
        bat_sim_temp_dir = sim_temp_dir.replace('/', '\\')
        cmd_command = r'pushd %s && RunEPlus.bat %s %s' % (bat_sim_temp_dir, bat_idf_name, bat_epw_name)
        os.system(cmd_command)
        
        #copy output csv files to main folder
        src = sim_temp_dir + r'/%s.csv' % bat_idf_name
        dst = sim_dir + '/' + '%s_%s_output.csv' % (city_name , sim_number)
        shutil.copyfile(src, dst)
        
        os.remove(sim_temp_dir + r'/%s.csv' % bat_idf_name)
        os.remove(sim_temp_dir + r'/%s.err' % bat_idf_name)

        print()
