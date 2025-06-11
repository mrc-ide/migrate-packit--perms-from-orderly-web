docker ps -aq | xargs -r docker stop
docker container prune --force
docker volume prune --all --force
docker network prune --force
