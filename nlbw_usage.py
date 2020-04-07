#!/usr/bin/python

# git repo: nlbw python sqlite3 stats
# put nlbw stats into sqlite3

import sys
import glob
import json
import sqlite3
from datetime import date
from decimal import getcontext, Decimal


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    step_unit = 1000.0 # 1024?
    results=[]
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        results.append("%3.2f %s" % (num, x))
        num /= step_unit
    return results


def createTable( conn ):
    cur = conn.cursor()
    cur.execute('create table trafficEntry(traffic_date, family, proto, port, mac, ip, conns, rx_bytes, rx_pkts, tx_bytes, tx_pkts, layer7)')
    return cur.lastrowid
    

# desktop 70:85:C2:B4:61:37 192.168.1.4
# getSum_bytes( conn, '2020', '03', '70:85:C2:B4:61:37' )
# all downnload for month
# getSum_bytes( conn, '2020', '03' )
def getSum_bytes( conn, year, month, upload=False, mac='' ):
    bytes=0
    sql = 'select sum('
    if upload:
        sql += 'tx'
    else:
        sql += 'rx'
    sql += '_bytes) from trafficEntry where traffic_date like ?'
    if mac:
        sql += 'and mac=?'
    cur = conn.cursor()
    dt=year+'-'+month+'-%'
    try:
        if mac:
            cur.execute(sql, [dt, mac])
        else:
            cur.execute(sql, [dt])
        
        bytes_list=cur.fetchall()
        bytes=bytes_list[0][0]
    except sqlite3.Error as e:
        print(e)
    sizes=convert_bytes(bytes)
    kb=sizes[1]
    mb=sizes[2]
    gb=sizes[3]
    tb=sizes[4]
    return [bytes, kb, mb, gb, tb]
    

class trafficEntry:
    def __init__(self, traffic_date, vals ):
        self.traffic_date = traffic_date
        self.family = vals[0]
        self.proto = vals[1]
        self.port = vals[2]
        self.mac = vals[3].upper()
        self.ip = vals[4]
        self.conns = vals[5]
        self.rx_bytes = vals[6]
        self.rx_pkts = vals[7]
        self.tx_bytes = vals[8]
        self.tx_pkts = vals[9]
        self.layer7 = vals[10]
        
    def insertsql( self, conn ):
#        try:
#            sql = '''SELECT traffic_date, mac FROM trafficEntry'''
#            cur.execute(sql)
#            return_list=cur.fetchall()
#            if return_list[0]:
#        except sqlite3.Error as e:
#            print(e)
        
        sql = ''' INSERT INTO trafficEntry(traffic_date, family, proto, port, mac, ip, conns, rx_bytes, rx_pkts, tx_bytes, tx_pkts, layer7) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
        try:
            cur = conn.cursor()
            cur.execute(sql, [self.traffic_date, self.family, self.proto, self.port, self.mac, self.ip, self.conns, self.rx_bytes, self.rx_pkts, self.tx_bytes, self.tx_pkts, self.layer7])
        except sqlite3.Error as e:
            print(e)
            print self.traffic_date+'-'+self.mac

        return cur.lastrowid


# parse the file name to get the date
def getfnamedt( fileName ):
    # strip the trailing . and everything after
    before = fileName.split(".json")[0]
    # strip everything leading up to the last slash
    afterArray = before.split("/")
    after = afterArray[-1]
    return after


def findMAC( allTrafficList, mac ):
    foundIt = []
    for trafficList in allTrafficList:
       if len(trafficList)>0:
          if mac==trafficList[0].mac:
              foundIt = trafficList
    
    if len(foundIt)==0:
        allTrafficList.append( foundIt )
    
    return foundIt


def dumpAllTrafficList( allTrafficList, upload=False, to_db=None ):
    cday = date.today()
    c_day = cday.strftime("%Y-%m-%d")
    
    total_bytes=0
    for trafficList in allTrafficList:
        daily_bytes = 0
        for trafficListEntry in trafficList:
            if to_db:
                if trafficListEntry.traffic_date != c_day:
                    trafficListEntry.insertsql( to_db )
            else:
                if upload:
                    daily_bytes += trafficListEntry.tx_bytes
                else:
                    daily_bytes += trafficListEntry.rx_bytes
        
        if not to_db:
            sizes=convert_bytes(daily_bytes)
            kb=sizes[1]
            mb=sizes[2]
            gb=sizes[3]
            tb=sizes[4]
            print( "daily total: "+trafficListEntry.mac+": "+str(total_bytes)+" bytes, "+kb+", "+mb+", "+gb+', '+tb )
            print
        
        total_bytes += daily_bytes
    if not to_db:
        sizes=convert_bytes(total_bytes)
        kb=sizes[1]
        mb=sizes[2]
        gb=sizes[3]
        tb=sizes[4]
        
        print( "total (all MACs): "+str(total_bytes)+" bytes, "+kb+", "+mb+", "+gb+', '+tb )
        print


def new_data( conn ):
    #fileList = glob.glob( sys.argv[1]+"/*.json" )
    fileList = glob.glob( "./test_data"+"/*.json" )
    # JSON_FILE = "./test_data/2020-03-01.json"
    
    allTrafficList = []
    
    for JSON_FILE in fileList:
        traffic = json.load(open(JSON_FILE))
        fndate = getfnamedt( JSON_FILE )
        
        # create lists of trafficEntry objects for each MAC
        for vals in traffic["data"]:
            # skip '00:00:00:00:00:00' MACs
            if vals[3]!='00:00:00:00:00:00':
                # find the list with the target MAC
                trafficList=findMAC(allTrafficList, vals[3])
                trafficList.append( trafficEntry( fndate, vals ) )
    
    dumpAllTrafficList( allTrafficList, False, conn )


DB_FILE = "nlbw_usage.db"

conn = None
try:
    conn = sqlite3.connect(DB_FILE)
except sys.Error as e:
    print(e)

#createTable( conn )
#new_data( conn )
#conn.commit()

print( 'March 2020:' )
print( getSum_bytes( conn, '2020', '03' ) )



conn.close()
