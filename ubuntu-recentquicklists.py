#!/usr/bin/env python3
##import time
##time.sleep(20) # delay for x seconds
from gi.repository import Unity, Gio, GObject, Dbusmenu, Gtk
import os, subprocess, sys
import configparser
import atexit
from gi.repository import Notify as notify#notification bubble
#notify.init("urq-APPINDICATOR_ID")#APPINDICATOR_ID for bubble notifications
#http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html

#custom logging
import log3
import logging.handlers #logging.WARNING and so on


# --> comment
## --> old/alternative code



#------------------function definitions------------------------
#main() is at the bottom of this script


def mainconfigread():#https://docs.python.org/3/library/configparser.html
	global maxage, onlycritical, startupsplash, shortnagging, verboselogging, showfullpath, maxentriesperlist, resolvesymlinks
	global Path
	config = configparser.SafeConfigParser()
	config.optionxform = lambda opt: opt#reason:
	#https://github.com/earwig/git-repo-updater/commit/51cac2456201a981577fc2cf345a1cf8c11b8b2f
	missingentries = False
	
	g_sections = ["maxage", "onlycritical", "verboselogging", "startupsplash", "shortnagging", "showfullpath", "maxentriesperlist", "resolvesymlinks"]
	g_defaults = ["7",		"True",			"False", 			"True",			"False",		"False",		"10"			,	"False"]
	
	#open the config file
	cfile=Path+'/'+"urq.conf"
	config.read(cfile)

	#if these entries are not existant, create them with default values
	if not config.has_section("General"):
		config.add_section("General")
		missingentries=True

		
	for i in range(len(g_sections)):		
		if not config.has_option("General",g_sections[i]):
			config.set("General",g_sections[i],g_defaults[i])
			missingentries=True


	
	#create missing entries with default values, if there are any
	if missingentries:
		with open(cfile, 'w') as configfile:
			config.write(configfile)

	#now, read stuff (be it the just written defaults if there were none, or actual user settings)
	maxage=config.getint("General","maxage")
	onlycritical=config.getboolean("General","onlycritical")
	verboselogging=config.getboolean("General","verboselogging")
	startupsplash=config.getboolean("General","startupsplash")
	shortnagging=config.getboolean("General","shortnagging")
	showfullpath=config.getboolean("General","showfullpath")
	maxentriesperlist=config.getint("General","maxentriesperlist")
	resolvesymlinks=config.getboolean("General","resolvesymlinks")
	
#</mainconfigread>


class app_config_entry:
	'config entry for each launcher'
    
	def __init__(self):#http://www.tutorialspoint.com/python/python_classes_objects.htm
		self.pinnedfiles = []#http://stackoverflow.com/questions/1680528/how-do-i-avoid-having-python-class-data-shared-among-instances
		self.maxentriesperlist = -1


#</class app_config_entry>


def appconfigread():#https://docs.python.org/3/library/configparser.html
	global Path, appfiles
	global maxentriesperlist
	global customappconfigs, mimetypes

	config = configparser.SafeConfigParser()
	config.optionxform = lambda opt: opt#reason:
	#https://github.com/earwig/git-repo-updater/commit/51cac2456201a981577fc2cf345a1cf8c11b8b2f
	missingentries = False
	
	a_sections = []
	customappconfigs = []
	tmp = []
	
	#open the config file
	cfile=Path+'/'+"urq.conf"
	config.read(cfile)

	
	#create sections for each launcher	
	for i in range(len(appfiles)):		
		customappconfigs.append(app_config_entry());
		if not config.has_section(appfiles[i]):
			config.add_section(appfiles[i])#add the section (but don't add the option if it's missing)
			missingentries=True
		else:#if there is an entry in the config file, pull the settings
			if (config.has_option(appfiles[i],"maxentriesperlist")):
				customappconfigs[i].maxentriesperlist=config.getint(appfiles[i],"maxentriesperlist")
			if (config.has_option(appfiles[i],"pinnedfiles")):
				tmp = []#is a list because semiarraytolist only handles lists
				tmp.append(config.get(appfiles[i],"pinnedfiles",raw=True))
				#raw-->True ignores special characters (%U, %F, ..) and imports them "as-is"
				customappconfigs[i].pinnedfiles=(semiarraytolist(tmp)[0])			
				
		for j in range(len(customappconfigs[i].pinnedfiles)):
			customappconfigs[i].pinnedfiles[j]=os.path.expanduser(customappconfigs[i].pinnedfiles[j])#turn tildes ('~') into absolute paths
		#</forloop j>

		if (customappconfigs[i].maxentriesperlist==-1):#if there was no setting 
			customappconfigs[i].maxentriesperlist=maxentriesperlist #get the general setting
			
	#</forloop i>
	
	
		

	
	#create missing entries with default values, if there are any
	if missingentries:
		with open(cfile, 'w') as configfile:
			config.write(configfile)

