# custom command insertfields code can be found under
# topo/miroutes/management/commands/insertfields.py

#docker-compose run web python manage.py insertfields
docker-compose run web ./manage.py dbrestore --noinput
docker-compose run web ./manage.py mediarestore --noinput
