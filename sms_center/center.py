#!/usr/bin/python
import sys, getopt
import serial
import requests
import time
import urllib
from pytz import timezone
from messaging.sms import SmsSubmit
from messaging.sms import SmsDeliver
API_URL="edit this"

TIMEZONE = 'Asia/Makassar'
check_balance = {'51010':'*888#','51011':'*123#'}
def log(text):
    print time.strftime("[%d/%m/%Y"),time.strftime("%H:%M:%S]"),text
def at_ccid(s):
    s.write('AT+CCID?\r')
    ret=s.readlines()
    while len(ret)<4:
        ret=s.readlines()
    a,msg,b,ret=ret
    a=msg.find('"')+1
    b=msg.rfind('"')
    iccid=msg[a:b]
    return iccid    
def at_cops(s):
    s.write('AT+COPS?\r')
    ret=s.readlines()
    while len(ret)<4:
        ret=s.readlines()
    a,msg,b,ret=ret
    return msg.splitlines()[0].split(',')[2]

def main(argv):
    if len(argv)<1:
        print("\nSyntax: ./center.py <port>")
        exit() 
    port = argv[0]
    print("Opening %s..." % port )
    try:
        s = serial.Serial(port,9600,timeout=1,rtscts=True,dsrdtr=True)
    except:
        raise
        exit()
	#s.write('AT+CFUN=1\r')
	#time.sleep(30)
	#ret=s.readlines()
    print("initializing modem...")
    s.write('ATE0;+CMGF=0;+CNMI=1,2\r')
    ret=s.readlines()
    '''
    print("Checking network status...")
    s.write('AT+CREG?\r')
    ret=s.readlines()
    while len(ret)<4:
        ret=s.readlines()
        print(ret)
        if "+CREG" in ret:
            break
    a,msg,a,ret=ret
    if "+CREG: 0,1" not in msg:
        print "Not connected to network"
        s.close()
        sys.exit(0)
    cops    = at_cops(s)
    log("OPRCODE : "+cops)
    '''
    log('SMS CENTER READY')
    while True:
        try:
            readlAllSMS(s)
        except KeyboardInterrupt:
            break
        except ValueError:
            pass

    s.close()

def readlAllSMS(s):
    s.write("AT+CMGL=4\r")
    rets = s.readlines()
    #print(rets)
    total_sms=0
    for l in rets:
        if len(l)>20:
            #print(l)
            pdu = l.splitlines()[0]
            sms = SmsDeliver(pdu)
            smsc    = sms.data['csca']
            nomor   = sms.data['number']
            tgl     = sms.data['date'].replace(tzinfo=timezone('UTC')).astimezone(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
            pesan   = sms.data['text'].splitlines()[0]
            data={'smsc':smsc,'tgl':tgl,'sender':nomor,'text':pesan}
            log(data)
            total_sms+=1
    #delete all message in simcard memory after read
    if total_sms>0:
        s.write("AT+CMGD=0,4\r")
	readAllsms

if __name__ == "__main__":
   main(sys.argv[1:])
