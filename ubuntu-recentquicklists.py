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


# --> comment
## --> old/alternative code


#custom logging
import log3
import logging.handlers #logging.WARNING and so on


#------------------function definitions------------------------
#main is at the bottom of this script


def configread():#https://docs.python.org/3/library/configparser.html
	global maxage, onlycritical, startupsplash, shortnagging, verboselogging, showfullpath, maxentriesperlist
	global Path
	config = configparser.SafeConfigParser()
	config.optionxform = lambda opt: opt#reason:
	#https://github.com/earwig/git-repo-updater/commit/51cac2456201a981577fc2cf345a1cf8c11b8b2f
	missingentries=False
	
	
	#open the config file
	cfile=Path+'/'+"urq.conf"
	config.read(cfile)

	#if these entries are not existant, create them with default values
	if not config.has_section("General"):
		config.add_section("General")
		missingentries=True

	if not config.has_option("General","maxage"):
		config.set("General","maxage","7")
		missingentries=True

	if not config.has_option("General","onlycritical"):
		config.set("General","onlycritical","True")	
		missingentries=True
		
	if not config.has_option("General","verboselogging"):
		config.set("General","verboselogging","False")
		missingentries=True
		
	if not config.has_option("General","startupsplash"):
		config.set("General","startupsplash","True")	
		missingentries=True
		
	if not config.has_option("General","shortnagging"):
		config.set("General","shortnagging","False")
		missingentries=True
		
	if not config.has_option("General","showfullpath"):
		config.set("General","showfullpath","False")
		missingentries=True
		
	if not config.has_option("General","maxentriesperlist"):
		config.set("General","maxentriesperlist","10")
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
	
#</configread>


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


#turns a list of strings of multiple elements into a list of all elements (semikolon-seperated)
def semiarraytolist(semi):
	list=[]
	for i in range(len(semi)):
		list.append(semi[i].split(";"))
	return list

#</semiarraytolist>


#get launcher objects (not printable)
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

	
	curr_launcher = current_launcher()
	for i in range(len(curr_launcher)):		
		if "application://" in curr_launcher[i]:
			#only get apps (there are other items, such as a removable drives spacer, as well)
			#because stuff has this format:
			#http://askubuntu.com/questions/157281/how-do-i-add-an-icon-to-the-unity-dock-not-drag-and-drop/157288#157288
			curr_launcher[i]=curr_launcher[i].replace("application://","")
			#make kde4 apps work as well, yay!!
			#change its prefix to a folder, as in usr/share/applications it has its folder
			curr_launcher[i]=curr_launcher[i].replace("kde4-","kde4/")
			
			
			config = configparser.SafeConfigParser()
			#in the following folder the actual desktop-files sit (which are queried for the exec &mimetype, anyway)
			config.read("/usr/share/applications/"+curr_launcher[i])
			if config.has_option("Desktop Entry","MimeType"):
				if config.has_option("Desktop Entry","Exec"):
						logger.warning(curr_launcher[i])
						mimetypes.append(config.get("Desktop Entry","MimeType"))
						#raw-->True ignores special characters and imports them "as-is"
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

				
	return launchers,mimetypes,appexecslist

#</get_apps>


def get_conv_apps():
	appfiles,mimetypes_raw,appexecslist=get_apps()
	applaunchers = []
	mimetypes = []
	
	for i in range(len(appfiles)):
		applaunchers.append(Unity.LauncherEntry.get_for_desktop_id(appfiles[i]))

	mimetypes=semiarraytolist(mimetypes_raw)
	
	
	for i in range(len(appexecslist)):#these replace actions also throw away any possible other arguments,
		appexecslist[i]=appexecslist[i].replace("%F","%U")#such as the okular "-caption %c" parameter, which isn't used here
		appexecslist[i]=appexecslist[i].replace("%f","%U")
		appexecslist[i]=appexecslist[i].replace("%u","%U")
		head, sep, tail = appexecslist[i].partition('%U')
		appexecslist[i]=head
		
	return applaunchers,mimetypes,appexecslist

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
	info = list[0]
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
					info = l
		geordList.append(info)
		ageMax = 0
		
	return geordList

