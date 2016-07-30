#!/usr/bin/env python3
##import time
##time.sleep(20) # delay for x seconds
from gi.repository import Unity, Gio, GObject, Dbusmenu, Gtk
import os, subprocess, sys
import configparser
import atexit
from gi.repository import Notify as notify#notification bubble


# --> comment
## --> old/alternative code



#custom logging
import log
##username=''
##LOG_PATH = '/home/'+username+'/logs/'
##LOG_PATH = '/var/log/' #file here needs to be manually created and chown respectively
#what the hell, just log in the same folder the script is in..
Path=os.path.dirname(os.path.realpath(__file__))


print("")
print("Please ignore possible warnings about requiring certain versions of Unity/Gtk/Notify etc. (which come up when executing the script via terminal), unless the script does nothing.")
print("In that case, you may need to upgrade these modules or Ubuntu itself (before, manually open and close a document to see whether the recentmanager just got emptied unexpectedly)")
print(" ")
print("Configuration & Debugging info (crtl+click): https://github.com/thirschbuechler/ubuntu-recentquicklists/wiki/Configuration-file")


def configread():#https://docs.python.org/3/library/configparser.html
	global maxage, onlycritical, startupsplash, shortnagging, verboselogging, showfullpath, maxentriesperlist
	global Path
	config = configparser.SafeConfigParser()
	config.optionxform = lambda opt: opt#reason:
	#https://github.com/earwig/git-repo-updater/commit/51cac2456201a981577fc2cf345a1cf8c11b8b2f

	
	
	#open the config file
	config.read(Path+'/'+"urq.conf")

	#if these entries are not existant, create them with default values
	if not config.has_section("General"):
		config.add_section("General")

	if not config.has_option("General","maxage"):
		config.set("General","maxage","7")

	if not config.has_option("General","onlycritical"):
		config.set("General","onlycritical","True")	

	if not config.has_option("General","verboselogging"):
		config.set("General","verboselogging","False")

	if not config.has_option("General","startupsplash"):
		config.set("General","startupsplash","True")	

	if not config.has_option("General","shortnagging"):
		config.set("General","shortnagging","False")

	if not config.has_option("General","showfullpath"):
		config.set("General","showfullpath","False")

	if not config.has_option("General","maxentriesperlist"):
		config.set("General","maxentriesperlist","10")

	#create missing entries with default values, if there are any
	with open('urq.conf', 'w') as configfile:
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

##def debugwait():
##	input("Press Enter to continue...")



#--------------------bootstrapping----------------------------------

configread()


log.verbose(verboselogging)#also display debug messages, if false: up to warning level
log.onlycritical(onlycritical)#turn general logging on or off, yes this has to sit below "verbose"

log.set_logpath(Path+'/')#here goes..
log.create('ubuntu-recentquicklists.out')#..the logfile
log.logging.warning('----Start-----')

#on registered exit try to log the occasion
@atexit.register
def goodbye():
	log.logging.warning('----Exit-----')
	#</goodbye>

#https://developer.gnome.org/gtk3/stable/GtkRecentManager.html
manager = Gtk.RecentManager.get_default()
if manager:
	log.logging.info("Gtk recentmanager loaded")
else:	
	log.logging.critical("Gtk recentmanager FAILED to load!!")


#global variables: horrible, but i don't want to write a 1000 things into each fct call either..

entriesperList = [] #counter to make maxentriesperlist happen, per launcher slot
mimetypes = []#which types of stuff an app thinks it can open
mimetypes_raw = []
appexecs = []#how the taskbar-icon opens stuff
launcherList = []
mixedlist = []#the click on a recent-item needs to know its associated application,
#it contains both (being constructed in createItem)

notify.init("urq-APPINDICATOR_ID")#APPINDICATOR_ID for bubble notifications
#http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html
if startupsplash:
	notify.Notification.new("<b>URQ</b>", "<b>Ubuntu-recentquicklists startup</b>", None).show()


#------------------function definitions------------------------

