import pandas as pd
import random
 
holidaysfile = 'src/random_holidays_EPobjects_list.csv'

def add_ddy_objects(command1 ,command2 ,idf1,ddy_data): 
    """
        #Add Sizing:DesignDay object from .ddy file to IDF
        command1 is a boolean to add the ddy objects or not
            if command1 is True and command2 is True, then add only the min and max temperature design days
        idf1 is the original IDF file
        ddy_data is the .ddy file
    """
    print()
    print('add_designday function:',command1)
    print('IDF originaly has %s DesignDay objects' % str(len(idf1.idfobjects['SizingPeriod:DesignDay'])))
    
    min_temp = 100
    min_temp_index = 0
    max_temp = -100
    max_temp_index = 0
    for i in range(0,len(ddy_data.idfobjects['SizingPeriod:DesignDay'])):
        if ddy_data.idfobjects['SizingPeriod:DesignDay'][i].Maximum_DryBulb_Temperature < min_temp:
            min_temp = ddy_data.idfobjects['SizingPeriod:DesignDay'][i].Maximum_DryBulb_Temperature
            min_temp_index = i
        if ddy_data.idfobjects['SizingPeriod:DesignDay'][i].Maximum_DryBulb_Temperature > max_temp:
            max_temp = ddy_data.idfobjects['SizingPeriod:DesignDay'][i].Maximum_DryBulb_Temperature
            max_temp_index = i
    print('min_temp_index',min_temp_index)
    print('max_temp_index',max_temp_index)
    print('min_temp',min_temp)
    print('max_temp',max_temp)

    for _ in range(0,len(idf1.idfobjects['SizingPeriod:DesignDay'])):                   #remove old DesignDay object
        remove_object = idf1.idfobjects['SizingPeriod:DesignDay'][-1]
        idf1.removeidfobject(remove_object)
    for _ in range(0,len(idf1.idfobjects['SizingPeriod:WeatherFileConditionType'])):    #remove old WeatherFileConditionType object
        remove_object = idf1.idfobjects['SizingPeriod:WeatherFileConditionType'][-1]
        idf1.removeidfobject(remove_object)
    for _ in range(0,len(idf1.idfobjects['Site:Location'])):                            #remove old Site:Location object
        remove_object = idf1.idfobjects['Site:Location'][-1]
        idf1.removeidfobject(remove_object)
    
    if command1:
        if command2:
            idf1.copyidfobject(ddy_data.idfobjects['SizingPeriod:DesignDay'][min_temp_index])
            idf1.copyidfobject(ddy_data.idfobjects['SizingPeriod:DesignDay'][max_temp_index])
            print('IDF has %s DesignDay objects' % str(len(idf1.idfobjects['SizingPeriod:DesignDay'])))
        else:
            for sizing_day in ddy_data.idfobjects['SizingPeriod:DesignDay']:
                idf1.copyidfobject(sizing_day)
            print('IDF has %s DesignDay objects' % str(len(idf1.idfobjects['SizingPeriod:DesignDay'])))
        for site_location in ddy_data.idfobjects['Site:Location']:
            idf1.copyidfobject(site_location)
        print('IDF has %s Site:Location objects' % str(len(idf1.idfobjects['Site:Location'])))
        print(idf1.idfobjects['Site:Location'][0])
    
    return idf1

def add_holidays(command,idf1): #Add random holidays from holidayslist.csv
    print()
    print('add_holidays function:',command)
    print('IDF has %s holidays objects' % str(len(idf1.idfobjects['RunPeriodControl:SpecialDays'])))
    for i in range(0,len(idf1.idfobjects['RunPeriodControl:SpecialDays'])):  #remove old holidays list
        remove_object = idf1.idfobjects['RunPeriodControl:SpecialDays'][-1]
        idf1.removeidfobject(remove_object)                

    if command:
        holidays  = pd.read_csv(holidaysfile, sep=',', header=0)
        x = random.sample(range(1, 100), 25)
        x.sort()
        print(x)
        for i in x:
            newobject = idf1.newidfobject("RunPeriodControl:SpecialDays")
            newobject.Name       = holidays['Name'][i-1]
            newobject.Start_Date = holidays['Dates'][i-1]    
    
    print('Current top 5 holidays in IDF, if any')
    print('IDF has %s holidays objects' % str(len(idf1.idfobjects['RunPeriodControl:SpecialDays'])))
    for i,ix in zip(idf1.idfobjects['RunPeriodControl:SpecialDays'],range(0,5)):
        print(ix,'--',i.Name,'--',i.Start_Date)
    
    return idf1

def running_mode(command,idf1):  #running mode, debug = 2 months, full = 1 year
    print()
    print('running_mode function:',command)
    if command == 'debug':
        idf1.idfobjects['RunPeriod'][0].Begin_Month = 11
        idf1.idfobjects['RunPeriod'][0].Begin_Day_of_Month = 1
        idf1.idfobjects['RunPeriod'][0].End_Month = 12
        idf1.idfobjects['RunPeriod'][0].End_Day_of_Month = 31
        print(idf1.idfobjects['RunPeriod'])
    elif command == 'full':
        idf1.idfobjects['RunPeriod'][0].Begin_Month = 1
        idf1.idfobjects['RunPeriod'][0].Begin_Day_of_Month = 1
        idf1.idfobjects['RunPeriod'][0].End_Month = 12
        idf1.idfobjects['RunPeriod'][0].End_Day_of_Month = 31    
        print(idf1.idfobjects['RunPeriod'])

    return idf1

