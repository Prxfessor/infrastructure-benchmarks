import os
import csv
import datetime
from datetime import timedelta
import math
from os import path

# TODO:
    # maybe convert all elapsed wall clock into seconds (check the tableau for issues)
    # test out the standard deviation to see if it is right

# check if the file exists here:
average_file = "averaged_time.csv"
SD_file = "standard_deviation.csv"


# if the files exist, get rid of them - so that when we append, it doesnt add onto existing data
if (path.exists(SD_file)):
    os.remove(SD_file)

if (path.exists(average_file)):
    os.remove(average_file)



ALL_DATA = {}
AVERAGED_DATA = []

#### STEP 1: check all the folders that are in iterations ###
# folder names stored here
iteration_folders = []

# check how many folders there are in the iterations folder
# doing plus 1 as the numbers start from 1
number_of_iterations = 0
while(os.path.isdir("iterations/iteration_" + str(number_of_iterations + 1))):
    iteration_folders.append("iteration_" + str(number_of_iterations + 1))
    number_of_iterations = number_of_iterations + 1

#### STEP 2: Store data from the file as Dict {iteration_num : values} ####
for folder in iteration_folders:
    # getting the times.csv file open
    file_path = "iterations/" + folder + "/times.csv"
    # create the dictionary key and value pair for that iteration
    ALL_DATA[folder] = []

    # read the data into the dict
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        next(reader, None)      
        for row in reader:
            # append the data to the dictionary
            ALL_DATA[folder].append(row)

measurement_titles = [
    "Architecture",
    "Application",
    "N",
    "User time (seconds)",
    "System time (seconds)",
    "Percent of CPU this job got",
    "Elapsed (wall clock) time",
    "Maximum resident set size (kbytes)",
    ]




## STEP 3: WORK OUT THE AVERAGE AND STANDARD DEVIATION ##
# for each line in each of the csv files
for line in range(len(ALL_DATA["iteration_1"])): 
    architecture = ""
    application = ""
    N = ""
    user_time = []
    system_time = []
    cpu_percent = []
    memory = []
    wall_clock = []

    # append the data for each iteration (for each files line)
    for iteration in ALL_DATA:
        architecture = str((ALL_DATA[iteration][line][0]))
        application = str(ALL_DATA[iteration][line][1])

        N = (ALL_DATA[iteration][line][2])
        user_time.append(float(ALL_DATA[iteration][line][3]))
        system_time.append(float(ALL_DATA[iteration][line][4]))
        cpu_percent.append(float(ALL_DATA[iteration][line][5].replace("%", "")))
        memory.append(int(ALL_DATA[iteration][line][7]))

        minutes, seconds, milliseconds = ALL_DATA[iteration][line][6].split(".")
        wall_clock.append(timedelta(minutes = int(minutes), seconds = int(seconds), milliseconds = int(milliseconds)))

    # work out the average for that line
    averaged_architecture = architecture
    averaged_application = application
    averaged_N = N
    averaged_user_time = sum(user_time) / number_of_iterations
    averaged_system_time = sum(system_time) / number_of_iterations
    averaged_cpu_percent = sum(cpu_percent)/ number_of_iterations
    averaged_memory = sum(memory)/ number_of_iterations
    averaged_wall_clock = sum(wall_clock, timedelta()) / number_of_iterations

    # write that average to the file
    writer = csv.writer(open("averaged_time.csv", "a"))
    # check if file lines are empty (if it is then add the headings)
    filesize = os.path.getsize("averaged_time.csv")
    if (filesize == 0):
        writer.writerow(measurement_titles)

    averaged_data = [str(averaged_architecture), str(averaged_application), str(averaged_N), str(averaged_user_time), str(averaged_system_time), str(averaged_cpu_percent) + "%", str(averaged_wall_clock), str(averaged_memory)]
    writer.writerow(averaged_data)


    # calculate the variance values using the averaged data above
    summed_user_time = []
    for i in user_time:
        summed_user_time.append(pow((i - averaged_user_time), 2))
    user_time_variance = math.sqrt(sum(summed_user_time) / number_of_iterations)

    summed_system_time = []
    for i in system_time:
        summed_system_time.append(pow((i - averaged_system_time), 2))
    system_time_variance = math.sqrt(sum(summed_system_time) / number_of_iterations)

    summed_cpu_percent = []
    for i in cpu_percent:
        summed_cpu_percent.append(pow((i - averaged_cpu_percent), 2))
    cpu_percent_variance = math.sqrt(sum(summed_cpu_percent) / number_of_iterations)

    summed_memory = []
    for i in memory:
        summed_memory.append(pow((i - averaged_memory), 2))
    memory_variance = math.sqrt(sum(summed_memory) / number_of_iterations)

    # for the wallclock we need to calculate using the total_seconds function and then convert back
    summed_wall_clock = []
    for i in wall_clock:
        summed_wall_clock.append(pow((i.total_seconds() - averaged_wall_clock.total_seconds()), 2))
    temp = math.sqrt(sum(summed_wall_clock) / number_of_iterations)
    # print(wall_clock_variance)
    wall_clock_variance = datetime. timedelta(seconds=temp)
    # print(conversion)

    # write the standard deviation to the file
    writer = csv.writer(open("standard_deviation.csv", "a"))
    filesize = os.path.getsize("standard_deviation.csv")
    if (filesize == 0):
        writer.writerow(measurement_titles)
    writer.writerow([averaged_architecture, averaged_application, averaged_N, user_time_variance, system_time_variance, str(cpu_percent_variance) + "%",wall_clock_variance, memory_variance])
