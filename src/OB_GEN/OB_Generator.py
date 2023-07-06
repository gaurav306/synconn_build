from time import sleep
import src.OB_GEN.OB_Generator_utils as utils
def ob_gen(yaml_configs):
    #read yaml
    #with open(r'../config.yaml', 'r') as file:
        #yaml_configs = yaml.safe_load(file)
    utils.preprocess_files(yaml_configs)
    utils.run_bat_file()
    sleep(1)
    utils.copy_ob_result_files(yaml_configs)
    sleep(1)
    utils.delete_OB_simulation_files()

if __name__ == '__main__':
    ob_gen()