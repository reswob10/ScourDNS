import os, sys, string, time, csv, operator, argparse
# from Tkinter import *
from datetime import datetime, timedelta, date
#from datetime import timedelta
#from datetime import date
from sys import stdout

# routine to check to see if a variable is a number or not
# could do this with regex inline as well
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#
ans1 = ['1', '2', '3']
print "1 - Full FQDN\n2 - Domain.TLD\n3 - TLD only"
ans = '0'
while ans not in ans1:
    print "\nPlease provide an answer 1, 2 or 3"
    ans = raw_input("What parameter would you like to search for?  ")


findip = raw_input('What is the domain you want to link to IPs? ')

countcycles = 0

DNSLOGFILE = ['Z:/DNS/DNS.log' , 'Y:/DNS.log', 'X:/dns.log']

csvfile = open(findip +'_results1.csv', 'wb')
output1 = csv.writer(csvfile)
output1.writerow(['Time', 'IP', 'FQDN'])
print "\nResults will be saved in ", csvfile

goon = False

for LOGFILE in DNSLOGFILE:
        DNSLOG = open(LOGFILE)
        print 'Now processing ', LOGFILE
        for line in DNSLOG:
            if 'not match any outstanding query' in line: continue
            if 'The DNS server has started.' in line: continue
            if 'The DNS server has finished the background loading of zones' in line: continue
            # split line to parse and check to see if begining of line is a date.  If so, continue to parse line
            p1 = line.split(' ')
            p2 = p1[0].split('/')
            countcycles += 1
            try:
                if is_number(p2[0]) == True and is_number(p2[1]) == True and is_number(p2[2]) == True: goon = True
                else: goon = False
            except:
                print "This line failed to process ", line
                continue
            if goon == True:
                # continue previous split to get time.
                p4 = p1[1].split(':')
                # print p4[0], '   ', p1[2]
                # print '\n', line
                if p1[2] == 'PM': H = int(p4[0]) + 12
                else: H = int(p4[0])
                M = int(p4[1])
                S = int(p4[2])
                #print H, M, S
                try: datethyme1 = datetime(int(p2[2]),int(p2[0]),int(p2[1]), H, M, S)
                except: datethyme1 = datetime(int(p2[2]),int(p2[0]),int(p2[1]))
                p4 = line.split('.')
                p41 = p4[0].split(' ')
                try:
                    p42 = p4[3].split(' ')
                except:
                    print 'The following line did not parse correctly to get the IP:\n'
                    print ('\t' + line + '\n')
                try: ipaddr = p41[-1] + '.' + p4[1] + '.' +  p4[2] + '.' +  p42[0]
                except: ipaddr = line
                cnt = 0
                stdout.write("\r%s" % countcycles +'    ')
                stdout.flush()
                # p4 = line.split('.')
                # p41 = p4[0].split(' ')
                p3 = line.split(')')
                for x in p3:
                    cnt = cnt + 1
                    try:
                        check1 = x[-2:]
                    except IndexError:
                        print line #if args.vlevel > 0:
                    #if countcycles > 800: sys.exit() # This line is used for troubleshooting and stops the program quickly
                    if x[-2:] == '(0':
                        #print x
                        TDL = p3[cnt - 1]
                        TDLdom = TDL.split('(')
                        if len(TDLdom[0]) > 80: continue
                        TDL1 = p3[cnt - 2]
                        TDL1dom = TDL1.split('(')
                        TDL2 = p3[cnt - 3]
                        TDL2dom = TDL2.split('(')
                        try:
                            TDL3 = p3[cnt - 4]
                            TDL3dom = TDL3.split('(')
                        except:
                            TDL3 = ' '
                        try:
                            TDL4 = p3[cnt - 5]
                            TDL4dom = TDL4.split('(')
                        except:
                            TDL4 = ' '
                        try:
                            TDL5 = p3[cnt - 6]
                            TDL5dom = TDL5.split('(')
                        except:
                            TDL5dom = ' '
                        if TDL5dom[0] != '' and len(TDL5dom[0]) < 80 and len(TDL4dom[0]) < 80 and len(TDL3dom[0]) < 80 and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                            #if args.vlevel > 0:print 'This is for x.x.x.x.x.x ' , TDL5dom[0] + '.' + TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            FQDN1 = TDL5dom[0] + '.' + TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                        elif TDL4dom[0] != '' and len(TDL4dom[0]) < 80 and len(TDL3dom[0]) < 80 and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                            #if args.vlevel > 0:print 'This is for x.x.x.x.x ', TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            FQDN1 = TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                        elif TDL3dom[0] != '' and len(TDL3dom[0]) < 80 and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                            #if args.vlevel > 0:print 'This is for x.x.x.x ' , TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            FQDN1 = TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                        elif TDL2dom[0] != '' and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                            #print TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            if len(TDL2dom[0]) > 80:
                                #if args.vlevel > 0:print 'this is for x.x', TDL1dom[0]
                                FQDN1 = TDL1dom[0] + '.' + TDLdom[0]
                            else:
                                #if args.vlevel > 0:print 'This is for x.x.x', TDL1dom[0]
                                FQDN1 = TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                        elif len(TDL2dom[0]) > 80:
                            #if args.vlevel > 0:print 'This is for the second x.x ' , TDL1dom[0] + '.' + TDLdom[0]
                            FQDN1 = TDL1dom[0] + '.' + TDLdom[0] #print 'the FQDN is ', FQDN1
                        DomainTLD = TDL1dom[0] + '.' + TDLdom[0]
                        if ans == '1':
                            if findip == FQDN1:
                                #print line #datethyme1, ipaddr, FQDN1
                                output1.writerow([datethyme1, ipaddr, FQDN1])
                        elif ans == '2':
                            if findip == DomainTLD:
                                #print line
                                output1.writerow([datethyme1, ipaddr, FQDN1])
                        elif ans == '3':
                            if findip == TDLdom[0]:
                                #print line
                                output1.writerow([datethyme1, ipaddr, FQDN1])
                        #domain1 = TDL1dom[0] + '.' + TDLdom[0]


