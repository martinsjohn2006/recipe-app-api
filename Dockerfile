# this tells docker what version of python to use in our build
#  this also tells docker what version of the linux operating system to use
#the name or website of the person intending to manage this project
FROM python:3.9-alpine3.13
LABEL maintainer="Martins John" 

#this tells the docker to not allow any delay in output
ENV PYTHONUNBUFFERED=1


#this copies the requirement text and some other files into our container
#also it choses the port to expose
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

#run some commands to create somethings and install some dependencies
#as soon as they are done installing, we remove them as we would love to keep our image as light as possible
#look at the "adduser" part, this creates a user in the linux system as we do not wish to 
#use the root user by default "django-user" is the name of the created user.
# it is also important to note that we just recently added a new command to the run block 
# this command installs all the needed dependencies for us to install psycopg2 and after we are done, we delete
# them, you can identify this line below as it starts with the alpine package manager "apk", now, one cool feature 
# with the installation is the there is a --virtual argument that helps us give a group name to a group of packages
# we wish to install and as soon as we are done we can make a delete of this packages using the group installation name.


ARG DEV=false

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; \ 
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \ 
     --disabled-password\
     --no-create-home\
      django-user &&\
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \   
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol
#this block helps us define our path to our user defined variables, executables
ENV PATH="/py/bin:$PATH"

#this tells the docker container the user to switch to. all of the commands 
#ran prior to this are actually run using the root user privilege.
USER django-user 