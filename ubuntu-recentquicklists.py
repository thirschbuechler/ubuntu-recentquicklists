#!/usr/bin/env python3
##import time
##time.sleep(20) # delay for x seconds
import apt

Version = "V1.2.2.x"
print("")
print("Ubuntu-recentquicklists "+Version+" startup")
print("")
print("loading apt-cache for package-detection..")
cache = apt.Cache()
prerequisites=['python3','gir1.2-rsvg-2.0', 'python3-gi']#gir1.2-rsvg-2.0 makes gi.require_version work
for pkg in prerequisites:
	if not cache[pkg].is_installed:
	    print("try installing %s if the script craps out" %pkg)
	else:
		print("package %s detected" %pkg)
import os, subprocess, sys

#get rid of terminal-startup-garble:
if not 'GI_TYPELIB_PATH' in os.environ:
	full_name = '/usr/lib/girepository-1.0'
	if os.path.exists(full_name):
		print("setting GI_TYPELIB_PATH env var")
		os.environ['GI_TYPELIB_PATH'] = full_name

import gi
gi.require_version('Unity', '7.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

#</get rid of garble>
from gi.repository import Unity, Gio, GObject, Dbusmenu, Gtk
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
#main() is at the very bottom


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


def savepinnedfiles():#customappconfigwrite

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


	for i in range(len(appfiles)):#for each launcher
		tmp = ""
		for file in customappconfigs[i].pinnedfiles:

			if len(file)>0:
					tmp=tmp+";"+file#collect all the pinned files

		if len(tmp)>0:
			config.set(appfiles[i],"pinnedfiles",tmp)

			tmp = ""
			logger.info("saved pinnedfiles of launcher %s" %(appfiles[i]))


		else:#0 pinnedfiles

			if (config.has_section(appfiles[i]) and config.has_option(appfiles[i],"pinnedfiles")):

				config.remove_option(appfiles[i],"pinnedfiles")

				logger.info("launcher %s has 0 pinnedfiles" %appfiles[i])



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
	global otherlauncheractionsexist, logger
	launchers = []#"icons" in taskbar
	appexecslist = []#how the icon opens stuff
	mimetypes = []#which types of stuff an app thinks it can open
	otherlauncheractionsexist = []

	curr_launcher = current_launcher()
	for i in range(len(curr_launcher)):
		if "application://" in curr_launcher[i]:
			#only get apps (there are other items, such as a removable drives, as well)
			#http://askubuntu.com/questions/157281/how-do-i-add-an-icon-to-the-unity-dock-not-drag-and-drop/157288#157288
			curr_launcher[i]=curr_launcher[i].replace("application://","")
			#make kde4 apps work as well, yay!! :
			#change their prefix to a folder, as in /usr/share/applications they have their own folder
			curr_launcher[i]=curr_launcher[i].replace("kde4-","kde4/")


			conffile1="/usr/share/applications/"+curr_launcher[i]
			conffile2="~/.local/share/applications/"+curr_launcher[i]
			conffile2=os.path.expanduser(conffile2)#turn tildes ('~') into absolute paths
			A=os.path.exists(conffile1)
			B=os.path.exists(conffile2)

			if A or B:#one has to exist, decide which one to use
				if A and B:
					logger.warning("two .desktop-files found, using "+conffile2)
					conffile=conffile2
				else:
					conffile=conffile1

				config = configparser.SafeConfigParser()
				#folders where the launcher's desktop-files sit
				config.read(conffile)

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
								if config.has_option("Desktop Entry","Actions") :
									otherlauncheractionsexist.append(1)
								elif config.has_option("Desktop Entry","X-Ayatana-Desktop-Shortcuts"):
									tmp = []#is a list because semiarraytolist only handles lists
									tmp.append(config.get("Desktop Entry","X-Ayatana-Desktop-Shortcuts",raw=True))
									#raw-->True ignores special characters (%U, %F, ..) and imports them "as-is"
									XAyatanaDS = []
									XAyatanaDS = (semiarraytolist(tmp)[0])
									if (XAyatanaDS == ["Screen", "Window"] or XAyatanaDS == ["Window", "Screen"]) :
										otherlauncheractionsexist.append(0)#something like SMPlayer where no additional separator is needed
									else:
										otherlauncheractionsexist.append(1)#separator probably needed

								else:
									otherlauncheractionsexist.append(0)
						#</if: has option desktop-entry exec>
						else:
								logger.warning(curr_launcher[i] + " has no Exec-Entry and will be omitted")
								logger.warning("have a look at the github-wiki:compatibility-manual_adding")

					#</if: has option desktop-entry mimetype>
					else:
						logger.warning(curr_launcher[i] + " has no MimeType-Entry and will be omitted")
						logger.warning("have a look at the github-wiki:compatibility-manual_adding")
				#</if: not excluded>
				else:
					logger.warning(curr_launcher[i]+" has been excluded via maxentriesperlist=0")
			#</if conffile exists>
		#</if "application://" in current_launcher[i]>
	#</for range in current_launcher>
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
	sortedList = []

	ageMax = 0
	for l in list:
		if l.get_modified() >= ageMax:
			ageMax = l.get_modified()

	age = ageMax
	for i in range(len(list)):
		for l in list:
			if l.get_modified() >= ageMax:
				if contains(sortedList,l) == False:
					ageMax = l.get_modified()
					lst = l
		sortedList.append(lst)
		ageMax = 0

	return sortedList

#</sort>


#this function gets called if something in a quicklist is clicked
def check_item_activated(menuitem, a, location):
#(lookup "pygtk gobject.GObject.connect" to see why this handler looks that way)
	global manager, appexecs, qlList, logger, pinningmode, removalmode, customappconfigs, moveup, movedown
	pos = 0
	separator_pos = -1
	# menuitem is a Dbusmenu.Menuitem object, it's the entry of the recent file
	for i in range(len(qlList)):
		if (menuitem.get_parent() == qlList[i]):#get its parent, aka the launcher under which it's seated
			pos=i
			break#exit for loop when element found

	if location.startswith("-"):#determine position of separator
								#since the separator-indexes aren't saved anywhere
		item_pos=int(location)*(-1)#to "remove" the dash

		sep_count=0
		foundit=False
		k=-1
		for pinnedentry in customappconfigs[i].pinnedfiles:

			k=k+1

			if pinnedentry.startswith("-"):
				sep_count=sep_count+1
				if (sep_count==item_pos):
					foundit=True
					break# break the for
		if foundit:
			separator_pos=k
		else:
			separator_pos=-1
	#</if startswith "-">


	if location.startswith("pinningswitch"):#pinningswitch pressed
		if pinningmode:
			pinningmode=False
		else:
			pinningmode=True
			removalmode=False

		#per default, don't go into move-submode
		moveup=False
		movedown=False

		update()#display list with checkboxes, don't launch anything
		savepinnedfiles()#also, save the pinned files to the config file

	#</ if pinningswitch>

	elif location.startswith("removalswitch"):#recentfiles-removalswitch pressed
		if removalmode:
			removalmode=False
		else:
			removalmode=True
			pinningmode=False

		update()#make the list, but with checkboxes and don't launch anything
		#(no saving occours, as only GTK-Recentfiles are managed)
	#</ if removalswitch>


	elif location.startswith("moveup"):#submenu of pinningmode.. pinningmode stays active
		if moveup:
			moveup=False#down already f
		else:
			moveup=True
			movedown=False
		update()
	elif location.startswith("movedown"):#submenu of pinningmode.. pinningmode stays active
		if movedown:
			movedown=False
		else:
			movedown=True
			moveup=False
		update()
	#</moveswitches>


	elif pinningmode and (moveup or movedown):#only works for pinnedfiles, not separators

		try:
			item=location
			if not location.startswith("-"):
				old_index = customappconfigs[i].pinnedfiles.index(item)

			else:
				old_index = separator_pos

			if moveup and old_index>0:
				new_index=old_index-1
			elif movedown and (old_index+1)!=len(customappconfigs[i].pinnedfiles):

				new_index=old_index+1
			else:
				new_index=old_index#don't do anything if the new index would be out-of-bounds

			if not location.startswith("-"):
				customappconfigs[i].pinnedfiles.remove(item)

			else:
				customappconfigs[i].pinnedfiles.pop(separator_pos)

			customappconfigs[i].pinnedfiles.insert(new_index, item)

			#http://stackoverflow.com/questions/3173154/move-an-item-inside-a-list

		except ValueError as v:
			if not location.startswith("separators++"):
				criticalx("can't move a recententry, only pinnedentries: disable moving and pin the file first")
				logger.warning(v)
			pass

		update()
	#</pinningmode and moveup/down>


	elif (pinningmode):#deal with the checkboxes
	#(this may break unity if acted on non-checkbox-entries, that's why it's an elif)

		if menuitem.property_get_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE) == Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED:
			#previously active means remove now

			if separator_pos >-1:#means a separator has been found, and toggled
				customappconfigs[i].pinnedfiles.pop(separator_pos)


			#</ if startswith "-">

			else:#regular file
				customappconfigs[i].pinnedfiles.remove(location)

				#(regular files have unique locations)

			##menuitem.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)
			##does not need to be unchecked since it's gone anyway
			update()#to show changes
		else:#previously inactive means add
			if location=="separators++":
					customappconfigs[i].pinnedfiles.append("-")

			else:
				customappconfigs[i].pinnedfiles.append(location)

				if not location.startswith("-"):#toggle checkmark if it's not a separator
					menuitem.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)

			update()#to show changes

	elif (removalmode):
		URI=""
		raw_list = manager.get_items()

		if resolvesymlinks:
			for item in raw_list:
				if (os.path.realpath(item.get_uri_display())==location):
					URI=item.get_uri()
		else:
			for item in raw_list:
				if (item.get_uri_display()==location):
					URI=item.get_uri()
		#</if-else resolvesymlinks>

		if not (URI==""):
			if Gtk.RecentManager.remove_item(manager,URI):
				update()#to show changes
				logger.info("item "+location+" removed from recent-manager")
			else:#if recent-manager.remove reported "False":
				if os.path.exists(location):
					criticalx("can't remove file","file "+location+" can't be removed from GTK Recentmanager (status:file-exists)")
				else:
					criticalx("can't remove file","file "+location+" can't be removed from GTK Recentmanager (status:file-non-existent)")
			#</if Gtk.Recentmanager>
		else:
			criticalx("can't remove file","file "+location+" can't be removed from GTK Recentmanager (status:no-URI-found)")



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


