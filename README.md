# ETL pipeline
From postgres to elastic-search

# Setup
Run in a docker (Debug=False).

run commands
```
docker exec -it app python3 manage.py populatedb
docker exec -it app python3 manage.py fillcreationdate
docker exec -it app python3 manage.py runpipeline
```
