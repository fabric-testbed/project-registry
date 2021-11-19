# Migrating to new database

Since PR is already running with active users the database must be migrated from a backup prior to starting the new service.

```
$ docker exec -u postgres pr-database psql -c "\dt;"
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | comanage_cous   | table | postgres
 public | fabric_people   | table | postgres
 public | fabric_projects | table | postgres
 public | fabric_roles    | table | postgres
 public | project_members | table | postgres
 public | project_owners  | table | postgres
 public | tags            | table | postgres
 public | version         | table | postgres
(9 rows)
```

### Backup database

From the host

```
docker exec -u postgres pr-database sh -c 'pg_dump -Fc postgres > /tmp/backup.sql'
docker cp pr-database:/tmp/backup.sql ./backup.sql
```

Then copy the database to the new host

### Restore database

Assumptions:

-  `venv` is virtual python directory
-  `.env` file is properly configured

Create new tables

```
source venv/bin/activate
source .env
python -m flask init        # creates migrations directory
python -m flask migrate     # generates migrations file
python -m flask upgrade     # applies migrations to database
```

Restore data from backup

```
docker cp ./backup.sql pr-database:/tmp/backup.sql
# for each <table_name> run
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t <table_name> /tmp/backup.sql'
```

Update the primary key sequence

```
# for each <table_name> get the MAX primary key value
docker exec -u postgres pr-database psql -c "select max(id) from <table_name>;"
# alter sequence value to restart with MAX+1
docker exec -u postgres pr-database psql -c "alter sequence <table_name>_id_seq restart with MAX+1;"
```

Load data from script

```
python -m server.swagger_server.db_load
```
