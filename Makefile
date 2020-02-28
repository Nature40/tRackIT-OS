PIMOD=docker-compose run pimod pimod.sh


all: Sensorbox.img RadioTracking.img

clean:
	rm -f Base.img Mesh.img Sensorbox.img RadioTracking.img

Base.img: 			Base.Pifile 		Base
	${PIMOD} Base.Pifile

Mesh.img: 			Mesh.Pifile 		Mesh 			Base.img
	${PIMOD} Mesh.Pifile

Sensorbox.img: 		Sensorbox.Pifile 	Sensorbox 		Mesh.img	pysensorproxy
	${PIMOD} Sensorbox.Pifile

RadioTracking.img: RadioTracking.Pifile	RadioTracking 	Sensorbox.img
	${PIMOD} RadioTracking.Pifile