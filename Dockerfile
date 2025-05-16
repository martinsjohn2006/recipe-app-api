# this tells docker what version of python to use in our build
#  this also tells docker what version of the linux operating system to use
#the name or website of the person intending to manage this project
FROM python:3.9-alpine3.13
LABEL maintainer = "Martins John" 

#this tells the docker to npt allow any delay in output
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

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

#this block helps us define our path to our user defined variables, executables
ENV PATH="/py/bin:$PATH"

#this tells the docker container the user to switch to. all of the commands 
#ran prior to this are actually run using the root user privilege.
USER django-user 