FROM python:3.8-buster
ARG KEDRO_UID=501
ARG KEDRO_GID=20

# install project requirements
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

# add kedro user
RUN groupadd -f -g ${KEDRO_GID} kedro_group && \
            useradd -d /home/kedro -s /bin/bash -g ${KEDRO_GID} -u ${KEDRO_UID} kedro

# copy the whole project except what is in .dockerignore
WORKDIR /home/kedro
COPY . .
RUN chown -R kedro:${KEDRO_GID} /home/kedro
USER kedro
RUN chmod -R a+w /home/kedro
# ENV HTTP_PROXY=http://192.168.1.29:8000
# for local test : ifconfig | grep 'inet 192'| awk '{ print $2}' give the adress of my mac = 192.168.1.29
# for macOS : docker.for.mac.host.internal
EXPOSE 5000

CMD ["python", "flask_entry.py"]
