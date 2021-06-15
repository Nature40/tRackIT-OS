---
menu: Common Tasks
---

# Common Tasks
In this section common tasks with *tRackIT stations* in the field are described.

## Connect to WiFi
*tRackIT stations* create a WiFi access point which can be used to access the configuration interfaces, investigate log files and retrieve data.
The WiFi is named according to the station (default: `tRackIT`) and the default password `BirdsAndBats`.
The WebUI can be accessed using the local IPv4 address [http://169.254.0.1/](http://169.254.0.1/).


## Login via SSH
SSH, the secure shell, is a protocol to connect to other network hosts in a secure manner. 
On a unix (GNU/Linux, macOS, ...) computer, open your local terminal and use the ssh command to open the connection:
```
$ ssh pi@169.254.0.1
The authenticity of host '169.254.0.1 (169.254.0.1)' can't be established.
ECDSA key fingerprint is SHA256:JXyJ1T+1xslHNkiqp3Th1jsQ5Vrk1laKGDBBRqEbtJY.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '169.254.0.1' (ECDSA) to the list of known hosts.
pi@169.254.0.1's password: 
Linux tRackIT 5.10.17-v8+ #1414 SMP PREEMPT Fri Apr 30 13:23:25 BST 2021 aarch64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Fri Jun 11 13:45:58 2021 from 192.168.1.111
pi@tRackIT:~ $ 
```

On Windows other programs do exists to login via ssh, e.g., [Putty](https://www.putty.org).


## Restart RadioTracking
RadioTracking (or more precise *pyradiotracking*) is the signal detection algorithm running on a *tRackIT station*. 
Like most software running in *tRackIT OS* it is supervised by systemd.
It can be restarted by accessing the systemd web interface ([http://169.254.0.1/sysdweb/](http://169.254.0.1/sysdweb/), user: `pi`, password: `natur`). 

You may also [login via ssh](#login-via-ssh) and use `systemctl` to restart a service:
```
pi@tRackIT:~ $ sudo systemctl restart radiotracking
pi@tRackIT:~ $ 
```

## Investigate Log Files
As *systemd* is used for service supervision, log files are maintained using *journald*.
Log files can either be accessed using the web interface ([http://169.254.0.1/sysdweb/](http://169.254.0.1/sysdweb/), user: `pi`, password: `natur`) or when [logged in via ssh](#login-via-ssh) using `journalctl`:

````
pi@tRackIT:~ $ journalctl -fu radiotracking
Jun 15 16:39:59 tRackIT systemd[1]: Started RadioTracking.
Jun 15 16:40:07 tRackIT bash[1410]: INFO:radiotracking:Starting all analyzers
Jun 15 16:40:07 tRackIT bash[1410]: INFO:radiotracking.analyze:Using '0' as device index.
Jun 15 16:40:07 tRackIT bash[1410]: INFO:radiotracking:SDR 0 CPU affinity: pid 1417's current affinity list: 0-3
Jun 15 16:40:07 tRackIT bash[1410]: INFO:radiotracking:SDR 0 CPU affinity: pid 1417's new affinity list: 0
Jun 15 16:40:07 tRackIT bash[1410]: INFO:radiotracking.analyze:Using '1' as device index.
...
```

> Note: The option `-u radiotracking` specifies the radiotracking unit; option `-f` enables following logs, such that the stream of log messages is printed immediately; end the stream with `^C` (CTRL-C).

