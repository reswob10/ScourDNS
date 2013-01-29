
# Files needed to run this script:  masterlist.txt, newblack.txt, list of blacklists, greylist.txt,
# countrycode list in csv formate (wonder if there is some way to automate getting this)

# need to find way to fully parse line and get snd rcv and other codes per
# http://www.computerperformance.co.uk/w2k3/services/DNS_debug_logging.htm

# option to strip out gstatic.com, mcafee.com, cloudfront.net, cedexis-radar.net

# better help section writeup

# save each day in new directory/folder
# newpath = r'C:\Program Files\arbitrary'
# if not os.path.exists(newpath): os.makedirs(newpath)

import os, sys, string, time, csv, operator, argparse, Tkinter, tkFileDialog
# from Tkinter import *
from datetime import datetime, timedelta, date
# root = Tk()
# root.withdraw()
from sys import stdout
parser = argparse.ArgumentParser(description='Options to run.')
parser.add_argument('-V', dest='vlevel', action='store', default = 0, help = "Level of verbosity: 0 - None, 1 - Minimum, 2 - Maximum")
parser.add_argument('-top', dest='topdoms', action='store', default = 10, help = "This is the number of top domains to list. Default is 10.")
parser.add_argument('-bottom', dest='botdoms', action='store', default = 30, help = "This is the number of bottom domains to list. Default is 30.")
parser.add_argument('-s', dest='sleep1', action='store', default = 0, help="This is how many seconds the program should sleep before running again. Default is 0, which means the program stops after one run.")
parser.add_argument('-test', action='store_true', help="set this switch to tell the program whether or not run is testing.  No changes to master file are made.")
parser.add_argument('-update', action='store_true', help='set this switch to update the config file')
parser.add_argument('-create', action='store_true', help='set this switch to create a new config file.  NOTE: This will overwrite any old config files')
parser.add_argument('-config', action='store_true', help='set this swtich to print the configuration then exit.')
parser.add_argument('-ig', action='store_true', help='set this switch to ignore tracking web sites.  See configuration for list')
parser.add_argument('-d', dest='days', action='store', default = 1, help =  "Number of days ago to start checking DNS logs.  Default is 1 day.")
#parser.add_argument('-help', action='store_true', help='display help')
args = parser.parse_args()

# for some reason, need to reload time to get sleep to work
time = reload(time)

