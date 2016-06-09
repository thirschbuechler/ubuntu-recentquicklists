#!/usr/bin/env python3
#import time
#time.sleep(20) # delays for x seconds
from gi.repository import Unity, Gio, GObject, Dbusmenu, Gtk
import os, subprocess, sys
import configparser
import atexit



#custom logging
import log

def debugwait():
	input("Press Enter to continue...")

log.verbose(False)
#verbose would include "info"-logging
log.create('ubuntu-recentquicklists')
log.logging.warning('----Start-----')

#on registered exit try to log it:
@atexit.register
def goodbye():
	log.logging.warning('----Exit-----')

#get recent manager
manager = Gtk.RecentManager.get_default()
if manager:
	log.logging.warning("recentmanager gtk module loaded")
else:	
	log.logging.error("recentmanager gtk FAIL on load!!")


#lists are all very weird, but i'm to lazy to change them 
mimetypes = []
mimezsemi = []
appexecs = []
launcherListe = []
mixedlist = []


#------------------function definitions

def isEven(number):
        return number % 2 == 0

#turns a list of strings of multiple elements into a list of all elements
def semiarraytolist(semi):
	#log.logging.info("in function semiarraytolist")
	liste=[]
	for i in range(len(semi)):
		liste.append(semi[i].split(";"))
	return liste


#get launcher objects (not printable)
def current_launcher():
	#log.logging.info("in function getcurrentlauncher")
	get_current = subprocess.check_output(["gsettings", "get", "com.canonical.Unity.Launcher", "favorites"]).decode("utf-8")
	return eval(get_current)

def get_apps():
	#log.logging.info("in function getapps")
	apps = []
	appexecslist = []
	mimetypes = []
	curr_launcher = current_launcher()
	for i in range(len(curr_launcher)):		
		if "application://" in curr_launcher[i]:
			#only get apps (there are other items, such as a removable drives spacer, as well)
			#because stuff has this format http://askubuntu.com/questions/157281/how-do-i-add-an-icon-to-the-unity-dock-not-drag-and-drop/157288#157288
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
						#raw=True ignores special characters and imports them "as-is"
						appexecslist.append(config.get("Desktop Entry","Exec",raw=True))
						#for adding kde4-stuff it to unity taskbar, that needs to be reset, tough
						curr_launcher[i]=curr_launcher[i].replace("kde4/","kde4-")
						apps.append(curr_launcher[i])
				else:
						log.logging.warning(curr_launcher[i] + " has no Exec-Entry and will be omitted")
						log.logging.warning("have a look at the github-wiki:compatibility-manual_adding")
						

			else:
				log.logging.warning(curr_launcher[i] + " has no MimeType-Entry and will be omitted")
				log.logging.warning("have a look at the github-wiki:compatibility-manual_adding")

	return apps,mimetypes,appexecslist
	

def evaluateapps():
	#log.logging.info("in function evaluateapps")
	appfiles,mimezsemi,appexecslist=get_apps()
	applaunchers = []
	
	for i in range(len(appfiles)):
		applaunchers.append(Unity.LauncherEntry.get_for_desktop_id(appfiles[i]))

	return applaunchers,mimezsemi,appexecslist







def contains(liste, item):
	if len(liste) != 0:
		for l in liste:
			if l.match(item) == True :
					return True
	return False

#sort list by modification date (most recent first)
def sort(liste):
	#log.logging.info("in function sort")
	info = liste[0]
	geordListe = []
	
	ageMax = 0
	for l in liste:
		if l.get_modified() >= ageMax:
			ageMax = l.get_modified()
	
	age = ageMax
	for i in range(len(liste)):
		for l in liste:
			if l.get_modified() >= ageMax:
				if contains(geordListe,l) == False:
					ageMax = l.get_modified()
					info = l
		geordListe.append(info)
		ageMax = 0
		
	return geordListe
			

def returnapplication(location):
	#log.logging.info("in function returnapplication")
	global mixedlist
	for i in range(len(mixedlist)):
		
		if isEven(i):
			if mixedlist[i]==location:
				return (i)