#create quicklist entry as dbus menu item (not yet attached to Unity)
def createItem(name, location, qlnummer):
	global qlList, appexecs, logger, pinningmode, removalmode, moveup, movedown
	create_checkbox=False
	set_checked=False

	name=name.replace("_","__")#escape the underscore with a second one, a single one would make an underline

	if pinningmode and location.startswith("-"):
		name="---separator---"#display the separator as an entry, so it can be clicked and removed or moved up/down
		set_checked=True

	if (pinningmode):
			create_checkbox=True

			if location.startswith("pinningswitch"):
				#intermission: add these switches
				createItem("[add separator]","separators++",qlnummer)#is inactive, should be added fine when clicked

				#do:   http://stackoverflow.com/questions/3173154/move-an-item-inside-a-list
				createItem("[move up]","moveup",qlnummer)
				createItem("[move down]","movedown",qlnummer)

				#continue, add the pinningswitch, with:
				set_checked=True

			elif location.startswith("moveup") and moveup:
				set_checked=True
			elif location.startswith("movedown") and movedown:
				set_checked=True


			else: #if its a recentfiles-entry or another switch
				if not location.startswith("-"):
					set_checked=False
				for j in range(len(customappconfigs[qlnummer].pinnedfiles)):

					if customappconfigs[qlnummer].pinnedfiles[j].startswith(location):#if this entry is pinned

						set_checked=True
	#<if pinningmode>


	elif (removalmode):
		if location.startswith("removalswitch"):#is checked in removalmode
			create_checkbox=True
			set_checked=True
	#<if removalmode>

	#create the thing
	#(makes an item with a name, the exec association happens in check_item_activated)
	item = Dbusmenu.Menuitem.new()
	item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, name)

	if create_checkbox:
		item.property_set (Dbusmenu.MENUITEM_PROP_TOGGLE_TYPE, Dbusmenu.MENUITEM_TOGGLE_CHECK)#have the checkbox-property
		if set_checked:
			item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)
		else:
			item.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)

	#attach event handler "check_item_activated"
	item.connect("item-activated", check_item_activated,location)
	if not qlList[qlnummer].child_append(item)	:
		criticalx("dbusmenu-item %s failed to be created" % name)
	else:
		logger.info("added "+location)

