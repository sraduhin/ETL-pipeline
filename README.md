# ETL pipeline
Writing ETL with
* django
* postgres
* docker
* nginx
* elasticsearch
* swagger

... and still writing

# Setup
Run in a docker.

run commands
```
docker exec -it app python3 manage.py populatedb
docker exec -it app python3 manage.py fillcreationdate
docker exec -it app python3 manage.py runpipeline
```
