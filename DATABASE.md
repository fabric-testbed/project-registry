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
source .env
source venv/bin/activate
pip install -r requirements.txt
python -m flask db init            # creates migrations directory
python -m flask db migrate         # generates migrations file
python -m flask db upgrade         # applies migrations to database
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

## Conveniece calls

**NOTE**: MAX values will vary for `alter sequence` calls

### `pg_restore` calls

```
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t comanage_cous /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t fabric_people /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t fabric_projects /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t fabric_roles /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t project_members /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t project_owners /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t tags /tmp/backup.sql'
docker exec -u postgres pr-database sh -c 'pg_restore -U postgres --data-only -d postgres -t version /tmp/backup.sql'
```

### `select max` calls

```
docker exec -u postgres pr-database psql -c "select max(id) from comanage_cous;"
docker exec -u postgres pr-database psql -c "select max(id) from fabric_people;"
docker exec -u postgres pr-database psql -c "select max(id) from fabric_projects;"
docker exec -u postgres pr-database psql -c "select max(id) from fabric_roles;"
docker exec -u postgres pr-database psql -c "select max(id) from project_members;"
docker exec -u postgres pr-database psql -c "select max(id) from project_owners;"
docker exec -u postgres pr-database psql -c "select max(id) from tags;"
docker exec -u postgres pr-database psql -c "select max(id) from version;"
```


### `alter sequence` calls

```
docker exec -u postgres pr-database psql -c "alter sequence comanage_cous_id_seq restart with 82;"
docker exec -u postgres pr-database psql -c "alter sequence fabric_people_id_seq restart with 58;"
docker exec -u postgres pr-database psql -c "alter sequence fabric_projects_id_seq restart with 26;"
docker exec -u postgres pr-database psql -c "alter sequence fabric_roles_id_seq restart with 434;"
docker exec -u postgres pr-database psql -c "alter sequence project_members_id_seq restart with 87;"
docker exec -u postgres pr-database psql -c "alter sequence project_owners_id_seq restart with 34;"
docker exec -u postgres pr-database psql -c "alter sequence tags_id_seq restart with 1;"
docker exec -u postgres pr-database psql -c "alter sequence version_id_seq restart with 2;"
```
