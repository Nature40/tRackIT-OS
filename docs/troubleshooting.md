---
menu: Troubleshooting
---

# Troubleshooting
In this section, common errors and problems are described and potential solutions are discussed. 

> Note: The solutions discussed in this section are not intended to be definitive, but should serve as a possible starting point for resolution.

## The *tRackIT station* keeps on restarting.
There are multiple reasons why *pyradiotracking* or the *tRackIT station* keeps on restarting, the underlying problems are:
1. A bad USB connection of an SDR stick or the USB hub;
2. A broken or failing SDR stick or
3. High system load or high temperatures. 

Bad connections and failing SDR sticks can be identified by [looking at `pyradiotrackings` log files](tasks#investigate-log-files) and check if the same SDR is failing over and over again:

```
Jun 15 16:03:13 mof-rts-00015 bash[1135]: WARNING:radiotracking:SDR 1 will be restarted.
Jun 15 16:03:14 mof-rts-00015 bash[1135]: Found Rafael Micro R820T tuner
Jun 15 16:03:14 mof-rts-00015 bash[1135]: [R82XX] PLL not locked!
Jun 15 16:03:14 mof-rts-00015 bash[1135]: Allocating 15 zero-copy buffers
Jun 15 16:03:19 mof-rts-00015 bash[1135]: WARNING:radiotracking.analyze:SDR 1 total clock drift (0.93777 s) is larger than two blocks, signal detection is degraded. Terminating...
Jun 15 16:03:21 mof-rts-00015 bash[1135]: WARNING:radiotracking:SDR 1 will be restarted.
Jun 15 16:03:22 mof-rts-00015 bash[1135]: Found Rafael Micro R820T tuner
Jun 15 16:03:22 mof-rts-00015 bash[1135]: [R82XX] PLL not locked!
Jun 15 16:03:14 mof-rts-00015 bash[1135]: Allocating 15 zero-copy buffers
...
```
The multiple restarting of SDR 1 indicates, that its connection or the device itself is broken and should be checked and potentially replaced. 

If the different SDRs are failing and restarting at random, it is more likely that the system has a general problem.

```
Jun 15 16:04:03 mof-rts-00015 bash[1246]: WARNING:radiotracking.analyze:SDR 1 total clock drift (1.03648 s) is larger than two blocks, signal detection is degraded. Terminating...
Jun 15 16:04:04 mof-rts-00015 bash[1246]: WARNING:radiotracking.analyze:SDR 2 total clock drift (0.91334 s) is larger than two blocks, signal detection is degraded. Terminating...
Jun 15 16:04:04 mof-rts-00015 bash[1246]: WARNING:radiotracking.analyze:SDR 3 total clock drift (0.91257 s) is larger than two blocks, signal detection is degraded. Terminating...
Jun 15 16:04:05 mof-rts-00015 bash[1246]: WARNING:radiotracking:SDR 1 will be restarted.
Jun 15 16:04:05 mof-rts-00015 bash[1246]: WARNING:radiotracking:SDR 2 will be restarted.
Jun 15 16:04:05 mof-rts-00015 bash[1246]: WARNING:radiotracking:SDR 3 will be restarted.
Jun 15 16:04:05 mof-rts-00015 bash[1246]: Found Rafael Micro R820T tuner
Jun 15 16:04:06 mof-rts-00015 bash[1246]: Found Rafael Micro R820T tuner
Jun 15 16:04:06 mof-rts-00015 bash[1246]: Found Rafael Micro R820T tuner
Jun 15 16:04:06 mof-rts-00015 bash[1246]: [R82XX] PLL not locked!
Jun 15 16:04:06 mof-rts-00015 bash[1246]: [R82XX] PLL not locked!
Jun 15 16:04:06 mof-rts-00015 bash[1246]: [R82XX] PLL not locked!
Jun 15 16:04:06 mof-rts-00015 bash[1246]: Allocating 15 zero-copy buffers
Jun 15 16:04:06 mof-rts-00015 bash[1246]: Allocating 15 zero-copy buffers
Jun 15 16:04:06 mof-rts-00015 bash[1246]: Allocating 15 zero-copy buffers
```

The warning message in line 1 indicates that data is not analysed fast enough on this station, which leads to the analyzer being restarted. 
Low power, hot temperatures and demanding settings (including high numbers of VHF transmitters) can lead to loads higher than the system capacity triggering this behavior. 
To cope with the problem:
1. Check the hardware, especially the heat sink, and the temperature monitoring if the temperature is below 80 °C;
2. Check the power connection to the Raspberry Pi and the USB hub; and
3. Alter settings, e.g., raise `signal_threshold_dbw`, `snr_threshold_db` and `signal_min_duration_ms`.

