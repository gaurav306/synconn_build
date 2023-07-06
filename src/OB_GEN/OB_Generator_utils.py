
import glob, os, shutil
from eppy.modeleditor import IDF

def replace_in_textfile(filename_source, filename_target, text, replace_text):
    with open(filename_source, 'r') as file :
        filedata = file.read()
    filedata = filedata.replace(text, replace_text)
    with open(filename_target, 'w') as file:
        file.write(filedata)

def replace_in_textfile_timestep_XML(filename_source, filename_target, timestep):
    with open(filename_source, 'r') as file :
        filedata = file.read()
    replace_text = '<NumberofTimestepsPerHour>%s</NumberofTimestepsPerHour>' % str(timestep)
    for i in range(1, 61):
        filedata = filedata.replace('<NumberofTimestepsPerHour>%s</NumberofTimestepsPerHour>' % str(i), 
                                replace_text)
    with open(filename_target, 'w') as file:
        file.write(filedata)

def run_bat_file():
    # run a bat file to run obFMU in energyplus environmet in command line
    cmd_command = r'pushd "src\OB_GEN\src\simfolder" && RunEPlus.bat 5Zone_obFMU weather'
    os.system(cmd_command)
    
def copy_ob_result_files_numbered(configs):
    #os.chdir(r'')
    files = glob.glob("*.csv")
    prefix = 'OB_interval_%smin_sched_' %str(int(60 / int(configs['energyplus_init']['timestep'])))
    print(prefix)
    if len(files) > 0:
        file_nums = []
        for file in files:
            if file.startswith(prefix):
                file_nums.append(int(file.split(prefix)[-1].split('.csv')[0]))
        if len(file_nums) > 0:
            file_number = max(file_nums) + 1
        else:
            file_number = 0
    else:
        file_number = 0
    interval = int(60 / int(configs['energyplus_init']['timestep']))
    src = r'src/OB_GEN/src/output_IDF.csv'
    dst = r'src/OB_GEN/OB_interval_%smin_sched_%s.csv' % (str(interval),str(file_number))
    shutil.copyfile(src, dst)

def copy_ob_result_files(configs):
    interval = int(60 / int(configs['energyplus_init']['timestep']))
    src = r'src/OB_GEN/src/output_IDF.csv'
    dst = r'src/OB_GEN/OB_interval_%smin_sched.csv' % (str(interval))
    shutil.copyfile(src, dst)


def copy_OB_simulation_files():
    # copy the obFMU simulation files to the simulation folder
    src = r"src/OB_GEN/src/simfolder/obCoSim.xml"
    dst = r"src/OB_GEN/src/obCoSim.xml"
    shutil.copyfile(src, dst)

    src = r"src/OB_GEN/src/simfolder/obFMU.fmu"
    dst = r"src/OB_GEN/src/obFMU.fmu"
    shutil.copyfile(src, dst)

    src = r"src/OB_GEN/src/simfolder/obXML.xml"
    dst = r"src/OB_GEN/src/obXML.xml"
    shutil.copyfile(src, dst)

def delete_OB_simulation_files():
    os.remove("src/OB_GEN/src/obCoSim.xml")
    os.remove("src/OB_GEN/src/obFMU.fmu")
    os.remove("src/OB_GEN/src/obXML.xml")
    os.remove("src/OB_GEN/src/output_IDF.idf")
    os.remove("src/OB_GEN/src/simfolder/5Zone_obFMU.csv")
    os.remove("src/OB_GEN/src/simfolder/5Zone_obFMU.err")
    os.remove("src/OB_GEN/src/output.csv")
    os.remove("src/OB_GEN/src/output_by_Occupant.csv")
    os.remove("src/OB_GEN/src/output_IDF.csv")
    os.remove("src/OB_GEN/src/SPACE1-1.csv")
    os.remove("src/OB_GEN/src/SPACE2-1.csv")
    os.remove("src/OB_GEN/src/SPACE3-1.csv")
    os.remove("src/OB_GEN/src/SPACE4-1.csv")
    os.remove("src/OB_GEN/src/SPACE5-1.csv")

def change_timestep(configs):
    iddfile                 = configs['energyplus_init']['idd_dir']
    IDF_file                = "src/OB_GEN/src/simfolder/5Zone_obFMU.idf"
    IDF.setiddname(iddfile)
    idf_data    = IDF(IDF_file)
    idf_data.idfobjects['Timestep'][0].Number_of_Timesteps_per_Hour = configs['energyplus_init']['timestep']
    idf_data.save()
    replace_in_textfile_timestep_XML('src/OB_GEN/src/simfolder/obCoSim.xml',
                                    'src/OB_GEN/src/simfolder/obCoSim.xml',
                                    configs['energyplus_init']['timestep'])
    
def preprocess_files(configs):

    ep_dir = configs['energyplus_init']['ep_dir']
    
    replace_in_textfile('src/OB_GEN/src/simfolder/RunEPlus_template.bat',
                        'src/OB_GEN/src/simfolder/RunEPlus.bat',
                        '%%Ep_dir%%', 
                        ep_dir)
    
    change_timestep(configs)

    copy_OB_simulation_files()