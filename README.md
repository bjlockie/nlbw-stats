<B> \* LIKELY HAS BUGS, UPLOADED FOR BACKUP *

# nlbw_stats
stats slicer for json output of daily nlbwmon (openwrt) databases

I wanted better stats on my Raspberry Pi4 openwrt router like the tomato firmware has.
I decided to scp json output of daily databases of nlbw to a Linux desktop and load them into a sqlite database so reports can be done with SQL.
Maybe eventually it can all be done on the Raspberry Pi 4 and have a web interface. :-)

I bought a TP Link UE300 (USB3 10/100/1000 LAN) and a Alfa AWUS036ACM USB3 wifi adapter (Mediatek7612U  chipset) for AP
I build an image using imagebuilder:
http://downloads.openwrt.org/snapshots/targets/bcm27xx/bcm2711/


1. Set up (nlbwmon) https://github.com/jow-/nlbwmon on an openwrt router.
2. Set up nlbwmon database interval to 1 day.
3. Set up dhcp/static IPs for hosts you want to track.

This repo will have"
1. The imagebuilder comand I use
2 a bash script to run nlbw (via ssh) to create the json output and scp the json and nlbwmon databases to your desktop
2. a python program to load the json and create the sqlite database