def remove_externalinterface(command, idf1):
    print()
    print('remove_externalinterface function:',command)
    if command:
        print('IDF had %s ExternalInterface objects' % str(len(idf1.idfobjects['ExternalInterface'])))
        for i in range(0,len(idf1.idfobjects['ExternalInterface'])):  #remove ExternalInterface object
            remove_object = idf1.idfobjects['ExternalInterface'][-1]
            idf1.removeidfobject(remove_object) 
        
        for i in range(0,len(idf1.idfobjects['ExternalInterface:FunctionalMockupUnitImport'])):  #remove ExternalInterface:FunctionalMockupUnitImport object
            remove_object = idf1.idfobjects['ExternalInterface:FunctionalMockupUnitImport'][-1]
            idf1.removeidfobject(remove_object) 
        
        for i in range(0,len(idf1.idfobjects['ExternalInterface:FunctionalMockupUnitImport:From:Variable'])):  #remove ExternalInterface:FunctionalMockupUnitImport:From:Variable object
            remove_object = idf1.idfobjects['ExternalInterface:FunctionalMockupUnitImport:From:Variable'][-1]
            idf1.removeidfobject(remove_object) 
        
        for i in range(0,len(idf1.idfobjects['ExternalInterface:FunctionalMockupUnitImport:To:Schedule'])):  #remove ExternalInterface:FunctionalMockupUnitImport:To:Schedule object
            remove_object = idf1.idfobjects['ExternalInterface:FunctionalMockupUnitImport:To:Schedule'][-1]
            idf1.removeidfobject(remove_object) 
        
        print('IDF now has %s ExternalInterface objects' % str(len(idf1.idfobjects['ExternalInterface'])))

        for i in range(len(idf1.idfobjects['Schedule:File'])):
            if idf1.idfobjects['Schedule:File'][i].File_Name == 'output_IDF.csv':
                idf1.idfobjects['Schedule:File'][i].File_Name = 'output_IDF_same_occupancy.csv'
                print('Schedule:File object changed to output_IDF_same_occupancy.csv')
    return idf1

def stochastic_occupancy(command,idf1): #either stochastic occupancy or not            
    print()
    print('stochastic_occupancy function:',command)
    if command:
        for i in range(5):
            idf1.idfobjects['People'][i].Number_of_People_Schedule_Name = 'P%s' %str(i+1) 
    else:
        for i in range(5):
            idf1.idfobjects['People'][i].Number_of_People_Schedule_Name = 'OCCUPY-1'
    return idf1

def random_setpoints_mode(command,idf1): #either stochastic occupancy or not            
    print()
    print('random_HVAC_mode function:',command)
    if command:
        for i in range(5):
            idf1.idfobjects['ZoneControl:Thermostat'][i].Control_1_Name = 'SPACE%s Dual SP Control' %str(i+1)             
    else:
        for i in range(5):
            idf1.idfobjects['ZoneControl:Thermostat'][i].Control_1_Name = 'Fixed_all'
    return idf1

def random_window_opening(command,idf1):             
    print()
    print('random_window_opening function:',command)
    if command:
        idf1.idfobjects['EnergyManagementSystem:ProgramCallingManager'][0].Program_Name_3 = 'WINDOW_OPENING_WITH_SCHEDULE_AND_THERSHOLD_OAT'
            
    else:
        idf1.idfobjects['EnergyManagementSystem:ProgramCallingManager'][0].Program_Name_3 = 'WINDOW_CLOSED'
    return idf1

def change_FileSchedule_names(command, idf1, filename1, filename2):
    print()
    print('change_schedulefile_name function:',command)
    if command:
        for i in range(len(idf1.idfobjects['Schedule:File'])):
            if idf1.idfobjects['Schedule:File'][i].File_Name == 'output_IDF_same_occupancy.csv':
                idf1.idfobjects['Schedule:File'][i].File_Name = filename1
                print('Schedule:File object changed to %s' % filename1)
            if idf1.idfobjects['Schedule:File'][i].File_Name == 'Signals_inputs.csv':
                idf1.idfobjects['Schedule:File'][i].File_Name = filename2
                print('Schedule:File object changed to %s' % filename2)
    return idf1

def change_timestep(command, idf1, timestep):
    print()
    print('change_timestep function:',command)
    if command:
        idf1.idfobjects['Timestep'][0].Number_of_Timesteps_per_Hour = timestep
        for i in range(len(idf1.idfobjects['Schedule:File'])):
            idf1.idfobjects['Schedule:File'][i].Minutes_per_Item = 60/timestep
        
        print('Timestep changed to %s' % timestep)
    return idf1