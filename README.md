# ubuntu-recentquicklists

Finally, there is a recent-files quicklist for ubuntu, as windows already has for quite some time.
This script adds recent files to the right-click on the unity-dash's launchers (program icons).

Required: python3

Usage: python3 "ubuntu-recentquicklists.py" &

Huge thanks to 
https://forum.ubuntuusers.de/topic/libreoffice-unity-dynamische-quicklist/
, which provided the framework to expand the functionality from being limited to libre-office to serve all applications.


Autorun
For running in the background, i'll probably create an init.d script, as proposed here:
http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

It is crucial to call the script via "python3 script.py", not "python script.py" since it won't work if you don't.