# routine to check to see if a variable is a number or not
# could do this with regex inline as well
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# function to create the configuration file
def createconfig():

    print '\n\nYou have chosen to create a new configuration for the DNS script. '
    checkthis = raw_input ('Do you want to continue? (y/n)  ')
    answers = ['y', 'Y']
    if checkthis not in answers:
        print 'You have chosen not to create a new configuration file.'
        print 'The program will now exit.'
        sys.exit()
    config = 'dnsconfig.txt'
    print '\n\nFirst you must chose one or more DNS debug log files the program '
    print ' will read during each run.'
    print 'Remember, these log files must be on a mapped drive.'
    logfiles = [ ]
    ans = 'y'
    while ans == 'y' or ans =='Y':
        print '\nPlease select a DNS debug log file'
        logfile = tkFileDialog.askopenfilename()
        logfiles.append(logfile)
        ans = raw_input('Do you want to add another DNS debug log file? (y/n)  ')
    print '\n\nBlacklists is a file or are files that contain the FQDNs of web '
    print 'locations that you do not want users to visit.'
    print 'You may not have any blacklists or you may have several. '
    checkthis = raw_input ('\nDo you want to select any blacklists?  (y/n)  ')
    blackfiles = []
    if checkthis == 'y' or checkthis =='Y':
        print 'Now you must select the file or files that contain your domain blacklists.'
        ans = 'y'
        while ans == 'y' or ans =='Y':
            print 'Please select a blacklist file:'
            blackfile = tkFileDialog.askopenfilename()
            blackfiles.append(blackfile)
            ans = raw_input('Do you want to add another blacklist file? (y/n)  ')
    
    print '\n\nGreylists is a file that contains the FQDN of web locations that users may'
    print ' be allowed to visit, you want to keep tabs on how much or who goes there. '
    print 'You may not have any greylists or you may have several. '
    checkthis = raw_input ('\nDo you want to select a greylist file?  (y/n)  ')
    if checkthis == 'y' or checkthis =='Y':
        print ' Now you must select the file contains your domain greylists.'
        greyfile = tkFileDialog.askopenfilename()
    else: greyfile = 'None'
    print '\n\n It is important to identify you own internal networks.  If machines external '
    print 'to your network are using you DNS, this may be a cause for concern because it can '
    print 'signal a misconfigured machine on someone else\'s network or malicious traffic.  '
    print 'To validate each query, please provide the \\16 address (i.e. The first two octets)'
    print 'for each network you know is using your DNS server.'
    print '\nIMPORNTANT!!!  You must enter AT LEAST ONE address!!! '
    ans = 'y'
    getips = []
    while ans =='y' or ans =='Y':
         getip = raw_input ('\n Please enter a \\16 address:  ')
         getips.append(getip)
         ans = raw_input('\nDo you want to enter another \\16 network? (y/n)  ')
    print '\n\n There are a number of websites that exist solely to track user web movements.  '
    print 'For example, Google uses all websites ending in gstatic.com to track user activity.  While '
    print 'it may be beneficial to see audit those DNS queries, the sheer number of them can quickly '
    print 'fill up the master list/database.  If you chose, you can tell the script to only count the '
    print 'number of times the tracking sites were looked up and not enter them into the master'
    print 'list/database.  After reviewing your output for a few days, you can enter a list of domains '
    print 'you want to count but not track in the master list/database.  By useing the -ig argument,'
    print 'the script will check the last two octet names against those domains you have listed '
    print 'in the config and if there is a match, the script will simply count the number of times '
    print 'the domain is seen, but not enter it into the master list/database. '
    checkthis = raw_input ('\nDo you want to enter any domains to ignore? (y/n)  ')
    if checkthis == 'y' or checkthis =='Y':#
        print ' Enter all domains in the following format:  sample.com '
        ans = 'y'
        ignoredomains = []
        while ans == 'y' or ans == 'Y':
            getdom = raw_input ('Please enter a domain to ignore:  ')
            ignoredomains.append(getdom)
            ans = raw_input ('Do you wnat to enter another domain to ignore? (y/n)  ')
    print '\n\n You have finished choosing all the parameters necessary for the program to run.  '
    print ' Please review your choices to ensure they are correct.  '
    print '\n These are the DNS debug log files you chose:  '
    for debug in logfiles:
        print debug
    print ' These are the blacklist files you chose:  '
    if len(blackfiles) == 0: print 'None'
    else:
        for black in blackfiles: print black
    print ' These is the greylist file you chose:\n', greyfile
    print ' These are the networks that you entered as valid users of your DNS server:  '
    for ip in getips: print ip
    print 'These are the domains you will not have entered into the master list:  '
    for dom in ignoredomains: print dom
    print 'If you choose yes to the following question, you will overwrite the current configuration file if present!'
    checkthis = raw_input ('Is the above information correct?  (y/n)  ')
    if checkthis == 'y' or checkthis == 'Y':
        writeconfig = open('config.txt', 'wb')
        for log in logfiles: writeconfig.write('DNS_DEBUG_FILES=' + log +'\n')
        for black in blackfiles: writeconfig.write('BLACKLIST_FILES=' + black +'\n')
        for ig in ignoredomains: writeconfig.write('DOMAINS_IGNORE=' + ig + '\n')
        writeconfig.write('GREYLIST_FILE=' + greyfile +'\n')
        for ip in getips: writeconfig.write('SAFE_IPS=' + ip + '\n')
        print ' Thank you for setting up your configuration file.  If at any time you want to edit '
        print 'this file, simply rerun the script with the -create switch.  To review your settings, '  
        print 'run the script with the -config switch.  The program will now exit.'
        writeconfig.close()
        sys.exit()
    else:
        print 'Current configuration remains unchanged.'
        print 'Please restart the program with the -create switch and verify each entry before hitting return.'  
        sys.exit()

