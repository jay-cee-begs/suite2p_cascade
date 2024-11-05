
## Configurations ##
####    these variables need to be edited if running from different folders/PCs    ####
main_folder = r"D:\zeiss\Desktop\rotation_stud\EXAMPLE_DATA"  ## main folder where the different subfolders are in
group1 = main_folder+r"\high pH APV" ## folder group 1, keep \ that way
group2 = main_folder+r"\high pH with cysteine" ## folder group 2, keep \ that way
#group3 = main_folder+r"\normal pH" ## folder group 3 keep \ that way
#group4 = main_folder+r"\pre image normal pH"
#group5 = main_folder+r"\tx1 high pH" ## folder group 1, keep \ that way
#group6 = main_folder+r"\tx1 high pH cysteine" ## folder group 2, keep \ that way
#group7 = main_folder+r"\tx1 high pH APV" ## folder group 3 keep \ that way
#group8 = main_folder+r"\tx1 normal pH"
#group9 = main_folder+r"\tx2 high pH" ## folder group 1, keep \ that way
#group10 = main_folder+r"\tx2 high pH cysteine" ## folder group 2, keep \ that way
#group11 = main_folder+r"\tx2 high pH APV" ## folder group 3 keep \ that way
#group12 = main_folder+r"\tx2 normal pH" ## folder group 3 keep \ that way
#group13 = main_folder+r"\wash high pH" ## folder group 1, keep \ that way
#group14 = main_folder+r"\wash high pH cysteine" ## folder group 2, keep \ that way
#group15 = main_folder+r"\wash high pH APV" ## folder group 3 keep \ that way
#group16 = main_folder+r"\wash normal pH"

group_number = 2 # prevents issue with for variable in locals()

cascade_file_path = r"D:\users\JC\Cascade-master" ## CASCADE master folder

frame_rate = 10

## plot a set of nb_neurons randomly chosen neuronal traces (first seconds)
nb_neurons = 16 ## maybe put directly into cascade_this???

model_name = "Global_EXC_10Hz_smoothing200ms" 
## select fitting model from list (created in cascada code) ##
## list still in CASCADE code, maybe add here##

EXPERIMENT_DURATION = 60
 
FRAME_INTERVAL = 1 / frame_rate
 
BIN_WIDTH =  20 
#SET TO APPROX 200ms
 
FILTER_NEURONS = True

groups = []
for n in range(group_number):
    group_name = f"group{n+1}"
    if group_name in locals():
        groups.append(locals()[group_name])

