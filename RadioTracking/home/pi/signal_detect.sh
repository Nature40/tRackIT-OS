#!/usr/bin/env bash

set -e
ulimit -c unlimited

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

# additional configuration
source "/boot/rtlsdr_signal_detect.conf"

# test if device is available
rtl_sdr -d ${1} -f ${FREQUENCY} -s ${SAMPLERATE} -g ${GAIN} -n1 /dev/null

# generate output paths
BASEFILE="/data/`hostname`/rtlsdr_signal_detect/`date +"%Y-%m-%dT%H%M%S"`"
METAFILE="${BASEFILE}.conf"
OUTFILE="${BASEFILE}_${1}.csv"

# create output folder
mkdir -p `dirname ${BASEFILE}`

# save configuration
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
EOF

# run actual detection
rtl_sdr -d ${1} -f ${FREQUENCY} -s ${SAMPLERATE} -g ${GAIN} - | \
	rtlsdr_signal_detect --sql -s -t ${THRESHOLD} -r ${SAMPLERATE} -b ${FFT_BINS} -n ${FFT_SAMPLES} --ll ${DURATION_MIN} --lu ${DURATION_MAX} -k ${KEEPALIVE} >> ${OUTFILE}