#</appconfigread>

def excluded(launcher_x):#https://docs.python.org/3/library/configparser.html
	global Path, appfiles

	config = configparser.SafeConfigParser()
	config.optionxform = lambda opt: opt#reason:
	#https://github.com/earwig/git-repo-updater/commit/51cac2456201a981577fc2cf345a1cf8c11b8b2f
	val = False
	
	#open the config file
	cfile=Path+'/'+"urq.conf"
	config.read(cfile)

	if (config.has_section(launcher_x) and config.has_option(launcher_x,"maxentriesperlist")):
		if (config.getint(launcher_x,"maxentriesperlist")==0):
			val = True
			
	return val

#</excluded>


def savepinnedfiles():
	global Path, appfiles
	global maxentriesperlist
	global customappconfigs, mimetypes

	config = configparser.SafeConfigParser()
	config.optionxform = lambda opt: opt#reason:
	#https://github.com/earwig/git-repo-updater/commit/51cac2456201a981577fc2cf345a1cf8c11b8b2f

	tmp = ""
	
	#open the config file
	cfile=Path+'/'+"urq.conf"
	config.read(cfile)

	
	for i in range(len(appfiles)):
		tmp = ""#for each launcher, collect all the pinned files:
		for file in customappconfigs[i].pinnedfiles:
			if len(file)>0:
					tmp=tmp+";"+file

		if len(tmp)>0:
			config.set(appfiles[i],"pinnedfiles",tmp)
			tmp = ""
			logger.info("saved pinnedfiles of launcher "+appfiles[i])
			
		else:#0 pinnedfiles
			if (config.has_section(appfiles[i]) and config.has_option(appfiles[i],"pinnedfiles")):
				config.remove_option(appfiles[i],"pinnedfiles")
				logger.info("removed all pinnedfiles from launcher "+appfiles[i])
			
	
	cfile=Path+'/'+"urq.conf"
	with open(cfile, 'w') as configfile:#save the configfile
		config.write(configfile)

#</savepinnedfiles>


def criticalx(title,msg=""):#displays bubble and loggs as well
	if (msg==""):#passing only one string triggers..
		msg=title
		title="URQ: Critical Error"
	logger.critical(title+": "+msg)
	notify.Notification.new("<b>"+title+"</b>", msg, None).show()

#</criticalx>
	

def debugwait():
	input("Press Enter to continue...")
def debughere(here):
	logger.info("currently here: "+here)
	print("currently here: "+here)

#</debugfcts>


#on registered exit try to log the occasion
@atexit.register
def goodbye():
	logger.warning('----Exit-----')

#</goodbye>


def isEven(number):
        return number % 2 == 0
#</isEven>


#turns a list of strings of semicolon-seperated elements into a list of all elements 
#only takes a list and turns it into another list! (can't take a string)
def semiarraytolist(semi):
	list=[]
	for i in range(len(semi)):
		list.append(semi[i].split(";"))
		
	return list

#</semiarraytolist>


