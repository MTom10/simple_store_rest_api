#  what python
FROM python:3.12
#  what port (no need in gunivorn)
# EXPOSE 5000
# what work directory, will move into /app folder
WORKDIR /app
# copy requires to docker current folder /app , before COPY . . , if requires not changed will be cached,
COPY requirements.txt .
# dont use a cash folder
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# will copy files from our file system ( . ) -entire folder
# of the project to image's file system /app
# . . because we're already in /app folder
copy . .

# what commands to run when the image starts up in the container
# CMD ["flask", "run", "--host", "0.0.0.0"]

CMD ["/bin/bash", "docker-entrypoint.sh"]