#this function gets called if something in our quicklist is clicked
def check_item_activated(menuitem, a, location):#afaik, the def of these arguments cannot be changed
	global mixedlist
	process = subprocess.Popen(mixedlist[returnapplication(location)+1],shell=True)
	


#create quicklist entry
def createItem(name, location, qlnummer):
	#log.logging.info("in function createitem")
	global mixedlist
	#remove the %U, %F or whatever of the exec path
	#(string replace command neither likes the % nor its escaped form %%)
	mixedlist.append(location)
	log.logging.info(location)
	#log.logging.info(appexecs[qlnummer])
	#the slash is used to escape the quotes (") meaning they are part of a string not end of a string 
	#mixedlist.append((appexecs[qlnummer])[:-2]+"\""+location+"\"") doesn't work for kde4
	
	#some make sure every exec-line is uniform and uses %U
	appexecs[qlnummer]=appexecs[qlnummer].replace("%F","%U")
	head, sep, tail = appexecs[qlnummer].partition('%U')
	mixedlist.append(head+"\""+location+"\"")

	item = Dbusmenu.Menuitem.new()
	item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, name)
	item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	#connect the click-handler. it's the same for all entries
	item.connect("item-activated", check_item_activated,location)
	if not qlListe[qlnummer].child_append(item)	:
		log.logging.info("no dbusmenu-item was created, quicklist can't be created!")
	
	
	log.logging.info("added "+location)
	#</createItem>

def update():
	liste = manager.get_items()
	log.logging.warning("updating, i've got "+str(len(liste))+"unfiltered items")
	infoListe = []
	
	for i in range(len(mimetypes)):
		infoListe.append([])


	#only use files with a supported mimetype
	for i in liste:
		if i.exists():#omitting that would allow deleted files to show up all the time
			for e in range(len(mimezsemi)):
				listex=[]
				listex=mimezsemi[e].split(";")
	
				for g in range(len(listex)):
					if i.get_mime_type()==listex[g]:
						infoListe[e].append(i)
							

	
	#log.logging.warning(str(len(infoListe))+" launchers have been identified")
	#
	x=0
	for y in range(len(infoListe)):			
		x=x+len(infoListe[y])
	log.logging.warning("now, "+str(x)+" items are good to go ")			
	#remove deleted documents
	#issue: no call from the system if something is deleted, only when recent files changed
	for i in range(len(infoListe)):
		if len(infoListe[i]) != 0 :
			for info in sort(infoListe[i]):
				createItem(info.get_uri_display(),info.get_uri_display(),i)
			

	#add seperators
	for i in range(len(infoListe)):
		if len(infoListe[i]) != 0:
			separator = Dbusmenu.Menuitem.new ();
			separator.property_set (Dbusmenu.MENUITEM_PROP_TYPE, Dbusmenu.CLIENT_TYPES_SEPARATOR)
			separator.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
			qlListe[i].child_append (separator)
	
	
	#</update>

#called on gtk_recent_manager "changed"-event
def check_update(a):
	#initialize_launchers()#on filechanges a new/rem. launcher gets recognized
	#make_ql()#and the quicklist gets generated
	#manager.connect("changed",check_update)#and connected
	#that, however, doesn't work (beyond 1-3clicks) and results in the quicklist not executing anything
	#maybe relaunch script itself, out of itself?

	for i in range(len(qlListe)):
		for c in qlListe[i].get_children():
			qlListe[i].child_delete(c)
	update()
	#</check_update>




def initialize_launchers():
	global launcherListe, mimezsemi, appexecs, mimetypes, qlListe


	launcherListe, mimezsemi, appexecs = evaluateapps()

	mimetypes=semiarraytolist(mimezsemi)


	if not launcherListe:
		log.logging.warning("no Launchers found!??")
	if not mimezsemi:
		log.logging.warning("no mimetypes found!??")



	#register quicklist
	qlListe = []
	for i in range(len(launcherListe)):
		qli = Dbusmenu.Menuitem.new()
		qlListe.append(qli)
	#</initialize_launchers()>

def make_ql():
	global launcherListe, qlListe
	for i in range(len(launcherListe)):
			launcherListe[i].set_property("quicklist", qlListe[i])

#--------------------------------- main commands

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
