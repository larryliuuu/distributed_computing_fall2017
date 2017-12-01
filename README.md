# Distributed Shared Memory System
UIUC Distributed Computing Research Group - Fall 2017

## Getting Started
### psql
1. Install PostgreSQL: 
* https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
* Brew Install PostgreSQL: `brew update && install postgresql`
2. Login psql: `psql`
3. Create DB `dc`: `create database dc`
4. Quit psql: `\d`
5. Login DB `dc`: `psql -d dc`
6. Create table `keys`: `CREATE TABLE keys (key VARCHAR(255), value VARCHAR(255), modified_by VARCHAR(255), time_modified TIMESTAMP WITHOUT TIME ZONE, temp1 VARCHAR(255), temp2 VARCHAR(255), temp3 VARCHAR(255), pkey BIGSERIAL PRIMARY KEY);`
7. Force unique keys: `ALTER TABLE keys ADD CONSTRAINT uq_key UNIQUE(key);`
8. Create role `db_user`: `CREATE ROLE db_user WITH PASSWORD 'db_pw';`
9. Add role login priviliges: `ALTER ROLE db_user WITH LOGIN;`

### python packages
* requests
* netifaces
* psycopg2