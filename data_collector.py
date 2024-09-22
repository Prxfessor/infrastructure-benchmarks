'''
ASSUMPTIONS:
    - assume that collectd and influxdb, python and docker have been installed on the architecture and configured
    - assume that the docker images have been created and have been named "mm" and "pi" for its corresponding application
    - assume that the name of the database in influxdb is called metrics
    - assume that you are running in the directory where the python script is in
    - assume that you have installed influxdb python library and numpy
'''


# importing libraries
import os
import csv
import time
from datetime import datetime
from influxdb import InfluxDBClient


# FUNCTION TO WRITE THE DATA FROM THE INFLUXDB INTO A CSV FILE, THEN FORMAT THE DATE AND SAVE IT
def write_to_csv(filepath, headers, results):
    # writing to the corresponding file
    with open(filepath, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, headers)
        dict_writer.writeheader()
        dict_writer.writerows(results)
    output_file.close()
    # update the date/time of the CSV files being written
    date_format(filepath)



# FUNCTION TO UPDATE THE DATE FROM UNIX TIMESTAMP TO H:M:S.m GIVEN A FILE NAME
def date_format(filename):
    data_file = csv.reader(open(filename))
    data_list = list(data_file)

    # index that contains the "time" heading
    time_index = 0

    # finding the time heading
    # going through the first row (heading row) and find the index where it says "time"
    for index in range(0, len(data_list[0])):
        if(data_list[0][index] == "time"):
            time_index = index

    # for all the values (skipping the first row [range 1, not 0]) update the time value
    for i in range(1, len(data_list)):
        # print(str(i) + "  " + data_list[i][time_index])
        updated_time = int(data_list[i][time_index]) / 1e9
        data_list[i][time_index] = (datetime.fromtimestamp(updated_time).strftime('%H:%M:%S.%f'))
    
    # writing updated data to the same file
    writer = csv.writer(open(filename, "w"))
    writer.writerows(data_list)



# FUNCTION TO CREATE A COPY OF THE "RESULTS" DIRECTORY STORE IT AS AN ITERATION.
def copy_folder():
    # the iteration number
    i = 1

    # if the directory exists, then continue to find the last numbered iteration
    while(os.path.isdir("iterations/iteration_" + str(i))):
        i = i + 1
    # if the iteration directory does not exist
    if (not os.path.isdir("iteration_" + str(i))):
        # copy the current results into the iterations folder and number it accordingly.
        os.system("cp -r results iteration_" + str(i))
        os.system("mv iteration_" + str(i) + " iterations")
        print("Completed and stored Iteration " + str(i))



# FUNCTION TO GET DATA FROM THE TIMES COMMAND AND MAKE IT INTO CSV
# need to pass through the output file of the command, the architecture, application and the N amount tested on as strings
def time_command_csv(filename, architecture, application, N):
    # defined the measurements we want to collect and other variables in the CSV file we are going to make
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

    # values of the measurements stored here
    measurement_values= []
    # append the name of the architecture
    measurement_values.append(architecture)
    # append the name of the application
    measurement_values.append(application)
    # append the N value
    measurement_values.append(str(N))

    # open the file and to get the specified measurements
    output_file = open(filename)

    # for everything in the output file
    for line in output_file:
        # for all the measurements in the measurements titles
        for measurement in measurement_titles:
            # if the measurement is in the output line
            if (measurement in line):
                # if the measurement is clock time (will have to manually change the : to . because we cannot split by ":" otherwise)
                if ("Elapsed (wall clock)" in line):
                    line = line.replace(":", ".")
                    temp_list = list(line)
                    # add in a colon at index 44
                    temp_list[44] = ":"
                    temp_list = ''.join(temp_list)
                    line = temp_list

                # get rid of all the tab spaces and new lines
                line = line.replace("\t", "")
                line = line.replace("\n", "")

                # split the data by the ":" and add the value into the measurement values
                name, value = line.split(":")
                measurement_values.append(value)

    # get rid of all extra spaces in the values
    for i in range(0, len(measurement_values)):
        measurement_values[i] = measurement_values[i].strip()

    # close the file we are reading from
    output_file.close()

    # Write the data to the csv file
    # if the times.csv exists, we just append the values to the end of it
    if (os.path.isfile("results/times.csv")):
        with open("results/times.csv",'a') as f:
            wr = csv.writer(f)
            wr.writerow(measurement_values)
    # if the times.csv does not exist, we add in the measurement headings and the corresponding values
    else:
        with open("results/times.csv",'a') as f:
            wr = csv.writer(f)
            wr.writerow(measurement_titles)
            wr.writerow(measurement_values)





