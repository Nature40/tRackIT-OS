#!/usr/bin/env bash

i=0

for color in blue yellow red green; do
	echo "Operating on device $i ($color):"
	rtl_sdr -n 1 -d $i /dev/null
	
	rtl_eeprom -d $i -w RTL2838UHIDIR.bin && yes | rtl_eeprom -d $i -s $color
	i=$((i+1))
done

echo "Done."