#</createItem>


def createSeparator(index):
	global qlList
	separator = Dbusmenu.Menuitem.new ();
	separator.property_set (Dbusmenu.MENUITEM_PROP_TYPE, Dbusmenu.CLIENT_TYPES_SEPARATOR)
	separator.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	qlList[index].child_append (separator)
#</createSeparator>


def update(a=None):
	#called on gtk_recent_manager "changed"-event
	#(lookup "pygtk gobject.GObject.connect" to see why this handler looks that way)
	global maxage, qlList, mimetypes, maxentriesperlist, otherlauncheractionsexist, logger, customappconfigs, resolvesymlinks, verboselogging, removalmode
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
		RecentFiles.append([])#initialize empty RecentFiles
		entriesperList.append(0)#and entriesperList


	x=0
	#only use files with a supported mimetype, populate RecentFiles accordingly
	for item in raw_list:
		if verboselogging:
			logger.info("item "+item.get_uri_display()+" is in raw_recentmanager")
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
					for j in range(len(customappconfigs[i].pinnedfiles)):#is this recent file queued to be pinned anyway

						if customappconfigs[i].pinnedfiles[j]==tmp:

							pinned=True

					if (pinned==False):#if not queued then add it

						if not showfullpath:
							createItem(tail, tmp,i)#name, fullpath
						else:
							createItem(tmp, tmp,i)#fullpath, fullpath
						entriesperList[i]=entriesperList[i]+1
				#</if  maxentriesperlist>
			#</rf in RecentFiles>
	#</ i in RecentFiles>


	#add separator between recentfiles and pinnedfiles/switches (if no pinnedfiles)

	for i in range(len(RecentFiles)):
		if len(RecentFiles[i]) != 0 :
			if (entriesperList[i] != 0 ):#only add separator if there are "normal" non-pinned recentfiles above
				##if (customappconfigs[i].pinnedfiles and customappconfigs[i].maxentriesperlist!=0):#if there was no pinning switch this should be checked

				createSeparator(i)
				##createItem("---separator rf-pf/sw---","/asdf",i)#debug-separator
	#</ i in RecentFiles>


	#------------#   add pinned files	  #------------#
	#cleanup empty entries
	for i in range(len(customappconfigs)):
		count=len(customappconfigs[i].pinnedfiles)

		defects=[]
		for j in range(count):
			tmp = customappconfigs[i].pinnedfiles[j]

			if tmp==" " or not tmp:
				defects.append(j)
		for j in range(len(defects)):
			customappconfigs[i].pinnedfiles.pop(j)

	#</cleanup empty entries>

	#add entries
	if not removalmode:
		for i in range(len(customappconfigs)):
			count=len(customappconfigs[i].pinnedfiles)

			seps=0
			for j in range(count):
				tmp = customappconfigs[i].pinnedfiles[j]

				head, tail = os.path.split(tmp)
				if tmp.startswith("-"):#is a pinnedfiles-separator

					if not pinningmode:
						createSeparator(i)
					else:
						seps=seps+1
						#memorizes multiple separator-positions..
						#only concerns separators which separate pinnedfiles from other pinnedfiles

						createItem("-","-%i" %seps,i)
				#</if startswith "-">

				elif not showfullpath:
					createItem(tail, head+"/"+tail,i)#name, fullpath
				else:
					createItem(head+"/"+tail, head+"/"+tail,i)#fullpath, fullpath
				entriesperList[i]=entriesperList[i]+1

				#add separator between pinned files and switches (after last element)
				if (j==count-1) and count>0:
					createSeparator(i)
					##createItem("---separator pf-sw---","/asdf",i)#debug-separator
				#</ j in customappconfigs>
		#</ i in customappconfigs>



	#------------#   add switches	  #------------#

	for i in range(len(RecentFiles)):#pinningmode switch
		createItem("[file pinning]", "pinningswitch",i)
		createItem("[remove recent-entries]", "removalswitch",i)


	#add separator between switches and launcheractions if needed
	for i in range(len(RecentFiles)):
		#if len(RecentFiles[i]) != 0:
			if (otherlauncheractionsexist[i]==1):
				createSeparator(i)
				##createItem("---separator sw-la---","/asdf",i)#debug-separator
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
	global qlList, pinningmode, removalmode, moveup, movedown
	#global variables: not the best, but I don't like to write/have a 1000 params in each fct call either..

	print("entering main()")
	pinningmode=False
	removalmode=False
	moveup=False
	movedown=False

	notify.init("urq-APPINDICATOR_ID")#APPINDICATOR_ID for bubble notifications
	Path=os.path.dirname(os.path.abspath(__file__))
	print("reading config-file..")
	mainconfigread()

	print("setting-up logfile..")
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


	#further terminal info messages
	print(" ")
	print("Configuration & Debugging info (crtl+click): https://github.com/thirschbuechler/ubuntu-recentquicklists/wiki/Configuration-&-Logging")
	print("(.. for the current release. Master branch features may only be documented in CHANGELOG.md, however)")
	print("")
	print("No further terminal output expected on normal operation.. go away ;)")


	#https://developer.gnome.org/gtk3/stable/GtkRecentManager.html
	manager = Gtk.RecentManager.get_default()
	if manager:
		logger.info("Gtk Recentmanager loaded")
	else:
		criticalx("Gtk Recentmanager FAILED to load!!","Abandon Ship!")


	get_conv_apps()#get the launchers, and the associated exec-entries

	appconfigread()

	qlList = []

	update()#get recentfiles and pinnedfiles and make the ql


	reg_ql()#append the dbus objects to the unity launcher entries

	logger.warning("all set, entering main loop (wait for changes)")

	loop = GObject.MainLoop()

	loop.run()

#</main>


#call main
main()
