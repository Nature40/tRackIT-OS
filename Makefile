PIMOD=docker-compose run pimod pimod.sh
DSSTORE_CLEAN=find . -name ".DS_Store" -type f -delete


all: Sensorbox.img RadioTracking.img

clean:
	@${DSSTORE_CLEAN}
	rm -f *.img

Base.img: 			Base.Pifile 		Base
	@${DSSTORE_CLEAN}
	${PIMOD} Base.Pifile

Sensorbox.img: 		Sensorbox.Pifile 	Sensorbox 		Base.img
	@${DSSTORE_CLEAN}
	${PIMOD} Sensorbox.Pifile

RadioTracking.img: RadioTracking.Pifile	RadioTracking 	Sensorbox.img
	@${DSSTORE_CLEAN}
	${PIMOD} RadioTracking.Pifile