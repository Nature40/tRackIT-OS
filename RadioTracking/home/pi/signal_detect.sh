#!/usr/bin/env bash

set -e
ulimit -c unlimited

FREQUENCY=150100001
SAMPLERATE=250000
GAIN=49
THRESHOLD=11
FFT_BINS=400
FFT_SAMPLES=50
DURATION_MIN=0
DURATION_MAX=1
KEEPALIVE=300

source "/boot/rtlsdr_signal_detect.conf"

OUTFILE="/data/`hostname`/rtlsdr_signal_detect/`date +"%Y-%m-%dT%H%M%S"`_$1.csv"
mkdir -p `dirname $OUTFILE`

rtl_sdr -d $1 -f $FREQUENCY -s $SAMPLERATE -g $GAIN - 2> $OUTFILE | \
rtlsdr_signal_detect -s -t $THRESHOLD -r $SAMPLERATE -b ${FFT_BINS} -n ${FFT_SAMPLES} --ll ${DURATION_MIN} --lu ${DURATION_MAX} -k ${KEEPALIVE} >> $OUTFILE 2>&1

mv core `basename $OUTFILE`.core

