## Table of Contents
- [Technical Guide](#technical-guide)
  - [Description:](#description)
  - [General Information:](#general-information)
  - [Installations:](#installations)
  - [Setup:](#setup)
    - [School Test Bed:](#school-test-bed)
      - [Virtual Machine](#virtual-machine)
        - [SSH Access, Zabbix and Grafana](#ssh-access-zabbix-and-grafana)
        - [InfluxDB, CollectD, and Grafana Services](#influxdb-collectd-and-grafana-services)
          - [InfluxDB Specific Information](#influxdb-specific-information)
        - [Configuration Files](#configuration-files)
      - [Docker](#docker)
    - [AWS Setup](#aws-setup)
  - [Metrics collected:](#metrics-collected)
    - [VM and Docker:](#vm-and-docker)
    - [AWS CloudWatch:](#aws-cloudwatch)
  - [Directory Structure](#directory-structure)
  - [How to Run](#how-to-run)
  - [Known Issues:](#known-issues)

# Technical Guide
## Description:
This project was developed to evaluate the performance between VMs (School Test Bed), Containers (Docker) and Serverless Architectures (AWS Lambda) with cold and warm start.

## General Information:
* **NOTE: Bare metal and VM are used interchangeably throughout the repository and the README However when referring to this we mean Virtual Machine**
  * The reason for this was due to multiple changes in the project specification compared to when first starting the project.
* **NOTE: The experiment was run 5 times in this case to gather the metrics and calculate further statistics on them**
* **Language Used**: Python 3.8
* **Applications Developed**:
  * **Data Intensive:** Matrix Multiplication
     * Developed using NumPy
     * Tested for N = 500, 1000, 1500, 2000, 2500
       * Was chosen as larger values would lead to computation times that are way too large
  * **Computationally Intensive:** Bailey-Borwein-Plouffe (Pi calculation)
     * Source: https://github.com/BrolanJ/Bailey-Borwein-Plouffe
     * Tested for N = 500, 1000, 5000, 10000, 15000
       * Was chosen as larger values would lead to computation times that are way too large
 * **Metrics Compared**:
    * Duration: How long it took to run in seconds
    * CPU Utilization: Percentage of CPU used
    * Memory Utilization: Memory used in kb




## Installations:
1. Install the following Python libraries: `pip`, `numpy`, and `influxdb client`
2. Install `Docker`




## Setup:
### School Test Bed:
* Is a type 1 hypervisor server that allows for VM's to be run on there. It is made up of 14 nodes and the specifcation is as follows:
  * 12 Compute PowerEdge 3430 Server
  * 1 Data R730xd server
  * 2 Gateway R730xd servers
* Accessing services:
  * OpenNebula: `https://localhost:8444`
  * Zabbix: `https://localhost:8444/zabbix/index.php` -  Will not use as you cannot configure Zabbix to monitor a single VM instance on a node


#### Virtual Machine
NOTE: Further information on this is stored in a standalone document (not available in this repository)
1. Create a persistent VM on the OpenNebula portal
   * OpenNebula is the VIM (Virtual Infrastructure Manager)
   * The image used was Debian Stretch as it came pre-installed with Docker, and it had the most amount of allocated memory to it
   * Specification of the VM:
     * CPU: Intel 4 Core Virtual CPU (2.4Ghz)
     * Memory: 8GB
     *
2. Access the VM via SSH


##### SSH Access, Zabbix and Grafana
1. SSH into the created VM


##### InfluxDB, CollectD, and Grafana Services
* Installation guide: https://serhack.me/articles/monitoring-infrastructure-grafana-influxdb-connectd/
  * Was installed on the VM
* Service management:
  ``` bash
  systemctl <start/stop/status> influxdb
  systemctl <start/stop/status> collectd
  systemctl <start/stop/status> grafana-server
  ```
* Alternative commands to the above
  ``` bash
  service influxdb start/stop/status
  service collectd start/stop/status
  ```
* To check the running services: `sudo netstat --tunlp`


###### InfluxDB Specific Information
* No user is required for the database
* Database operations:
  * For viewing the data
  ``` SQL
  show databases
  use <name_of_database>
  show measurements
  select * from <table_name>
  ```
  * For exporting the data from InfluxDB into CSV file (Will need to run in BASH)
  ``` bash
  #export data to CSV file
  influx -database '<DATABASE_NAME>' -execute 'select * from <TABLE_NAME>' -format 'csv' > test.csv
  ```


##### Configuration Files
* Copy the configuration files from this repository into the locations on the VM as seen below:
  * influxdb.config: `/etc/influxdb/influxdb.conf`
  * collectd.config: `/etc/collectd/collectd.conf`



#### Docker
* Create a `Dockerfile` next to the application
* Basic Docker commands:
  ``` bash
  docker build -t <name> .
  docker images
  docker rmi <image_name> -f
  docker run -e N=<N> <name_of_image>
  ```
* To allow the time command to work **on** docker and not **in**. We need to add `/usr/bin/time -v`, to the Dockerfiles:
  ``` docker
  RUN apt-get update
  RUN apt-get install time
  ```
* Output to file: `docker run ... 2> <file_name>`




### AWS Setup
* Timeout: 5 minutes
* Memory: 1024MB - This was increased for another instance to 8192mb (8GB), where we further explored the Memory increase correlation to the cold start.
* Matrix Multiplication required a **numpy** layer:
  1. Click `add a layer`
  2. Choose `AWS layers`
  3. Select `AWSLambda-Python38-SciPy1x`
  4. Choose version `29`
  5. Add environment variables in `configurations` ⇒ `environment variables`




## Metrics collected:
### VM and Docker:
* Collectd, InfluxDB, and Grafana was used as supporting evidence to the `time` command. This was due to a security issue on the School test bed that did not allow Grafana to be configured correctly
* `Time` command
  * Measurements collected:
    * User time (seconds)
    * System time (seconds)
    * Percent of CPU this job got
    * Elapsed (wall clock) time
    * Maximum resident set size (kbytes)

### AWS CloudWatch:
* NOTE: CPU utilization was not available to use. We could only compare what metrics we have collected
* Init duration (ms)
* Max Memory Used (MB)
* Duration (ms)
* Resources configured (MB)




## Directory Structure
| Directory / File               | Purpose                                                                                                                                                                                                    |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `architectures/`               | Contains the code for the different architectures                                                                                                                                                          |
| `architectures/aws/`           | Contains the code for the AWS architecture                                                                                                                                                                 |
| `architectures/bare_metal/`    | Contains the code for the bare metal architecture                                                                                                                                                          |
| `architectures/docker/`        | Contains the code for the Docker architecture                                                                                                                                                              |
| `configurations/influxdb.conf` | Contains the configurations for the InfluxDB                                                                                                                                                               |
| `configurations/collectd.conf` | Contains the configurations for collectd                                                                                                                                                                   |
| `iterations/`                  | Contains the output created by `data_collector.py` of the metrics of each iteration for the Docker and bare metal, it contains both the metrics from InfluxDB and `times` library                          |
| `results/`                     | Contains the meaningful results from the `iterations/` for each application on Docker and on bare metal                                                                                                    |
| `results/bare_metal/`          | Contains the meaningful results from the `iterations/` for each application on bare metal                                                                                                                  |
| `results/docker/`              | Contains the meaningful results from the `iterations/` for each application on Docker                                                                                                                      |
| `ALL_RESULTS.zip`              | Contains the results from the `results/` directory, the `averaged_time.csv`, the `standard_deviation.csv`, and additional the manually added data from AWS metrics                                         |
| `averaged_time.csv`            | Contains the average metrics of the Docker and bare metal over the iterations                                                                                                                              |
| `standard_deviation.csv`       | Contains the standard deviation of the metrics of the Docker and bare metal over the iterations                                                                                                            |
| `data_collector.py`            | Contains the script to collect data from the `times` command and InfluxDB from the Docker and bare metal architecture - it stores the collected data in `iterations`                                       |
| `data_aggregator.py`           | Contains the script to run that takes the data from the `iterations` directory and calculates the average and the standard deviation - will output the `standard deviation.csv` and the `average_time.csv` |




## How to Run
1. Run `data_collector.py` N times to collect the data for the Docker and Cloud Testbed
2. Run `data_aggregator.py` to get averages and standard deviations of the data collected
3. For the AWS data. For the mean time will need to run the code manually and collect the data manually.
4. Use influxDB data to verify and validate collected data




## Known Issues:
* **Issue**: There was an security issue on the Cloud Test Bed that meant we could not run the Grafana service as intended. There was no fix for this.
    * **Solution**:
        * We used the metrics collected from InfluxDB and collectd to support the metrics collected by the `time` command.


* **Issue**: When installing InfluxDB the `types.db` might be missing at the path `/usr/share/collectd/`
     * **Solution**:
       * Download `types.db` for InfluxDB if it is missing in the `collectd` directory:
       ``` bash
       cd /usr/share/collectd/
       wget https://raw.githubusercontent.com/collectd/collectd/master/src/types.db
       ```

* **Issue**: There was an issue with the CPU utilisation in the MM script where the percentage went above 100%:
     * **Reason**: Numpy is multithreaded by default an uses multiple cores
       * Can be seen by checking the numpy configurations: `numpy.__config__.show()`
     * **Solution:**: Configure numpy to use 1 thread
       * Set environment variables:
         * OpenBLAS: `export OPENBLAS_NUM_THREADS=1`
         * MKL: `export MKL_NUM_THREADS=1`
