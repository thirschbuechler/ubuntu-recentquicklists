##currently new master-branch features:

####pinnedfiles: files can be pinned via the config file:
- run the script, it generates a config-section for each launcher
- add pinnedfiles = ~/Desktop/file1.txt;/data/file2.txt
- also, the option to set maxentriesperlist for each launcher individually
- restart the script after changing the config file (or log-off and log-on again if you've configured autorun, if you want to)


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
