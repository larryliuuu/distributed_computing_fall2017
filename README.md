# Distributed Shared Memory System
UIUC Distributed Computing Research Group - Fall 2017

## Getting Started
### psql
1. Install PostgreSQL: 
* https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
* Brew Install PostgreSQL: `brew update && brew install postgresql`
2. Login psql: `psql`
3. Create DB `dc`: `create database dc`
4. Quit psql: `\q`
5. Login DB `dc`: `psql -d dc`
6. Create table `keys`: `CREATE TABLE keys (key VARCHAR(255), value VARCHAR(255), modified_by VARCHAR(255), time_modified TIMESTAMP WITHOUT TIME ZONE, version VARCHAR(255), temp2 VARCHAR(255), temp3 VARCHAR(255), pkey_id BIGSERIAL PRIMARY KEY);`
7. Force unique keys: `ALTER TABLE keys ADD CONSTRAINT uq_key UNIQUE(key, version);`
8. Create role `db_user`: `CREATE ROLE db_user WITH PASSWORD 'db_pw';`
9. Add role login priviliges: `ALTER ROLE db_user WITH LOGIN;`
10. Add rest of privileges to role: `alter user db_user with superuser;`

### python packages
* requests
* netifaces
* psycopg2
* pathlib


## Completed Tasks
1. Postgres database READ/WRITE/DELETE API
2. Message passing with causal consistency
3. Averaging Algorithm in Cassandra
4. Execution of an algorithm from template/config utilizing neighboring nodes
5. Execution of an algorithm from template on an ad-hoc network of raspberry pi nodes
