# ETL pipeline
From postgres to elastic-search

Для имитации проблемы запускал бд локально
```angular2html
docker run -d --rm \
--name postgres \
-p 5432:5432 \
-v $HOME/postgresql/data:/var/lib/postgresql/data \
-e POSTGRES_PASSWORD=pass \
-e POSTGRES_USER=app \
-e POSTGRES_DB=movies_database \
postgres:13
```
затем
```
docker exec -it app python3 manage.py populatedb
docker exec -it app python3 manage.py fillcreationdate
docker exec -it app python3 manage.py runpipeline
```
