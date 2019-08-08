# Docker setup

## Run

```
docker-compose up -d
docker logs -f exodus
```

When everything is up (Docker logs `Exodus is ready.`), launch the worker:
```
docker exec -it exodus /entrypoint.sh "start-worker"
```

The exodus container automatically:
- Create the database
- Make migration
- Import trackers from the main instance
- Start the frontend of exodus

Don't forget to rebuild your container if there is any change with `docker-compose build`.

## Aliases

You can use the command
```
docker exec -it exodus /entrypoint.sh "<command>"
```
to make actions, where `<command>` can be:
- `create-db`: Create the database and apply migrations
- `create-user`: Create a Django user
- `import-trackers`: Import all trackers from the main exodus instance
- `start-frontend`: Start the web server
- `start-worker`: Start the exodus worker