# function to load the blacklist and reload the blacklist if it changes
def loadblacklist():
    cnt = 0
    for BL in Blist:
        try : black = open(BL)   
        except:
            print 'Unable to open the ', BL, ' blacklist. will continue to load others. To quit hit ctrl - c'
            time.sleep(1)
            continue
        for line in black:
            blacklist.append(line.rstrip())
            cnt = cnt + 1
        black.close()
    print 'The number of entries in the black list is ', cnt

# function to load the greylist
def loadgreylist():
    cnt = 0
    try :
        grey = open(grey1)
        for line in grey:
            greylist.append(line.rstrip())
            cnt = cnt + 1
    except:
        print 'Unable to open the greylist. will continue to run without comparisons. to quit hit ctrl - c'
        time.sleep(1)
    print 'The number of entries in the grey list is ', cnt


if args.create == True: createconfig()

# Open configuration file and read parameters
DNSLOGFILE = []
Blist = []
intip = []
IGDOMAINS = []

# config = {}
try: configfile = open('config.txt', 'rb')
except:
    print 'Could not open config file. Please verify it exists, is named correctly and is not already open by another program.'
    print 'To create a new config file or update the current one, run the program with the -create switch'
    sys.exit()

grey1 = 'None'
#newblack = 'None'
for line in configfile:
    if 'DNS_DEBUG_FILES' in line:
        info = line.split('=')
        DNSLOGFILE.append(info[1].rstrip())
    if 'BLACKLIST_FILES' in line:
        info = line.split('=')
        Blist.append(info[1].rstrip())
    if 'SAFE_IPS' in line:
        info = line.split('=')
        intip.append(info[1].rstrip())
    if 'GREYLIST_FILE' in line:
        info = line.split('=')
        grey1 = info[1].rstrip()
    if 'DOMAINS_IGNORE' in line:
        info = line.split('=')
        IGDOMAINS.append(info[1].rstrip())

if len(DNSLOGFILE) == 0:
    print ' You must have at least one log file listed.  Please run this program with the -create switch to ID a log file.'
    sys.exit()

# print DNSLOGFILE
# print Blist
# print intip
# print grey1
# print newblack

# get list of dns log files
# ['demo_dns.txt'] #
# ['path to dns logs' , 'if multiple logs', 'separate like this with different path in between each apostrophe', 'z:/path/path/logfile', 'note: must use backward slash like linux, not forward like windows']    
# DNSLOGFILE = ['Z:/DNS/DNS.log' , 'Y:/DNS.log', 'X:/dns.log'] #['demo_dns.txt']

# print configuration on screen at start of script

print '\n\nThese are the parameters the program will use:\n'
print 'The following DNS log files will be used'
for file in DNSLOGFILE:
    print file
if len(Blist) > 0:
    print '\nThe following Blacklists will be checked.'
    for file in Blist: print file
else: print '\n No blacklists will be checked.'
if len(intip) > 0:
    print '\nThe following networks will be viewed as approved to use your DNS servers.'
    for file in intip: print file
else: print '\nThe program will not check to see if unauthorized IPs are using your DNS server.'
if grey1 == 'None':  print '\n No greylists will be checked.'
else: print '\nThe following Greylist will be checked: ', grey1
# if newblack == 'None': print '\n No files will be checked additions to the blacklist'
# else: print '\n The following file will be check for additions to the blacklist: ', newblack
if args.ig == True and len(IGDOMAINS) > 0:
    print '\nThe following domains will be counted but not be added to the masterlist.'
    for domain in IGDOMAINS: print domain
if args.ig == False: print '\nYou have selected NOT to ignore any domains. \n(To ignore domains, run the same command with the -ig switch)'
print '\nThe script will start checking log entries starting ', args.days, ' days ago.'

if args.config == True: sys.exit()

# the following parameter (sleep) only matters if the program is being run, not if the user just wants to see the configuration
if int(args.sleep1) > 0:
    print '\nThe program will sleep for ', args.sleep1, ' seconds between runs unless or until interrupted.'
else:  print '\nThe program will run once, export results and exit.'


