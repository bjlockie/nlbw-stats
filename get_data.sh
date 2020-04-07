#!/bin/ash

for f in $(ls -t *.db.*)
do
    echo $f
    YR=`echo $f | cut -c 1-4`
    MN=`echo $f | cut -c 5-6`
    DY=`echo $f | cut -c 7-8`
    echo "$YR-$MN-$DY"
    # export database
   	`nlbw -t $YR\-$MN\-$DY -c csv > $YR\-$MN\-$DY.csv`

    # "family"        "proto" "port"  "mac"   "ip"    "conns" "rx_bytes"      "rx_pkts"       "tx_bytes"      "tx_pkts"       "layer7"
done

for f in $(ls -t *.csv)
do
     cat $f
done
