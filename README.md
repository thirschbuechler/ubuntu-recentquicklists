# ubuntu-recentquicklists

Finally, there is a recent-files quicklist for ubuntu, as windows already has for quite some time.
This script adds recent files to the right-click on the unity-dash's launchers (program icons).

Required: python3

Installation:
open a shell (or crtl+alt+t)
cd ~/
git clone https://github.com/thirschbuechler/ubuntu-recentquicklists.git
python3 "ubuntu-recentquicklists.py" &
exit

make sure to type "exit" instead of closing the shell-window, as the latter would kill the script
(more info: http://unix.stackexchange.com/questions/134924/i-am-using-why-isnt-the-process-running-in-the-background)

Huge thanks to 
https://forum.ubuntuusers.de/topic/libreoffice-unity-dynamische-quicklist/
, which provided the framework to expand the functionality from being limited to libre-office to serve all applications.
Also, stackexchange (in particular stackoverflow) helped a lot.

Autorun
For running in the background, i'll probably create an init.d script, as proposed here:
http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/


It is crucial to call the script via "python3 script.py", not "python script.py" since it won't work if you don't.
