# FOR MM
FROM python:3.8
# N is the argument variable being passed
ENV N=100
# COPY the mm.py script in
COPY mm.py /
# update the image
RUN apt-get update
# install numpy needed for the application
RUN pip3 install numpy
# install the time command
RUN apt-get install time
# run this command below with the environment varibale at the end
# can be run by: "docker run -e N=300 mm"
CMD /usr/bin/time -v python3 mm.py $N