# initialize sleep time from argument.  
sleep1 = int(args.sleep1)
#sleep1 = 5000
runtime = 1
countcycles = 0
 
# Initialize first checktime which is set to the time the script starts,  minus 24 hours or 1 day
check2 = date.today()
gettime1 = time.strftime("%d%b%Y%H%M%S", time.localtime())
getdate1 = time.strftime("%d%b%Y", time.localtime())
checktime = datetime.now() - timedelta(days=int(args.days))
if args.vlevel > 0: print checktime

# make new folder for today's output
newpath = 'C:/Python27/projects/' + getdate1
if not os.path.exists(newpath): os.makedirs(newpath)

# create output file for the list of FQDNs and write the labels on the first row
topd = newpath + '/top_domains' + gettime1 + '.csv'
output2 = open(topd, 'wb')
top10today = csv.writer(output2)
top10today.writerow(['Domain Name', 'Count'])
 
# create output file for the flist of TLDs found and write the labels on the first row
topctry = newpath + '/top_countries' + gettime1 + '.csv'
output3 = open(topctry, 'wb')
topcountries = csv.writer(output3)
topcountries.writerow(['Domain Name', 'Count', 'TLD'])
 
# create the output for errors that the script may output duruing execution
errlog = newpath + '/error_log' + gettime1 +'.txt'
output5 = open(errlog, 'wb')
 
# create dictionaries for the following variables to count
newlist = {}
todaytop10 = {}
countrycount = {}
iana = {}
 
# create lists to track and check
blacklist = []
greylist = []
mlist = []
 
 # load the master list
try :
    master = open('masterlist.txt', 'rb')
    for line in master:
        mlist.append(line.rstrip('\n'))
 
except:
    print 'Unable to open the masterlist. will continue to run, but will be unable to determine new domains. to quit hit ctrl - c'
    time.sleep(5)

# close and reopen the master list in append mode.
master.close()
master = open('masterlist.txt', 'ab')

# load all blacklists
badcount = 0


# this is the blacklist that you can add newly found FQDNs to while script is running.  
# the script will check this file on every loop.  If the modified time is newer than the checktime, it will load the FQDNs into the blacklist
# newblack = 'C:/Python27/projects/newblack.txt'
# ['blacklist.txt'] #['different blacklists to load', 'files listed in same manner as dns logs above'] #'blacklist.txt',
#  Blist = [ 'C:/Python27/projects/radar.txt', 'C:/Python27/blacklists/blacklists/hacking/domains', 'C:/Python27/blacklists/blacklists/warez/domains', 'C:/Python27/blacklists/blacklists/suspect/domains', 'C:/Python27/blacklists/blacklists/violence/domains']#['blacklist.txt']
loadblacklist()
# load all greylists.  These are domains that may be suspicious, but appear too often to be indicators in of themselves
if grey1 != 'None' : loadgreylist()
#grey1 = 'C:/Python27/projects/greylist.txt'

 
# load the country codes
try:  
    ccodes = open('country_domain-list.csv')
    countrycode1 = csv.reader(ccodes)
    for line in countrycode1:
        iana[line[0].lstrip('.')] = line[1]
except: print 'unable to open country codes document'


