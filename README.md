ScourDNS
========


This script is provided as is, blah blah blah.

For any questions, comments, suggestions, constructive critiques, please contact me at reswob10@gmail.com

Files needed from download to execute:

analyzednslog.py
country_domain-list.csv
README.md

This script does some basic analysis of the Windows DNS Debug Log.  NOTE: This currently only runs on Windows and was written in Python 2.7x

Currently it only analyzing the DNS requests.  In the future it will analyze the DNS replies and attempt to do some simple correlation.

For optimal results using reqeusts only, please configure you Window DNS Debug log according to:

https://support.appriver.com/KB/a669/enable-dns-request-logging-for-windows-20032008.aspx

NOTE:  I will update this as I modify the script to support replies and requests.

For a full background on using DNS debug logs to assist with monitoring you enterprise for malicious and/or unauthorized behaviour, see the powerpoint presentation and/or the accompanying word document that has notes and links.

--------------------------------------------------------------------

The script needs the following files before it can be run the first time:

masterlist.txt 
	-- Create an empty file with this name.  This is where the script will store all the domains it sees.  The script will refer to this file to determine if it is seeing a new domain

country_domain-list.csv
	-- This file should come with the script.  It contains a list of country codes and TLDs.  The script will use this list to count the number of times each TLD or country was reqeusted via DNS.  This could come in handy if you want to know how many times people in your enterprise are contacting a certain country.  You can edit this list to add your local domains.

The following files are optional:

blacklists
	-- You can have multiple blacklists.  They can be named whatever you want, but they must be text files and can only contain one FQDN per line.  These files contains a list of all FQDNs that are dangerous or verboten.  If the script sees a request to any FQDN contained in one of the blacklist files, it will log the time, IP and FQDN in the 'bad_looks' file.

greylist
	-- This file (and there can be only one) contains FQDNs of domains you want to monitor DNS requests for, but these FQDNs are not necessarily bad.  You may want to use this for correlations.

To prepare for both creating the configuration file and running the script, make sure you have created a mapped drive to each of the locations where you are saving the Windows DNS Debug logs.  For example if the DNS debug log is being saved at \\SERVER\DNS\dns_dbug.txt, then you must do the following:  net use x: \\SERVER\DNS so that you have a valid path to dns_dbug.txt.  Simply pointing to \\SERVER\DNS does not currently work.

Now you are ready to configure the program.  This will provide the script with all the parameters it needs to run.  This only needs to be done once, after that you only need to run the configuration if any of the parameters have changed.

To run the configuration type:  python analyzednslog.py -create

Follow the instructions and enter the parameters as requested.  The script will save all your answers in a file called config.txt.

To review the configuration file, type: python analyednslog.py -config

To run the script, type: python analyednslog.py

This will cause the script to execute once and exit.

By default, the script will review all DNS Debug log entries starting from 1 day prior to the time of execution and review all entries up to the present time.  The script will create a folder named for the day and month of the time of execution and save all output to that folder.  If the folder is already there, the script will simply add to anything currently in the folder.  There will be up to 6 output files:

bad_looks-datetimestamp.csv
	-- This file will have three colums: DATETIME, IP, FQDN.  Each line represents a time that the script has matchs a DNS request to an entry in one of the blacklists.  It is recommended that you note which blacklist each entry comes from and why that domain is on the blacklist so you know the urgency of the alert.  This is probably the file you want to feed into a SIEM.

concerned_looks-datetimestamp.csv
	-- This file will have three colums: DATETIME, IP, FQDN.  Each line represents a time that the script has matchs a DNS request to an entry in one of the greylists.  It is recommended that you note why that domain is on the greylist so you know the urgency of the alert.  

new_domains-datetimestamp.csv
	-- This file will have a list of all the FQDNs never seen before as compared to your master list.  When you run this script for the very first time, this list will be very large as it creates the master list.  The size of the file in subsequent runs will depend on various factors such as the size of your enterprise, how much the users surf, etc

top_domains-datetimestamp.csv
	-- This file will have a list of all the FQDNs seen during the run of the script and a count of how many times each FQDN was requested that day.  

top_countries-datetimestamp.csv
	-- This file will have a list of all the TLDs seen during the run of the script and a count of how many times each FQDN was requested that day.  If the script could not match the TLD to the country code csv, it will label it as unknown.  If you know what those TLDs match to, you can edit the csv file.

error_log-datetimestamp.csv
	-- This file will have errors encountered during the run of the script.  The script SHOULD catch all errors and write them here.  If it does not and crashes, please copy the error code and line and send it to me.


It is important to note that these are only the DNS requests, and as such any entries found in the above files does NOT mean the user and/or machine in question actually connected to the FQDN.  Web content filters, Firewalls, ACLs and other network infrastructure devices or settings may have blocked the connection.  Also, timeouts, bad transmissions and other network issues may have also prevented full connection.  Use entries here as correlation or as data points for investigation, not as 'smoking guns' for finding incidents.

The following options are available when running the script:

-s #
	-- If you want to run the script multiple times and keep a running count, simple use the -s option and provide a number which will represent the number of seconds the script will sleep between runs.  If you use this option, the output directory will have multple bad_looks, new_domains and concerned_looks files but only one each of the top_domains, top_countries and error_log files.  To stop the program, hit ctrl-c and the script will finalize the calculations and close out all files.

-top #
	-- When the program exits, by default, it will desplay the top 10 domains requested during the run.  To change that number, provide the number of your choice.

-bottom # 
	-- not currently used

-test
	--set this switch to tell the program whether or not this is a test run.  No changes to master file are made.

-d #
	-- Number of days in the past to start checking DNS logs.  Default is 1 day.  For example, if you come in on a Monday and want to analyze DNS logs from Saturday - the current time, run the script with -d 3.

-ig
	-- set this switch to ignore tracking web sites.  If you have provided a list of domains that you want to ignore, use this switch to make sure the script does not add them to the master list.  For example, there are several domains that are used as tracking mechanisms such as all FQDNs ending in gstatic.com are FQDNs that Google uses to track user movement across the web.  These FQDNs are numerous and can fill up the master list very quickly.  If you chose to ignore any of these domains, you can add them during configuraion.  They will still be counted for statistical purposes, but not added to the masterlist.

-create
	-- create or update a configuration file.

-config
	-- view a configuration file.

-V
	-- show more detail of what the script is either doing or finding.


As an companion script, there is find_ips.py.

This script will enable you to find all the IP addresses that made a DNS request for a domain.  This check can be done against a full FQDN (e.g. www.sample.com), a domain only (e.g. sample.com) or a TLD (e.g. com).  It will search the complete DNS debug log and create an output file will all hits against the search term you provided.  Future enhancements will give you the ability to search a particular time frame only.  This way the search won't take as long.  