#</sort>


#this function gets called if something in a quicklist is clicked
def check_item_activated(menuitem, a, location):
#(lookup "pygtk gobject.GObject.connect" to see why this handler looks that way)
	global manager, appexecs, qlList, logger
	pos = 0
	
	# menuitem is a Dbusmenu.Menuitem object, it's the entry of the recent file
	for i in range(len(qlList)):
		if (menuitem.get_parent() == qlList[i]):#get its parent, aka the launcher under which it's seated
			pos=i
			break#exit for loop
			
			
	if os.path.exists(location):
		logger.info("exec "+appexecs[pos]+ "\""+ location+"\"")
		process = subprocess.Popen(appexecs[pos]+ "\""+ location+"\"",shell=True)#look up which program to use for this "location" (=path+filename)
	else:#if what you wanted to open is gone
		#https://bugzilla.gnome.org/show_bug.cgi?id=137278
		head, tail = os.path.split(location)#tail=filename
		if not shortnagging:
			text = "sorry, Gtk Recentmanager doesn't track moved/deleted files. Reopen & close the file to renew its link."
			text = text + "In case it got renamed, that happend now, so go back to the quicklist and try again"
		else:
			text = "(has been renamed/moved/deleted)"
			##notify.Notification.new("<b>URQ: "+tail+" not found</b>", "(has been renamed/moved/deleted)", None).show()
			##"<b>URQ: File not found</b>"
		criticalx("URQ: "+tail+" not found", text)
		##logger.warning("File not found: "+location)
		##manager.remove_item(location) #it got removed already, so just update the list
		check_update()

#</check_item_activated>


#create quicklist entry as dbus menu item, not yet attached to Unity
def createItem(name, location, qlnummer):
	global qlList, appexecs, logger
	
	item = Dbusmenu.Menuitem.new()
	#this only creates an item with a name, the exec association happens in check_item_activated
	item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, name)
	item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	#attach event handler "check_item_activated"
	item.connect("item-activated", check_item_activated,location)
	if not qlList[qlnummer].child_append(item)	:
		logger.warning("dbusmenu-item %s failed to be created, quicklist can't be created!" % name)
	else:
		logger.info("added "+location)

#</createItem>


def update():
	global maxage, qlList, mimetypes, maxentriesperlist, seperatorsneeded, logger
	list = manager.get_items()
	logger.warning("updating, i've got "+str(len(list))+"unfiltered items")
	infoList = []
	entriesperList = [] #counter per launcher slot (to make maxentriesperlist happen)
	
	for i in range(len(mimetypes)):
		infoList.append([])#initialize infoList
		entriesperList.append(0)#and entriesperList


	x=0
	#only use files with a supported mimetype, populate infoList accordingly
	for i in list:
		if i.exists():#prevent deleted/moved/renamed "ghosts" of files showing up
			for e in range(len(mimetypes)):
				for g in range(len(mimetypes[e])):
					if ((i.get_mime_type()==mimetypes[e][g]) and (i.get_age()<(maxage+1))):
						x=x+1
						infoList[e].append(i)
	#</ i in list>	

	
	logger.warning("now, "+str(x)+" items are good to go ")			

	#create empty list
	#for i in range((len(infoList))):

	
	for i in range(len(infoList)):
		if len(infoList[i]) != 0 :#if there are items to be added
			for info in sort(infoList[i]):
				if (entriesperList[i]<maxentriesperlist):
					head, tail = os.path.split(info.get_uri_display())
					##alternatively: tail=info.get_short_name ()
					if not showfullpath:
						createItem(tail, head+"/"+tail,i)#name, fullpath
					else:
						createItem(head+"/"+tail, head+"/"+tail,i)#fullpath, fullpath
					entriesperList[i]=entriesperList[i]+1
				#</if maxage, maxentriesperlist>
			#</info in infoList>
	#</ i in infoList>	
	
	
	
	#add seperators
	for i in range(len(infoList)):
		if len(infoList[i]) != 0:#only add seperator if there are recent files for this launcher
			if (seperatorsneeded[i]==1):
				separator = Dbusmenu.Menuitem.new ();
				separator.property_set (Dbusmenu.MENUITEM_PROP_TYPE, Dbusmenu.CLIENT_TYPES_SEPARATOR)
				separator.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
				qlList[i].child_append (separator)
				
