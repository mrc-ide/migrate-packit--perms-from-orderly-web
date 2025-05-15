docker ps -aq | xargs -r docker stop
docker container prune --force
docker volume prune --force
docker network prune --force