########## SETUP ##########
# start the influx db service
print(" - - - SETTING UP - - -")
os.system("systemctl start influxdb")
print("Started influxdb")
time.sleep(5)

# connecting to the influxdb at localhost and on port 8086 (default port)
client = InfluxDBClient(host='localhost', port=8086)
print("Connected to influxdb client")

# clearing the database before using it.
client.drop_database("metrics")
client.create_database("metrics")
client.switch_database('metrics')
print("Cleared influxdb database")

# # define the N for each application arguments
PI_N = [5000, 10000, 15000, 20000 ,25000]
MM_N = [500, 1000, 1500, 2000,2500]

# PI_N = [500, 600]
# MM_N = [200, 500]


# create the file name for the time application output
time_filename = "results/temp.txt"
print("- - - SET UP COMPLETE - - -\n")




########## BARE METAL ##########
print(" - - - BARE METAL - - -")
# PI PROGRAM
for n in range(0, len(PI_N)):
    # get the for the CPU and memory result file names
    cpu_path_to_csv_file = "results/bare_metal/pi_results/pi_cpu_" + str(PI_N[n]) + ".csv"
    memory_path_to_csv_file = "results/bare_metal/pi_results/pi_memory_" + str(PI_N[n]) + ".csv"
    
    # start collectd and sleep to allow for service to start
    os.system("systemctl start collectd")
    time.sleep(6)

    # run the command for the PI program and save the output to the results/temp.txt
    os.system("(/usr/bin/time -v python3 architectures/bare_metal/pi.py " + str(PI_N[n]) +  ") 2> " + time_filename)

    # clean up the data from the temp.txt and append it to times.csv
    time_command_csv(time_filename, "bare_metal", "pi", PI_N[n])
    # sleep for 6s, dependent on the batch-timeout in the influxdb config file (5ms)
    time.sleep(6)
    os.system("systemctl stop collectd")

    # query to collect the csv from influxdb (get all the points from that query as a list)
    cpu_results = list(client.query('SELECT * from cpu_value', epoch = "ns" ).get_points())
    memory_results = list(client.query('SELECT * from memory_value', epoch = "ns" ).get_points())


    # WRITE CPU DATA
    headers = cpu_results[0].keys()
    write_to_csv(cpu_path_to_csv_file, headers, cpu_results)

    # WRITE MEMORY DATA
    headers = memory_results[0].keys()
    write_to_csv(memory_path_to_csv_file, headers, memory_results)
    
    # clear the database for new measurements
    client.drop_database("metrics")
    client.create_database("metrics")
    client.switch_database('metrics')


# MM PROGRAM
for n in range(0, len(MM_N)):
    # get the for the CPU and memory result file names
    cpu_path_to_csv_file = "results/bare_metal/mm_results/mm_cpu_" + str(MM_N[n]) + ".csv"
    memory_path_to_csv_file = "results/bare_metal/mm_results/mm_memory_" + str(MM_N[n]) + ".csv"

    # start collectd and sleep to allow for service to start
    os.system("systemctl start collectd")
    time.sleep(6)

    # run the command for the MM program and save the output to the results/temp.txt
    os.system("(/usr/bin/time -v python3 architectures/bare_metal/mm.py " + str(MM_N[n]) +  ") 2> " + time_filename)

    # clean up the data from the temp.txt and append it to times.csv
    time_command_csv(time_filename, "bare_metal", "mm", MM_N[n])
    # sleep for 6s, dependent on the batch-timeout in the influxdb config file (5ms)
    time.sleep(6)
    os.system("systemctl stop collectd")

    # query to collect the csv from influxdb (get all the points from that query as a list)
    cpu_results = list(client.query('SELECT * from cpu_value', epoch = "ns" ).get_points())
    memory_results = list(client.query('SELECT * from memory_value', epoch = "ns" ).get_points())

    # WRITE CPU DATA
    headers = cpu_results[0].keys()
    write_to_csv(cpu_path_to_csv_file, headers, cpu_results)
    
    # WRITE MEMORY DATA
    headers = memory_results[0].keys()
    write_to_csv(memory_path_to_csv_file, headers, memory_results)

    # clear the database for new measurements
    client.drop_database("metrics")
    client.create_database("metrics")
    client.switch_database('metrics')
    



