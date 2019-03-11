RUN_CMD=docker-compose run pimod pimod.sh

.PHONY: clean all
.DELETE_ON_ERROR:

all: Base.img Sensorbox.img
clean:
	rm -f Base.img Sensorbox.img
	rm `ls **/*.pyc`

Base.img: Base.Pifile Base
	${RUN_CMD} Base.Pifile

Sensorbox.img: Base.img Sensorbox.Pifile
	${RUN_CMD} Sensorbox.Pifile

