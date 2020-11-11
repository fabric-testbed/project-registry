FROM python:3
MAINTAINER Michael J. Stealey <michael.j.stealey@gmail.com>

# Set default environment variables

# copy source files
COPY ./server /server
COPY ./dbmgmt /dbmgmt
COPY ./docker-entrypoint.sh /server/docker-entrypoint.sh
WORKDIR /server

# set entrypoint and exposed ports
ENTRYPOINT ["/server/docker-entrypoint.sh"]
EXPOSE 5000
CMD ["run_server"]
