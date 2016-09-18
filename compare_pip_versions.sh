#!/bin/bash

# execute this on the commandline in the ./code directory
# it gets the current python library version numbers from
# pip and compares it with the last working ones.
# If they differ and everything still works, just update
# the last_working_pip_versions.txt file with the newer
# numbers.
#

docker exec -t topo_web_1 pip freeze > current_pip_versions.txt
diff last_working_pip_versions.txt current_pip_versions.txt
