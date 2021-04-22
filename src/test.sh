 #!/bin/bash

coverage run -m pytest && coverage report --rcfile=.coveragerc