#get launcher objects (not "print"-able)
def current_launcher():
	#http://askubuntu.com/questions/165147/bash-script-to-add-remove-desktop-launchers-to-unity-launcher
	get_current = subprocess.check_output(["gsettings", "get", "com.canonical.Unity.Launcher", "favorites"]).decode("utf-8")
	return eval(get_current)

#</current_launcher>


def get_apps():
	global seperatorsneeded, logger
	launchers = []#"icons" in taskbar
	appexecslist = []#how the icon opens stuff
	mimetypes = []#which types of stuff an app thinks it can open
	seperatorsneeded = []
	
	curr_launcher = current_launcher()
	for i in range(len(curr_launcher)):		
		if "application://" in curr_launcher[i]:
			#only get apps (there are other items, such as a removable drives, as well)
			#http://askubuntu.com/questions/157281/how-do-i-add-an-icon-to-the-unity-dock-not-drag-and-drop/157288#157288
			curr_launcher[i]=curr_launcher[i].replace("application://","")
			#make kde4 apps work as well, yay!! :
			#change their prefix to a folder, as in /usr/share/applications they have their own folder
			curr_launcher[i]=curr_launcher[i].replace("kde4-","kde4/")
			
			
			config = configparser.SafeConfigParser()
			#folders where the launcher's desktop-files sit
			config.read("/usr/share/applications/"+curr_launcher[i])
			##this ("~/.local/share/applications/"+curr_launcher[i])) should be the user-editable folder for the unity dash,
			##but it always crashes the configload, for every file, so  don't load from there (formatting error?)
						
			if not excluded(curr_launcher[i]):
				if config.has_option("Desktop Entry","MimeType"):
					if config.has_option("Desktop Entry","Exec"):
							logger.warning(curr_launcher[i]+" is a quicklist candidate")
							mimetypes.append(config.get("Desktop Entry","MimeType"))
							#raw-->True ignores special characters (%U, %F, ..) and imports them "as-is"
							appexecslist.append(config.get("Desktop Entry","Exec",raw=True))
							#for adding kde4-stuff it to unity taskbar, that needs to be reset, tough
							curr_launcher[i]=curr_launcher[i].replace("kde4/","kde4-")
							launchers.append(curr_launcher[i])
							if ( config.has_option("Desktop Entry","Actions") or config.has_option("Desktop Entry","X-Ayatana-Desktop-Shortcuts") ):
								seperatorsneeded.append(1)
							else:
								seperatorsneeded.append(0)
					else:
							logger.warning(curr_launcher[i] + " has no Exec-Entry and will be omitted")
							logger.warning("have a look at the github-wiki:compatibility-manual_adding")


				else:
					logger.warning(curr_launcher[i] + " has no MimeType-Entry and will be omitted")
					logger.warning("have a look at the github-wiki:compatibility-manual_adding")
			else:
				logger.warning(curr_launcher[i]+" has been excluded via maxentriesperlist=0")
				
	return launchers,mimetypes,appexecslist

#</get_apps>


def get_conv_apps():
	global launcherList, mimetypes, appexecs, appfiles #appfiles later necessary for appconfigread
	launcherList = []
	mimetypes = []
	launcherList = []
	appexecs = []
	
	
	appfiles,mimetypes,appexecs=get_apps()
	
	mimetypes=semiarraytolist(mimetypes)
	
	
	for i in range(len(appfiles)):
		launcherList.append(Unity.LauncherEntry.get_for_desktop_id(appfiles[i]))
	
	
	for i in range(len(appexecs)):#these replace actions also throw away any possible other arguments,
		appexecs[i]=appexecs[i].replace("%F","%U")#such as the okular "-caption %c" parameter, which isn't used here
		appexecs[i]=appexecs[i].replace("%f","%U")
		appexecs[i]=appexecs[i].replace("%u","%U")
		head, sep, tail = appexecs[i].partition('%U')
		appexecs[i]=head
		
		
	if not launcherList:
		criticalx("Launcher list empty!")
	elif not mimetypes:#if there are launchers but no mimetype-list
		criticalx("Mimetype list empty!")
		
	#values are global so don't need to be returned

