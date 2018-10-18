# Docker setup

Run dependencies:
```
docker-compose up -d
```

Run εxodus container:
```
docker-compose -f docker-compose.run.yml up -d
```

Create database, user and import trackers:
```
docker exec -it <εxodus_container> /entrypoint.sh "create-db"
docker exec -it <εxodus_container> /entrypoint.sh "create-user"
docker exec -it <εxodus_container> /entrypoint.sh "import-trackers"
```

Run worker and frontend:
```
docker exec -it <εxodus_container> /entrypoint.sh "start-worker"
docker exec -it <εxodus_container> /entrypoint.sh "start-frontend"
```
