FROM python:3
MAINTAINER Michael J. Stealey <michael.j.stealey@gmail.com>

# make code directory
RUN mkdir /code

# copy source files
COPY ./server /code/server
COPY ./migrations /code/migrations
COPY ./.env /code/.env
COPY ./requirements.txt /code/requirements.txt
COPY ./docker-entrypoint.sh /code/docker-entrypoint.sh
WORKDIR /code

# set entrypoint and exposed ports
ENTRYPOINT ["/code/docker-entrypoint.sh"]
EXPOSE 6000
CMD ["run_server"]

