##currently new master-branch features:
* fixed a pinningfile-issue which may prevent pinnedfiles to be saved to config-file
* maxentriesplerist=0 now allows prevents ubuntu-recentquicklists from overwriting a previously existing dynamic-quicklist on a particular launcher (e.g. on nemo-filemanager)

#V1.2.1
 
##added:
- filepinning via menu
- installation and update scripts
- option to set maxentriesperlist individually for each launcher
- option resolvesymlinks (general setting, defaults to False)
 to make quicklists read "The_file" instead of "The_Link_to_the_file"

##fixed:
- filenames' underscores get displayed properly



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

