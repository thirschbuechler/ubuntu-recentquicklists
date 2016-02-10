#!/usr/bin/env python
from gi.repository import Unity, Gio, GObject, Dbusmenu, Gtk
import os, subprocess, sys
import configparser

def debugwait():
	input("Press Enter to continue...")

#get recent manager
manager = Gtk.RecentManager.get_default()
print("recentmanager gtk function loaded")

mimetypes = []
mimezsemi = []
appexecs = []
launcherListe = []
mixedlist = []

def isEven(number):
        return number % 2 == 0

#turns a list of strings of multiple elements into a list of all elements
def semiarraytolist(semi):
	liste=[]
	for i in range(len(semi)):
		liste.append(semi[i].split(";"))
	return liste


#get launcher objects (not printable)
def current_launcher():
	get_current = subprocess.check_output(["gsettings", "get", "com.canonical.Unity.Launcher", "favorites"]).decode("utf-8")
	return eval(get_current)

def get_apps():
	apps = []
	appexecslist = []
	mimetypes = []
	curr_launcher = current_launcher()
	for i in range(len(curr_launcher)):		
		if "application://" in curr_launcher[i]:
			#only get apps (there are other items, such as a removable drives spacer, as well)
			curr_launcher[i]=curr_launcher[i].replace("application://","")
			config = configparser.SafeConfigParser()
			config.read("/usr/share/applications/"+curr_launcher[i])
			if config.has_option("Desktop Entry","MimeType"):
				if config.has_option("Desktop Entry","Exec"):
						print(curr_launcher[i])
						apps.append(curr_launcher[i])
						mimetypes.append(config.get("Desktop Entry","MimeType"))
						appexecslist.append(config.get("Desktop Entry","Exec",raw=True))
						#raw=True ignores special characters and imports them "as-is"

			else:
				print(curr_launcher[i] + " has no MimeType- or Exec-Entry and will be omitted")
	return apps,mimetypes,appexecslist
	

def evaluateapps():
	appfiles,mimezsemi,appexecslist=get_apps()
	applaunchers = []
	
	for i in range(len(appfiles)):
		applaunchers.append(Unity.LauncherEntry.get_for_desktop_id(appfiles[i]))

	return applaunchers,mimezsemi,appexecslist

#debugwait()


launcherListe, mimezsemi, appexecs = evaluateapps()

mimetypes=semiarraytolist(mimezsemi)


if not launcherListe:
	print("no Launchers found!??")
if not mimezsemi:
	print("no mimetypes found!??")



#register quicklist
qlListe = []
for i in range(len(launcherListe)):
	qli = Dbusmenu.Menuitem.new()
	qlListe.append(qli)



def contains(liste, item):
	if len(liste) != 0:
		for l in liste:
			if l.match(item) == True :
					return True
	return False

#sort list by modification date (most recent first)
def sort(liste):
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
	global mixedlist
	#remove the %U, %F or whatever of the exec path
	#(string replace command neither likes the % nor its escaped form %%)
	mixedlist.append(location)
	mixedlist.append((appexecs[qlnummer])[:-2]+"\""+location+"\"")
	item = Dbusmenu.Menuitem.new()
	item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, name)
	item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
	#connect the click-handler. it's the same for all entries
	item.connect("item-activated", check_item_activated,location)
	qlListe[qlnummer].child_append(item)	
	



def update():
	print("updating")
	liste = manager.get_items()
	infoListe = []
	
	for i in range(len(mimetypes)):
		infoListe.append([])


	#only use files with a supported mimetype
	for i in liste:
		if i.exists():
			for e in range(len(mimezsemi)):
				listex=[]
				listex=mimezsemi[e].split(";")
	
				for g in range(len(listex)):
					if i.get_mime_type()==listex[g]:
						infoListe[e].append(i)
							

	
				
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
	
	
	#</update()>

#called on gtk_recent_manager "changed"-event
def check_update(a):
	print("gtk recent_manager changed: check_update")
	for i in range(len(qlListe)):
		for c in qlListe[i].get_children():
			qlListe[i].child_delete(c)
	update()
	#</check_update>

#update on startup
update()

#connect the handler
manager.connect("changed",check_update)

for i in range(len(launcherListe)):
			launcherListe[i].set_property("quicklist", qlListe[i])

loop = GObject.MainLoop()

loop.run()