#</get_conv_apps>


def contains(list, item):
	if len(list) != 0:
		for l in list:
			if l.match(item) == True :
					return True
	return False

#</contains>


#sort list by modification date (most recent first)
def sort(list):
	lst = list[0]
	geordList = []
	
	ageMax = 0
	for l in list:
		if l.get_modified() >= ageMax:
			ageMax = l.get_modified()
	
	age = ageMax
	for i in range(len(list)):
		for l in list:
			if l.get_modified() >= ageMax:
				if contains(geordList,l) == False:
					ageMax = l.get_modified()
					lst = l
		geordList.append(lst)
		ageMax = 0
		
	return geordList

#</sort>


#this function gets called if something in a quicklist is clicked
def check_item_activated(menuitem, a, location):
#(lookup "pygtk gobject.GObject.connect" to see why this handler looks that way)
	global manager, appexecs, qlList, logger, pinningmode, customappconfigs
	pos = 0
	# menuitem is a Dbusmenu.Menuitem object, it's the entry of the recent file
	for i in range(len(qlList)):
		if (menuitem.get_parent() == qlList[i]):#get its parent, aka the launcher under which it's seated
			pos=i
			break#exit for loop when element found
			
	
	if location.startswith("pinningswitch"):#if the switch between pinningmode and normal (recent-files)mode is pressed
		pinningmode = not pinningmode#turn it on/off
		update()#make the list, but with checkboxes and don't launch anything
		savepinnedfiles()#also, save the pinned files to the config file
				
	elif (pinningmode):#deal with the checkboxes -- this may break unity if acted on non-checkbox-entries, that's why it's an elif
		
		if menuitem.property_get_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE) == Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED:
			#previously active means remove now
			customappconfigs[i].pinnedfiles.remove(location)
			menuitem.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)
			update()#to show changes
		else:#previously inactive means add
			customappconfigs[i].pinnedfiles.append(location)
			menuitem.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)
			update()#to show changes
			
	else:#not pinningswitch: normal recent-files operation, which means call the thing the user has clicked on
			
		if os.path.exists(location):#if there is a file to be opened, open it
			logger.info("exec "+appexecs[pos]+ "\""+ location+"\"")
			process = subprocess.Popen(appexecs[pos]+ "\""+ location+"\"",shell=True)#look up which program to use for this "location" (=path+filename)

		else:#if the thing is gone
			#https://bugzilla.gnome.org/show_bug.cgi?id=137278
			head, tail = os.path.split(location)#tail=filename

			if not shortnagging:#prepare text
				text = "sorry, Gtk Recentmanager doesn't track moved/deleted files. Reopen & close the file to renew its link."
				text = text + "In case it got renamed, that happend now, so go back to the quicklist and try again"
			else:
				text = "(has been renamed/moved/deleted)"

			criticalx("URQ: "+tail+" not found", text)
			##manager.remove_item(location) #it got removed already, so just update the list

			update()
		#</else: gone>
	#</location.startswith pinningswitch>
	
#</check_item_activated>


#create quicklist entry as dbus menu item (not attached to Unity at this point)
def createItem(name, location, qlnummer):
	global qlList, appexecs, logger, pinningmode
	
	item = Dbusmenu.Menuitem.new()
	name=name.replace("_","__")#escape the underscore with a second one, a single one would make an underline
	#this only creates an item with a name, the exec association happens in check_item_activated
	item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, name)
	item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	
	if (pinningmode):
			item.property_set (Dbusmenu.MENUITEM_PROP_TOGGLE_TYPE, Dbusmenu.MENUITEM_TOGGLE_CHECK)#set checkbox properties if in pinning mode
			if location.startswith("pinningswitch"):
				if pinningmode:
					item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)#then it gets a checkmark
				##else:
				##	item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)
				##moved down
				
			else:#if its a recentfiles-entry
				item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)
				for j in range(len(customappconfigs[qlnummer].pinnedfiles)):
					if customappconfigs[qlnummer].pinnedfiles[j].startswith(location):#check if this entry is pinned
						item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)#then it gets a checkmark
					#else:
						#item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)
	elif location.startswith("pinningswitch"):
		item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)
	#<if pinningmode>
		
	#attach event handler "check_item_activated"
	item.connect("item-activated", check_item_activated,location)
	if not qlList[qlnummer].child_append(item)	:
		criticalx("dbusmenu-item %s failed to be created" % name)
	else:
		logger.info("added "+location)

