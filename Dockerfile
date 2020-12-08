FROM python:3.7.9

RUN mkdir -p /init
RUN mkdir -p /logs
RUN mkdir -p /platform_manager
RUN mkdir -p /simulation-tools

# install the python libraries
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# copy the source code files to the container
COPY supported_components*.json /
COPY init/ /init/
COPY platform_manager/ /platform_manager/
COPY simulation-tools/ /simulation-tools/

WORKDIR /

CMD [ "python", "-u", "-m", "platform_manager.platform_manager" ]