##def debughere(here):
##	log.logging.info("currently here: "+here)
	##</debughere>

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
	get_current = subprocess.check_output(["gsettings", "get", "com.canonical.Unity.Launcher", "favorites"]).decode("utf-8")
	return eval(get_current)
	#</current_launcher>

def get_apps():
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
			#here, we need to change its prefix to a folder, as in usr/share/applications it has its folder
			curr_launcher[i]=curr_launcher[i].replace("kde4-","kde4/")
			
			config = configparser.SafeConfigParser()
			#in the following folder the actual desktop-files sit (which are queried for the exec &mimetype, anyway)
			config.read("/usr/share/applications/"+curr_launcher[i])
			if config.has_option("Desktop Entry","MimeType"):
				if config.has_option("Desktop Entry","Exec"):
						log.logging.warning(curr_launcher[i])
						mimetypes.append(config.get("Desktop Entry","MimeType"))
						#raw-->True ignores special characters and imports them "as-is"
						appexecslist.append(config.get("Desktop Entry","Exec",raw=True))
						#for adding kde4-stuff it to unity taskbar, that needs to be reset, tough
						curr_launcher[i]=curr_launcher[i].replace("kde4/","kde4-")
						launchers.append(curr_launcher[i])
				else:
						log.logging.warning(curr_launcher[i] + " has no Exec-Entry and will be omitted")
						log.logging.warning("have a look at the github-wiki:compatibility-manual_adding")
						

			else:
				log.logging.warning(curr_launcher[i] + " has no MimeType-Entry and will be omitted")
				log.logging.warning("have a look at the github-wiki:compatibility-manual_adding")

	return launchers,mimetypes,appexecslist
	#</get_apps>

def get_conv_apps():
	appfiles,mimetypes_raw,appexecslist=get_apps()
	applaunchers = []
	
	for i in range(len(appfiles)):
		applaunchers.append(Unity.LauncherEntry.get_for_desktop_id(appfiles[i]))

	return applaunchers,mimetypes_raw,appexecslist
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

def returnapplication(location):
	global mixedlist
	for i in range(len(mixedlist)):#lazy search
		if isEven(i):
			if mixedlist[i]==location:
				return (i)
				#mixedlist contains the "location"=path+filename, and after that entry the associated app
	#</returnapplication>

#this function gets called if something in our quicklist is clicked
def check_item_activated(menuitem, a, location):#afaik, the def of these arguments cannot be changed (everytime I tried it stopped working)
	global mixedlist, manager
	if os.path.exists(location):#look up which program to use for this "location" (=path+filename), its the element after where the file itself lies in mixedlist
		process = subprocess.Popen(mixedlist[returnapplication(location)+1],shell=True)
	else:#if what you wanted to open is gone
		#https://bugzilla.gnome.org/show_bug.cgi?id=137278
		if not shortnagging:		
			text = "sorry, Gtk Recentmanager doesn't track moved/deleted files. Reopen & close the file to renew its link."
			text = text + "In case it got renamed, that happend now, so go back to the quicklist and try again"
			notify.Notification.new("<b>URQ: File not found</b>", text, None).show()
		else:
			notify.Notification.new("<b>URQ: File not found</b>", "(has been renamed/moved/deleted)", None).show()

		log.logging.warning("File not found: "+location)
		##manager.remove_item(location) #it got removed already, so just update the list
		check_update_real()
		#a renamed file however shows up in new list??
	#</check_item_activated>