#</createItem>


def update(a=None):
	#called on gtk_recent_manager "changed"-event
	#(lookup "pygtk gobject.GObject.connect" to see why this handler looks that way)
	global maxage, qlList, mimetypes, maxentriesperlist, seperatorsneeded, logger, customappconfigs, resolvesymlinks
	tmp = ""
	pinned=False
		
	#old quicklists have to be deleted before updating, otherwise new items would be appended
	for i in range(len(qlList)):
		for c in qlList[i].get_children():
			qlList[i].child_delete(c)
	
	#add entries if there are too little
	while (len(qlList)<len(launcherList)):
		qlList.append(Dbusmenu.Menuitem.new())
	
	
			
	raw_list = manager.get_items()
	logger.warning("updating, got "+str(len(raw_list))+"unfiltered items")
	RecentFiles = []
	entriesperList = [] #counter per launcher-slot (to make maxentriesperlist happen)
	
	for i in range(len(mimetypes)):
		RecentFiles.append([])#initialize emtpy RecentFiles
		entriesperList.append(0)#and entriesperList


	x=0
	#only use files with a supported mimetype, populate RecentFiles accordingly
	for item in raw_list:
		if item.exists():#prevent deleted/moved/renamed "ghosts" of files showing up
			for e in range(len(mimetypes)):
				for g in range(len(mimetypes[e])):
					if ((item.get_mime_type()==mimetypes[e][g]) and (item.get_age()<(maxage+1))):
						x=x+1
						RecentFiles[e].append(item)
	#</ item in raw_list>	

	
	logger.warning("now, "+str(x)+" items are good to go ")			

	#------------#   add recent files   #------------#
	
	for i in range(len(RecentFiles)):
		if len(RecentFiles[i]) != 0 :#if there are items to be added
			for rf in sort(RecentFiles[i]):
				if (entriesperList[i]<customappconfigs[i].maxentriesperlist):
					pinned=False
					tmp = rf.get_uri_display()#get path
					if resolvesymlinks:
						tmp = os.path.realpath(tmp)
					head, tail = os.path.split(tmp)
						##alternatively: tail=rf.get_short_name ()
					for j in range(len(customappconfigs[i].pinnedfiles)):#see pinned==False
						if customappconfigs[i].pinnedfiles[j]==tmp:
							pinned=True
							
					if (pinned==False):#if this file isn't queued to be pinned later
						
						if not showfullpath:
							createItem(tail, tmp,i)#name, fullpath
						else:
							createItem(tmp, tmp,i)#fullpath, fullpath
						entriesperList[i]=entriesperList[i]+1
				#</if  maxentriesperlist>
			#</rf in RecentFiles>
	#</ i in RecentFiles>	
	
	
	#add pinning seperator
	for i in range(len(RecentFiles)):
		if len(RecentFiles[i]) != 0:
			if (entriesperList[i] != 0):#only add seperator if there are "normal" non-pinned recentfiles above
				##if (customappconfigs[i].pinnedfiles and customappconfigs[i].maxentriesperlist!=0):#if there was no pinning switch this should be checked
				separator = Dbusmenu.Menuitem.new ();
				separator.property_set (Dbusmenu.MENUITEM_PROP_TYPE, Dbusmenu.CLIENT_TYPES_SEPARATOR)
				separator.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
				qlList[i].child_append (separator)
	#</ i in RecentFiles>	
		
		
	#------------#   add pinned files	  #------------#
	
	for i in range(len(customappconfigs)):
		for j in range(len(customappconfigs[i].pinnedfiles)):
			tmp = customappconfigs[i].pinnedfiles[j]
			head, tail = os.path.split(tmp)
			if not showfullpath:
				createItem(tail, head+"/"+tail,i)#name, fullpath
			else:
				createItem(head+"/"+tail, head+"/"+tail,i)#fullpath, fullpath
			entriesperList[i]=entriesperList[i]+1
				
			#</ j in customappconfigs>
	#</ i in customappconfigs>	
	
	#------------#   add pinning switch	  #------------#
	for i in range(len(RecentFiles)):#pinningmode switch
		createItem("[file pinning]", "pinningswitch",i)
	
	
	#add seperators, if the launcher has actions below the files
	for i in range(len(RecentFiles)):
		if len(RecentFiles[i]) != 0:
			if (seperatorsneeded[i]==1 and customappconfigs[i].maxentriesperlist!=0):
				separator = Dbusmenu.Menuitem.new ();
				separator.property_set (Dbusmenu.MENUITEM_PROP_TYPE, Dbusmenu.CLIENT_TYPES_SEPARATOR)
				separator.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
				qlList[i].child_append (separator)
	#</ i in RecentFiles>	
		