# ########## DOCKER ##########
print(" - - - DOCKER - - -")
# PI PROGRAM
for n in range(0, len(PI_N)):
    # get the for the CPU and memory result file names
    cpu_path_to_csv_file = "results/docker/pi_results/pi_cpu_" + str(PI_N[n]) + ".csv"
    memory_path_to_csv_file = "results/docker/pi_results/pi_memory_" + str(PI_N[n]) + ".csv"

    # start collectd and sleep to allow for service to start
    os.system("systemctl start collectd")
    time.sleep(6)

    # run the command for the PI program and save the output to the results/temp.txt
    os.system("docker run -e N="+ str(PI_N[n]) +" pi 2> " + time_filename)

    # clean up the data from the temp.txt and append it to times.csv
    time_command_csv(time_filename, "docker", "pi", PI_N[n])
    # dependent on the batch-timeput in the influxdb config file (5ms)
    time.sleep(6)
    os.system("systemctl stop collectd")

    # query to collect the csv from influxdb (get all the points from that query as a list)
    cpu_results = list(client.query('SELECT * from cpu_value', epoch = "ns" ).get_points())
    memory_results = list(client.query('SELECT * from memory_value', epoch = "ns" ).get_points())

    # WRITE CPU DATA
    headers = cpu_results[0].keys()
    write_to_csv(cpu_path_to_csv_file, headers, cpu_results)

    # WRITE MEMORY DATA
    headers = memory_results[0].keys()
    write_to_csv(memory_path_to_csv_file, headers, memory_results)

    # clear the database for new measurements
    client.drop_database("metrics")
    client.create_database("metrics")
    client.switch_database('metrics')


# MM PROGRAM
for n in range(0, len(MM_N)):
    # get the for the CPU and memory result file names
    cpu_path_to_csv_file = "results/docker/mm_results/mm_cpu_" + str(MM_N[n]) + ".csv"
    memory_path_to_csv_file = "results/docker/mm_results/mm_memory_" + str(MM_N[n]) + ".csv"

    # start collectd and run the program and then stop collectd
    os.system("systemctl start collectd")
    time.sleep(6)

    # run the command for the MM program and save the output to the results/temp.txt
    os.system("docker run -e N="+ str(MM_N[n]) +" mm 2> " + time_filename)

    # clean up the data from the temp.txt and append it to times.csv
    time_command_csv(time_filename, "docker", "mm", MM_N[n])
    # dependent on the batch-timeput in the influxdb config file (5ms)
    time.sleep(6)
    os.system("systemctl stop collectd")

    #    # query to collect the csv from influxdb (get all the points from that query as a list)
    cpu_results = list(client.query('SELECT * from cpu_value', epoch = "ns" ).get_points())
    memory_results = list(client.query('SELECT * from memory_value', epoch = "ns" ).get_points())

    # WRITE CPU DATA
    headers = cpu_results[0].keys()
    write_to_csv(cpu_path_to_csv_file, headers, cpu_results)

    # WRITE MEMORY DATA
    headers = memory_results[0].keys()
    write_to_csv(memory_path_to_csv_file, headers, memory_results)

    # clear the database for new measurements
    client.drop_database("metrics")
    client.create_database("metrics")
    client.switch_database('metrics')




########## FINISHING UP ##########
# stop all services running
print("\n - - - FINISHING UP - - -")
os.system("systemctl stop influxdb")
os.system("systemctl stop collectd")
print("Stopped influxdb and collectd")
copy_folder()
os.system("rm results/times.csv results/temp.txt")
print("Cleared the CSV files")
print("- - - END OF PROGRAM - - -")