# Start the main loop  
while 1:
    try:
        print '\n\nStarting check at: ', checktime, ' and there are ', len(mlist), ' items in the master list.'
        gettime = time.strftime("%d%b%Y%H%M%S", time.localtime())
        checknewblack = False
        for BL in Blist:
            btime = time.ctime(os.path.getmtime(BL))
            blacktime = datetime.strptime(btime, "%a %b %d %H:%M:%S %Y")
            if int(args.vlevel) > 0: print 'This is the time of the new blacklist: ', blacktime #
            if countcycles > 0:
                if blacktime > checktime: checknewblack = True
        if checknewblack == True:
            print '\nThere have been new domains added to the blacklist.  Now reloading.'
            blacklist = []
            loadblacklist()
        if grey1 != 'None':
            gtime = time.ctime(os.path.getmtime(grey1))#time.ctime(os.path.getmtime(dirname)
            greytime = datetime.strptime(gtime, "%a %b %d %H:%M:%S %Y")
            if int(args.vlevel) > 0: print 'This is the time of the greylist.txt: ', greytime
            if greytime > checktime:
                print 'adding new domains to greylist'
                try:
                    grey = open(grey1)  
                    cnt1 = 0
                    for line in grey:
                        greylist.append(line.rstrip())
                        try: blacklist.remove(line.rstrip())
                        except: print 'not there'
                        cnt1 += 1
                    print 'Added ', cnt1, ' domains to the greylist'
                except:
                    print 'Unable to open the ', grey, ' greylist. will continue to load others. To quit hit ctrl - c'
                    time.sleep(1)
        newdom = newpath + '/new_domains-' + gettime + '.csv'
        output4 = open(newdom, 'wb')
        newdoms = csv.writer(output4)
        newdoms.writerow(['Domain Name', 'Count'])
        newfile = newpath + '/bad_looks-' + gettime + '.csv'
        csvfile = open(newfile, 'wb')
        output1 = csv.writer(csvfile)
        output1.writerow(['Time', 'IP', 'FQDN'])
        greydom = newpath + '/concerned_looks-' + gettime + '.csv'
        greys = open(greydom, 'wb')
        greyout = csv.writer(greys)
        greyout.writerow(['Time', 'IP', 'FQDN'])
        for LOGFILE in DNSLOGFILE:
            try: DNSLOG = open(LOGFILE)
            except:
                print 'Unable to open ', LOGFILE, '.  Will continue with next log file.'
                output5.write('Could not open the following log file:\n')
                output5.write('\t'+ LOGFILE + '\n')
                continue
            print 'Now processing ', LOGFILE
            for line in DNSLOG:
                if 'not match any outstanding query' in line: continue
                if 'The DNS server has started.' in line: continue
                if 'The DNS server has finished the background loading of zones' in line: continue
                # split line to parse and check to see if begining of line is a date.  If so, continue to parse line
                p1 = line.split(' ')
                p2 = p1[0].split('/')
                countcycles = countcycles + 1
                if not len(p2) > 2:
                    continue
                if is_number(p2[0]) == True and is_number(p2[1]) == True and is_number(p2[2]) == True:
                    #print p1[1], p1[2]
                    # continue previous split to get time.
                    p4 = p1[1].split(':')
                    if p1[2] == 'PM': H = int(p4[0]) + 12
                    else: H = int(p4[0])
                    M = int(p4[1])
                    S = int(p4[2])
                    #print H, M, S
                    try: datethyme1 = datetime(int(p2[2]),int(p2[0]),int(p2[1]), H, M, S)
                    except: datethyme1 = datetime(int(p2[2]),int(p2[0]),int(p2[1]))
                    #print 'The checktime is ', checktime, ' and the dns entry time is ', datethyme1
                    #if checktime > datethyme1: continue # comment this line if not at work
                    # restart split of line to get originating IP
                    p4 = line.split('.')
                    p41 = p4[0].split(' ')
                    # print 'First octect is: ', p41[-1]
                    # try: print 'Second octect is: ', p4[1]
                    # except:
                        # print line
                        # sys.exit()
                    # print 'Third octect is: ', p4[2]
                    try:
                        p42 = p4[3].split(' ')
                    except:
                        #print p42
                        #print p42[0]
                        output5.write('The following line did not parse correctly to get the IP:\n')
                        output5.write('\t' + line + '\n')
                    try:
                        ipaddr = p41[-1] + '.' + p4[1] + '.' +  p4[2] + '.' +  p42[0]
                    except:
                        print countcycles
                        print line
                        output5.write(line + ' Could not be used as an IP address\n')
                        continue
                    try:
                        ipcheck = p41[-1] + '.' + p4[1]
                    except:
                        iperr = 1
                        output5.write(line + ' Could not be checked for IP compliance.\n')
                    
                    if ipcheck not in intip:
                        print ipaddr + ' is a DNS request from an external IP'
                        output1.writerow([datethyme1, ipaddr, 'DNS request from external IP'])
                        #if ipcheck == '146.138' : output5.write(line)
                    # restart split to get type of lookup
                    # p5 = line.split('] ')
                    # p51 = p5[1].split(' ')
                    # TYPE = p51[0]
                    # restart split of line to get FQDN being requested
                    p3 = line.split(')')
                    cnt = 0
                    for x in p3:
                        cnt = cnt + 1
                        try:
                            check1 = x[-2:]
                        except IndexError:
                            output5.write('The script could not acquire the last two characters on the line:\n')
                            output5.write(['\t',line,'\n'])
                            if int(args.vlevel) > 0:print line
                        #if countcycles > 1000: sys.exit() # This line is used for troubleshooting and stops the program quickly
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
                            domain1 = TDL1dom[0] + '.' + TDLdom[0]
                            # if domain1 in IGDOMAINS: continue # not sure if I want to skip totally or count as well...
                            if TDL5dom[0] != '' and len(TDL5dom[0]) < 80 and len(TDL4dom[0]) < 80 and len(TDL3dom[0]) < 80 and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                                if int(args.vlevel) > 0:print 'This is for x.x.x.x.x.x ' , TDL5dom[0] + '.' + TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                                FQDN1 = TDL5dom[0] + '.' + TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            elif TDL4dom[0] != '' and len(TDL4dom[0]) < 80 and len(TDL3dom[0]) < 80 and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                                if int(args.vlevel) > 0:print 'This is for x.x.x.x.x ', TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                                FQDN1 = TDL4dom[0] + '.' + TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            elif TDL3dom[0] != '' and len(TDL3dom[0]) < 80 and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                                if int(args.vlevel) > 0:print 'This is for x.x.x.x ' , TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                                FQDN1 = TDL3dom[0] + '.' + TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            elif TDL2dom[0] != '' and len(TDL2dom[0]) < 80 and len(TDL1dom[0]) < 80:
                                #print TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                                if len(TDL2dom[0]) > 80:
                                    if int(args.vlevel) > 0:print 'this is for x.x', TDL1dom[0]
                                    FQDN1 = TDL1dom[0] + '.' + TDLdom[0]
                                else:
                                    if args.vlevel > 0:print 'This is for x.x.x', TDL1dom[0]
                                    FQDN1 = TDL2dom[0] + '.' + TDL1dom[0] + '.' + TDLdom[0]
                            elif len(TDL2dom[0]) > 80:
                                if args.vlevel > 0:print 'This is for the second x.x ' , TDL1dom[0] + '.' + TDLdom[0]
                                FQDN1 = TDL1dom[0] + '.' + TDLdom[0] #print 'the FQDN is ', FQDN1
    
                            
                            # check if the FQDN is in the master list, if so, check to see if it is in the new list
                            # if it is, increment the count by one. Also checks to see if it is in the list of domains to ignore.
                            # if so, it does not add to the master list.
                            # It should never be that the FQDN is in the master list and NOT in the new list.
                            # If the FQDN is not in the master list, add to master list and write to masterlist text file
                            # and add it to the new list dictionary
                            if FQDN1 in mlist:
                                if FQDN1 in newlist:
                                    newlist[FQDN1] += 1
                            else:
                                #print FQDN1
                                if args.ig == True:
                                    if domain1 not in IGDOMAINS: mlist.append(FQDN1)
                                else: mlist.append(FQDN1)
                                if args.test == False:
                                    if args.ig == True:
                                        if domain1 not in IGDOMAINS: master.write(FQDN1 + '\n')
                                    else:  master.write(FQDN1 + '\n')
                                newlist[FQDN1] = 1
                            # check if in the list of todays domains.  if not, add to list of todays domains which
                            # will be sorted later to determine the top ten for that day
                            if FQDN1 in todaytop10:
                                todaytop10[FQDN1] += 1
                            else:
                                todaytop10[FQDN1] = 1
    
                            # check if in the list of top level domains found today.  if not, add to list of top level domains.
                            # will compare against country code list later for top countries.   
                            if TDLdom[0] in countrycount:
                                countrycount[TDLdom[0]] += 1
                            else:
                                countrycount[TDLdom[0]] = 1
                            # check if the FQDN is in any of the loaded blacklists.  if so print and write to the file.
                            # later will list which blacklist it was found in
                            if FQDN1 in blacklist:
                                print FQDN1, ' was found in the blacklist'
                                time.sleep(1)
                                output1.writerow([datethyme1, ipaddr, FQDN1])
                                badcount += 1
                            # check if the FQDN is in any of the loaded greylists.  If so , write to the file
                            if FQDN1 in greylist:
                                greyout.writerow([datethyme1, ipaddr, FQDN1])
    except KeyboardInterrupt:
        # note that if we put the following routine into a def then we can run it when
        # when user does control - c, when sleep1 = 0, or in middle of runs but user does not chose to exit
        print '\n'
        # First we write all the unique FQDNs found to a file along with the count of how many times each was seen
        for key in todaytop10:
            top10today.writerow([key, todaytop10[key]])
        output2.close()
        # Then we reopen the file and read it all back in to a list.
        output2 = open(topd, 'rb')
        top102day = csv.reader(output2)
        list2 = {}
        for line in top102day:
            if line[1] == 'Count': continue
            list2[line[0]] = int(line[1])
        # We then sort that list and print out the top ten from that list
        sortedlist = sorted(list2.items(),key=lambda x: x[1])
        sortedlist.reverse()
        print '\nThese are the top ', args.topdoms, ' domains hit today.\n'
        for x in range(0,int(args.topdoms)+1):
            print sortedlist[x][0], str(sortedlist[x][1])[:-2]
        # I decided not to print all the unique domains one by one.  Just the total because there could be hundreds.
        print
        domcount = len(sortedlist) - 1
        print  '\nThere were ',domcount, ' unique domains (TLDs) hit today.\n'

        # This writes the unique TLDs found to a file along with the count of how many times each was seen
        # It also attempts to match them to a country code and if found lists the country.  If not, it writes 'unknown'

        for key in countrycount:
            #print key
            if key in iana:
                if args.vlevel > 1:print 'true!'
                countrycode = iana[key]
                if args.vlevel > 1:print 'This is the country: ' + countrycode
            else: countrycode = 'unknown'
            if args.vlevel > 0: print str(key) + '\t' + str(countrycount[key]) + '\t' + str(countrycode)
            topcountries.writerow([key, countrycount[key], countrycode])
        output3.close()
        # Then we reopen the file and read it all back in to a list.
        sys.exit()

    checktime = datetime.now()
    if sleep1 > 0:
        print 'sleeping for ', sleep1, ' seconds. Hit ctrl-c to end program and calculate stats.'
        try:
            csvfile.close()
            newcount = 0
            for key in newlist:
                newdoms.writerow([key, newlist[key]])
                newcount += 1
            output4.close()
            print 'There were ' + str(newcount) + ' new domains found and ' + str(badcount) + ' requests to blacklisted domains.\n'
            badcount = 0
            newlist = {}
            for i in range(0,sleep1):
                stdout.write("\r%s" % str(sleep1 - i)+'    ')
                stdout.flush()
                time.sleep(1)
 
        except KeyboardInterrupt:
            # note that if we put the following routine into a def then we can run it when
            # when user does control - c, when sleep1 = 0, or in middle of runs but user does not chose to exit
            print '\n'
            # First we write all the unique FQDNs found to a file along with the count of how many times each was seen
            for key in todaytop10:
                top10today.writerow([key, todaytop10[key]])
            output2.close()
            # Then we reopen the file and read it all back in to a list.
            output2 = open(topd, 'rb')
            top102day = csv.reader(output2)
            list2 = {}
            for line in top102day:
                if line[1] == 'Count': continue
                list2[line[0]] = int(line[1])
            # We then sort that list and print out the top ten from that list
            sortedlist = sorted(list2.items(),key=lambda x: x[1])
            sortedlist.reverse()
            print '\nThese are the top ', args.topdoms, ' domains hit today.\n'
            for x in range(0,int(args.topdoms)+1):
                print sortedlist[x][0], str(sortedlist[x][1])[:-2]
            # I decided not to print all the unique domains one by one.  Just the total because there could be hundreds.
            print
            domcount = len(sortedlist) - 1
            print  '\nThere were ',domcount, ' unique domains (TLDs) hit today.\n'

            # This writes the unique TLDs found to a file along with the count of how many times each was seen
            # It also attempts to match them to a country code and if found lists the country.  If not, it writes 'unknown'
 
            for key in countrycount:
                #print key
                if key in iana:
                    if args.vlevel > 1:print 'true!'
                    countrycode = iana[key]
                    if args.vlevel > 1:print 'This is the country: ' + countrycode
                else: countrycode = 'unknown'
                if args.vlevel > 0: print str(key) + '\t' + str(countrycount[key]) + '\t' + str(countrycode)
                topcountries.writerow([key, countrycount[key], countrycode])
            output3.close()
            # Then we reopen the file and read it all back in to a list.
            output3 = open(topctry, 'rb')
            topcountry2day = csv.reader(output3)
            list1 = {}
 
            # for line in topcountry2day:
                  # if line[1] == 'Count': continue
                  # list1[line[0]] = int(line[1])
            # # We then sort that list and print out the top ten from that list
            # nationsortedlist = sorted(list1.items(),key=lambda x: x[1])  # By value
            # nationsortedlist.reverse()
            # print '\nThese are the top countries or domains hit today.\n'
            # cntcountry = len(nationsortedlist) - 1
            # for x in range(0,cntcountry):
                # print nationsortedlist[x][0], '\t\t', str(nationsortedlist[x][1])#[:-2]
            sys.exit()
        print '\n'
    elif sleep1 == 0 or runtime == 0:  
        print '\n'
        # First we write all the unique FQDNs found to a file along with the count of how many times each was seen
        for key in todaytop10:
            top10today.writerow([key, todaytop10[key]])
        output2.close()
        # Then we reopen the file and read it all back in to a list.
        output2 = open(topd, 'rb')
        top102day = csv.reader(output2)
        list2 = {}
        for line in top102day:
            if line[1] == 'Count': continue
            list2[line[0]] = int(line[1])
        # We then sort that list and print out the top ten from that list
        sortedlist = sorted(list2.items(),key=lambda x: x[1])
        sortedlist.reverse()
        print '\nThese are the top ', args.topdoms, ' domains hit today.\n'
        for x in range(0,int(args.topdoms)+1):
            print sortedlist[x][0], str(sortedlist[x][1])[:-2]
        # I decided not to print all the unique domains one by one.  Just the total because there could be hundreds.
        print
        domcount = len(sortedlist) - 1
        print  '\nThere were ',domcount, ' unique domains (TLDs) hit today.\n'

        # This writes the unique TLDs found to a file along with the count of how many times each was seen
        # It also attempts to match them to a country code and if found lists the country.  If not, it writes 'unknown'
        
        for key in countrycount:
            #print key
            if key in iana:
                if args.vlevel > 1:print 'true!'
                countrycode = iana[key]
                if args.vlevel > 1:print 'This is the country: ' + countrycode
            else: countrycode = 'unknown'
            if args.vlevel > 0: print str(key) + '\t' + str(countrycount[key]) + '\t' + str(countrycode)
            topcountries.writerow([key, countrycount[key], countrycode])
        output3.close()
        # Then we reopen the file and read it all back in to a list.
        # output3 = open(topctry, 'rb')
        # topcountry2day = csv.reader(output3)
        # list1 = {}
        # for line in topcountry2day:
             # if line[1] == 'Count': continue
             # list1[line[0]] = int(line[1])
        # # We then sort that list and print out the top ten from that list
        # nationsortedlist = sorted(list1.items(),key=lambda x: x[1])  # By value
        # nationsortedlist.reverse()
        # print '\nThese are the top countries or domains hit today.\n'
        # cntcountry = len(nationsortedlist) - 1
        # for x in range(0,cntcountry):
            # print nationsortedlist[x][0], '\t\t', str(nationsortedlist[x][1])#[:-2]
        sys.exit()
    else: runtime = runtime - 1
     
## Tie into DHCP rogue check, if a rogue is found have it check to see if the rogue did any dns lookups


