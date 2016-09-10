##currently new master-branch features:

####files can be pinned via the config file:
- run the updated script, it generates a config-section for each launcher in urq.conf
- add files this way: "pinnedfiles = ~/Desktop/file1.txt;/data/file2.txt" (separated by semicolon)
- restart the script after changing the config file (or log-off and log-on again if you've configured autorun, if you want to)
 
also, the option to set maxentriesperlist for each launcher is now available
minor fix: filenames' underscores get displayed properly



#V1.1
##fixed:
* config file still showed up in home dir instead of prog dir
* entries always get started by corresponding launcher
* streamlined code, consolidated main()

##added:
* limit number of quicklist entries per list
* auto seperator rules (no double seperators)
* logging file: size restriction
* terminal output info "version not specified"
* notification bubbles for critical errors, just in case (never experienced, though)



#V1.0
first release
