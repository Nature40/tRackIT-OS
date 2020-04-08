#!/usr/bin/env bash

set -euf -o pipefail

DEVICE=${1}

# default config
FREQUENCY=150100001
SAMPLERATE=250000
GAIN=49
THRESHOLD=11
FFT_BINS=400
FFT_SAMPLES=50
DURATION_MIN=0
DURATION_MAX=1
KEEPALIVE=300
POS_X=0.0
POS_Y=0.0
ORIENTATION_OFFSET=0

# additional configuration
CONFIGFILE="/boot/rtlsdr_signal_detect.conf"
echo "# Loading config file ${CONFIGFILE}..."
source "${CONFIGFILE}"

# test if device is available
echo "# Testing hardware availability..."
rtl_sdr -d ${DEVICE} -f ${FREQUENCY} -s ${SAMPLERATE} -g ${GAIN} -n1 /dev/null

# generate output paths
BASEFILE="/data/`hostname`/rtlsdr_signal_detect/`date +"%Y-%m-%dT%H%M%S"`"
METAFILE="${BASEFILE}.conf"
OUTFILE="${BASEFILE}_${DEVICE}.csv"

# create output folder
echo "# Creating output folder ${BASEFILE}..."
mkdir -p `dirname ${BASEFILE}`

# save configuration
echo "# Dumping configuration ${METAFILE}..."
tee ${METAFILE} <<EOF
FREQUENCY=${FREQUENCY}
SAMPLERATE=${SAMPLERATE}
GAIN=${GAIN}
THRESHOLD=${THRESHOLD}
FFT_BINS=${FFT_BINS}
FFT_SAMPLES=${FFT_SAMPLES}
DURATION_MIN=${DURATION_MIN}
DURATION_MAX=${DURATION_MAX}
KEEPALIVE=${KEEPALIVE}
POS_X=${POS_X}
POS_Y=${POS_Y}
ORIENTATION_OFFSET=${ORIENTATION_OFFSET}
EOF

case "${DEVICE}" in
"blue")
	ORIENTATION=`awk '{print $1 + 0}' <<<"${ORIENTATION_OFFSET}"`
    ;;
"yellow")
	ORIENTATION=`awk '{print $1 + 90}' <<<"${ORIENTATION_OFFSET}"`
    ;;
"red")
	ORIENTATION=`awk '{print $1 + 180}' <<<"${ORIENTATION_OFFSET}"`
    ;;
"green")
	ORIENTATION=`awk '{print $1 + 270}' <<<"${ORIENTATION_OFFSET}"`
    ;;
esac

echo "# Creating run database and tables..."
mysql -e "CREATE DATABASE IF NOT EXISTS rteu;"
mysql -e "CREATE TABLE IF NOT EXISTS rteu.runs (
  id            int(10) unsigned     NOT NULL AUTO_INCREMENT,
  center_freq   int(10) unsigned     DEFAULT NULL,
  samplerate    int(10) unsigned     DEFAULT NULL,
  gain          tinyint(3) unsigned  DEFAULT NULL,
  threshold     tinyint(3) unsigned  DEFAULT NULL,
  fft_bins      smallint(5) unsigned DEFAULT NULL,
  fft_samples   tinyint(3) unsigned  DEFAULT NULL,
  duration_min  float                DEFAULT NULL,
  duration_max  float                DEFAULT NULL,
  keepalive     smallint(5) unsigned DEFAULT NULL,
  hostname      varchar(60)          DEFAULT NULL,
  device        varchar(10)          DEFAULT NULL,
  pos_x         float                DEFAULT NULL,
  pos_y         float                DEFAULT NULL,
  orientation   smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (id)
) DEFAULT CHARSET=latin1;"

echo "# Inserting run into table..."
DB_RUN_ID=`mysql --skip-column-names --batch -e "INSERT INTO rteu.runs (center_freq, samplerate, gain, threshold, fft_bins, fft_samples, duration_min, duration_max, keepalive, hostname, device, pos_x, pos_y, orientation)
	VALUE(${FREQUENCY}, ${SAMPLERATE}, ${GAIN}, ${THRESHOLD}, ${FFT_BINS}, ${FFT_SAMPLES}, ${DURATION_MIN}, ${DURATION_MAX}, ${KEEPALIVE}, '${HOSTNAME}', '${DEVICE}', ${POS_X}, ${POS_Y}, ${ORIENTATION});
	SELECT LAST_INSERT_ID();"`

# reenable failure resilience
set +e +o pipefail

# run actual detection
echo "# Starting detection (run ${DB_RUN_ID})..."
rtl_sdr -d ${DEVICE} -f ${FREQUENCY} -s ${SAMPLERATE} -g ${GAIN} - | \
	rtlsdr_fcu 30s | \
	rtlsdr_signal_detect --sql --db_run_id ${DB_RUN_ID} -s -t ${THRESHOLD} -r ${SAMPLERATE} -b ${FFT_BINS} -n ${FFT_SAMPLES} --ll ${DURATION_MIN} --lu ${DURATION_MAX} -k ${KEEPALIVE} >> ${OUTFILE}

# if a process finishes (and isn't killed), restart all services
echo "# Restarting all signal_detect instances in 10 seconds"
sleep 10
systemctl restart signal_detect@*

# keep script running, such that it doesn't get restart twice
sleep 10
