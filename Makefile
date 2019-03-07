RUN_CMD=docker-compose run pimod pimod.sh

.PHONY: clean all
.DELETE_ON_ERROR:

all: Base.img LiftCar.img
clean:
	rm -f Base.img LiftCar.img LiftCar-Students.img
	rm `ls **/*.pyc`

Base.img: Base.Pifile Base
	${RUN_CMD} Base.Pifile

LiftCar.img: Base.img LiftCar.Pifile LiftCar
	${RUN_CMD} LiftCar.Pifile

LiftCar-Students.img: LiftCar.img LiftCar-Students.Pifile Sensorbox
	${RUN_CMD} LiftCar-Students.Pifile

Sensorbox.img: Base.img Sensorbox.Pifile
	${RUN_CMD} Sensorbox.Pifile

