##currently new master-branch features:
* now requiring gir1.2-rsvg-2.0 !!!
* pinnedfiles now can be moved up/down within the UI
* separators now can be added and removed via the UI
* added package-detection at startup
* now using ~./local dir for .desktop files primarily instead of the /usr one
* added gi-require-statements to reduce terminal-output garbage
* added recent-files removal switch (won't remove pinned files, use the pinningswitch for that)
* (fix: recentfiles-removalmode reported removal-failure on success)
* (recentfiles-removalmode hides pinnedfiles, as they can't be removed there anyway)
* added separator between pinnedfiles and pinningswitch
* filepinning-separator option: In urq.conf, a separator can be added via "-". Example (FILE1, separator, FILE2):
 * pinnedfiles = ;FILE1;-;FILE2

#V1.2.2
* fixed a pinningfile-issue which may prevent pinnedfiles to be saved to config-file
* maxentriesperlist=0 now prevents ubuntu-recentquicklists from overwriting a previously existing dynamic-quicklist on a particular launcher (e.g. on nemo-filemanager)
* fixed a bad comment which prevented new configfile-sections from being created

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
* auto separator rules (no double separators)
* logging file: size restriction
* terminal output info "version not specified"
* notification bubbles for critical errors, just in case (never experienced, though)



#V1.0
first release
