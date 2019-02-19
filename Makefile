RUN_CMD=docker-compose run pimod pimod.sh

all: Base.img LiftCar.img
clean:
	rm Base.img LiftCar.img LiftCar-Students.img

Base.img: Base.Pifile Base
	${RUN_CMD} Base.Pifile

LiftCar.img: Base.img LiftCar.Pifile LiftCar
	${RUN_CMD} LiftCar.Pifile

LiftCar-Students.img: LiftCar.img LiftCar-Students.Pifile Sensorbox
	${RUN_CMD} LiftCar-Students.Pifile