#create quicklist entry
def createItem(name, location, qlnummer):
	global mixedlist, qlList
	
	mixedlist.append(location)
	log.logging.info(location)
	##log.logging.info(appexecs[qlnummer])
	##the slash is used to escape the quotes (") meaning they are part of a string not end of a string 
	##mixedlist.append((appexecs[qlnummer])[:-2]+"\""+location+"\"") doesn't work for kde4
	##(string replace command neither likes the % nor its escaped form %%)
	
	#some make sure every exec-line is uniform and uses %U
	appexecs[qlnummer]=appexecs[qlnummer].replace("%F","%U")
	head, sep, tail = appexecs[qlnummer].partition('%U')
	mixedlist.append(head+"\""+location+"\"")
	##appexecs[qlnummer]=(head+"\""+location+"\"")#mixedlist required to find its associated exec directive

	item = Dbusmenu.Menuitem.new()
	#this only creates an item with a name, the exec association and stuff happens in check_item_activated
	item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, name)
	item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	#connect the click-handler. it's the same for all entries
	item.connect("item-activated", check_item_activated,location)
	if not qlList[qlnummer].child_append(item)	:
		log.logging.warning("dbusmenu-item %s failed to be created, quicklist can't be created!" % name)
	
	
	log.logging.info("added "+location)
	#</createItem>

def update():
	global maxage, qlList, mimetypes, mimetypes_raw
	list = manager.get_items()
	log.logging.warning("updating, i've got "+str(len(list))+"unfiltered items")
	infoList = []
	
	for i in range(len(mimetypes)):
		infoList.append([])


	#only use files with a supported mimetype
	for i in list:
		if i.exists():#<--omitting that would allow deleted files to show up all the time
			for e in range(len(mimetypes_raw)):
				listx=[]
				listx=mimetypes_raw[e].split(";")
	
				for g in range(len(listx)):
					if i.get_mime_type()==listx[g]:
						infoList[e].append(i)
							

	
	##log.logging.warning(str(len(infoList))+" launchers have been identified")
	
	x=0
	for y in range(len(infoList)):			
		x=x+len(infoList[y])
	log.logging.warning("now, "+str(x)+" items are good to go ")			


	#create empty list
	for i in range((len(infoList))+1):
		#if len(infoList[i]) != 0 :
			entriesperList.append(0)


	for i in range(len(infoList)):
		if len(infoList[i]) != 0 :
			for info in sort(infoList[i]):
				if ( (info.get_age()<maxage) and (entriesperList[i]<maxentriesperlist) ):
					head, tail = os.path.split(info.get_uri_display())
					##alternatively: tail=info.get_short_name ()
					if not showfullpath:
						createItem(tail, head+"/"+tail,i)
					else:
						createItem(head+"/"+tail, head+"/"+tail,i)
					entriesperList[i]=entriesperList[i]+1
			

	#add seperators
	for i in range(len(infoList)):
		if len(infoList[i]) != 0:
			separator = Dbusmenu.Menuitem.new ();
			separator.property_set (Dbusmenu.MENUITEM_PROP_TYPE, Dbusmenu.CLIENT_TYPES_SEPARATOR)
			separator.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
			qlList[i].child_append (separator)
	
	
	#</update>


def check_update_real():
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
	#</check_update_real>


#called on gtk_recent_manager "changed"-event, the "a" parameter is a bit mysterious
def check_update(a):
	check_update_real()
	#</check_update>




def initialize_launchers():
	global launcherList, mimetypes_raw, appexecs, mimetypes, qlList


	launcherList, mimetypes_raw, appexecs = get_conv_apps()

	mimetypes=semiarraytolist(mimetypes_raw)#turn the bulk comma-seperated mess into an actual list


	if not launcherList:
		log.logging.critical("no Launchers found!??")
	if not mimetypes_raw:
		log.logging.critical("no Mimetypes found!??")



	#register quicklist
	qlList = []
	for i in range(len(launcherList)):
		qli = Dbusmenu.Menuitem.new()
		qlList.append(qli)
	#</initialize_launchers()>

def make_ql():
	global launcherList, qlList
	for i in range(len(launcherList)):
			launcherList[i].set_property("quicklist", qlList[i])
	#</make_ql>

#--------------------------------- (further) main commands--------------------------------

#debugwait()

initialize_launchers()

#update on startup
update()

#connect the handler
manager.connect("changed",check_update)

make_ql()

log.logging.warning("all set, entering main loop (wait for changes)")

loop = GObject.MainLoop()

loop.run()
