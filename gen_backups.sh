#!/usr/bin/env bash

echo "This script runs on backup server -- this is here in the repo to keep everythin in one place..."
exit

cd /home/mitopo_backup/

rm -rf backup.14

for i in {13..0}
do 
  mv backup.$i backup.$(($i+1))
done

rsync --partial --progress -a --delete --link-dest=../backup.1 -e "ssh -p 2200" gucki@129.187.164.4:topo/www backup.0

ssh -p 2200 gucki@129.187.164.4 "cd topo; docker-compose run web ./manage.py dumpdata" > backup.0/mitopo_db.json
ssh -p 2200 gucki@129.187.164.4 "cd topo; docker-compose run web pg_dump -h postgresql -U postgres --clean" > backup.0/mitopo_db.pgdump

