# custom command insertfields code can be found under
# topo/miroutes/management/commands/insertfields.py

#docker-compose run web python manage.py insertfields

# django-dbbackup is so buggy... until they resolve it we just use a custom backup with rsync and djangos dumpdata/loaddata...

#docker-compose run web ./manage.py dbrestore --noinput
#docker-compose run web ./manage.py mediarestore --noinput

#scp -P 2200 mitopo_backup@localhost:backup.0/mitopo_db.json .

rsync --partial --progress -a -v -e "ssh -p 2200" mitopo_backup@129.187.164.4:backup.0/ backup.0

docker-compose run web ./manage.py loaddata backup.0/mitopo_db.json
mv backup.0/www .
