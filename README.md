# ubuntu-recentquicklists

Finally, there is a recent-files quicklist for ubuntu, as windows already has got for quite some time.
This script adds recent files to the right-click on the unity-dash's launchers (program icons).
No more messing around with the unity menue for the last 30 or so files you've accessed and also have a launcher in your unity bar.

Required: python3

Installation:
see https://github.com/thirschbuechler/ubuntu-recentquicklists/wiki/Installation

Huge thanks to 
https://forum.ubuntuusers.de/topic/libreoffice-unity-dynamische-quicklist/ (german post), which provided the framework to expand the functionality from being limited to libre-office to serve all applications.
Also, stackexchange (in particular stackoverflow) helped a lot.

Autorun:
For running in the background, i'll probably create an init.d script, as proposed here:
http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/


It is crucial to call the script via "python3 script.py", not "python script.py" since it won't work if you don't.