#</update>


#called on gtk_recent_manager "changed"-event
def check_update(a=None):
	#per definition, the a parameter has to be here, altough unused
	#(lookup "pygtk gobject.GObject.connect" to see why this handler looks that way)

	##initialize_launchers()#on filechanges a new/rem. launcher gets recognized
	##make_ql()#and the quicklist gets generated
	##manager.connect("changed",check_update)#and connected
	##that, however, doesn't work (beyond 1-3clicks) and results in the quicklist not executing anything
	##maybe relaunch script itself, out of itself?


	#old quicklists have to be deleted before updating, otherwise new items would be appended
	for i in range(len(qlList)):
		for c in qlList[i].get_children():
			qlList[i].child_delete(c)
	update()
	
#</check_update>


def initialize_launchers():
	global launcherList, appexecs, mimetypes, qlList

	launcherList, mimetypes, appexecs = get_conv_apps()


	if not launcherList:
		criticalx("no Launchers found!")
	if not mimetypes:
		criticalx("no Mimetypes found!")



	#register quicklist
	qlList = []
	for i in range(len(launcherList)):
		qlList.append(Dbusmenu.Menuitem.new())

#</initialize_launchers()>


def make_ql():
	global launcherList, qlList
	for i in range(len(launcherList)):
			launcherList[i].set_property("quicklist", qlList[i]) #launcherList entries are Unity.LauncherEntry objects
	
#</make_ql>


#--------------------------------- main --------------------------------
def main():
	global mimetypes, appexecs, launcherList, seperatorsneeded, manager
	global onlycritical, verboselogging, Path, logger
	#global variables: not the nicest, but i don't want to write a 1000 things into each fct call either..

	
	mimetypes = []#which types of stuff an app thinks it can open
	appexecs = []#how the taskbar-icon opens stuff
	launcherList = []
	seperatorsneeded = []

	
	notify.init("urq-APPINDICATOR_ID")#APPINDICATOR_ID for bubble notifications
	Path=os.path.dirname(os.path.abspath(__file__))
	configread()

	#logging switches
	if (onlycritical):
		logger = log3.setup(Path+"/"+"ubuntu-recentquicklists.out",logging.CRITICAL)
	elif (verboselogging):
		logger = log3.setup(Path+"/"+"ubuntu-recentquicklists.out",logging.INFO)
	else:
		logger = log3.setup(Path+"/"+"ubuntu-recentquicklists.out",logging.WARNING)

	logger.warning("----Start-----")
	if startupsplash:
		notify.Notification.new("<b>URQ</b>", "<b>Ubuntu-recentquicklists startup</b>", None).show()

		
	#terminal info messages
	print("")
	print("Please ignore possible warnings about requiring certain versions of Unity/Gtk/Notify etc. (which come up when executing the script via terminal), unless the script does nothing.")
	print("In that case, you may need to upgrade these modules or Ubuntu itself (before, manually open and close a document to see whether the recentmanager just got emptied unexpectedly)")
	print(" ")
	print("Configuration & Debugging info (crtl+click): https://github.com/thirschbuechler/ubuntu-recentquicklists/wiki/Configuration-file")


	#https://developer.gnome.org/gtk3/stable/GtkRecentManager.html
	manager = Gtk.RecentManager.get_default()
	if manager:
		logger.info("Gtk recentmanager loaded")
	else:	
		criticalx("Gtk recentmanager FAILED to load!!","Abandon Ship!")


	initialize_launchers()

	#update on startup
	update()

	#connect the handler "check_update" to the signal "changed" (called when gtk's recent files list changes)
	#(lookup "pygtk gobject.GObject.connect")
	manager.connect("changed",check_update)

	make_ql()#turn the dbus objects into unity launcher entries

	logger.warning("all set, entering main loop (wait for changes)")

	loop = GObject.MainLoop()

	loop.run()
	
#</main>


#call main
main()
