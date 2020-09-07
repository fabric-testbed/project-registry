FROM python:3
MAINTAINER Michael J. Stealey <michael.j.stealey@gmail.com>

# Set default environment variables

# copy source files
COPY ./server /code
COPY ./docker-entrypoint.sh /code
WORKDIR /code

# set entrypoint and exposed ports
ENTRYPOINT ["/code/docker-entrypoint.sh"]
EXPOSE 5000
CMD ["run_server"]