#</update>


def reg_ql():#register quicklist
	global launcherList, qlList, manager
	for i in range(len(launcherList)):
		if (customappconfigs[i].maxentriesperlist!=0):
			launcherList[i].set_property("quicklist", qlList[i]) #launcherList entries are Unity.LauncherEntry objects
			
	#connect function "update" as a handler to the signal "changed" (called when gtk's recent files list changes)
	#(lookup "pygtk gobject.GObject.connect")
	manager.connect("changed",update)
#</reg_ql>


#---------------------------------  main  --------------------------------
def main():
	global manager, onlycritical, verboselogging, Path, logger
	global qlList, pinningmode
	#global variables: not the best, but I don't like to write/have a 1000 things in each fct call either..

	Version = "V1.2.2"
	pinningmode=False
	
	notify.init("urq-APPINDICATOR_ID")#APPINDICATOR_ID for bubble notifications
	Path=os.path.dirname(os.path.abspath(__file__))
	mainconfigread()

	logfile=Path+"/"+"urq.out"
	#logging switches
	if (onlycritical):
		logger = log3.setup(logfile,logging.CRITICAL)
	elif (verboselogging):
		logger = log3.setup(logfile,logging.INFO)
	else:
		logger = log3.setup(logfile,logging.WARNING)

	logger.warning("----"+Version+"Start-----")
	if startupsplash:
		notify.Notification.new("<b>URQ</b>", "<b>Ubuntu-recentquicklists "+Version+" startup</b>", None).show()

		
	#terminal info messages
	print("")
	print("Ubuntu-recentquicklists "+Version+" startup")
	print("")
	print("Please ignore possible warnings about requiring certain versions of Unity/Gtk/Notify etc. (which come up when executing the script via terminal), unless the script does nothing.")
	print("In that case, you may need to upgrade these modules or Ubuntu itself (before doing so, manually open and close a document to see whether GTK-recentmanager just got emptied unexpectedly)")
	print(" ")
	print("Configuration & Debugging info (crtl+click): https://github.com/thirschbuechler/ubuntu-recentquicklists/wiki/Configuration-file")
	print("(.. for the current release. Master branch features may only be documented in CHANGELOG.md, however)")


	#https://developer.gnome.org/gtk3/stable/GtkRecentManager.html
	manager = Gtk.RecentManager.get_default()
	if manager:
		logger.info("Gtk Recentmanager loaded")
	else:	
		criticalx("Gtk Recentmanager FAILED to load!!","Abandon Ship!")

		
	get_conv_apps()
	
	appconfigread()
	
	qlList = []
	
	update()

	reg_ql()#append the dbus objects to the unity launcher entries

	logger.warning("all set, entering main loop (wait for changes)")

	loop = GObject.MainLoop()

	loop.run()
	
#</main>


#call main
main()
