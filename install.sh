#!/bin/bash
VERSION=V1.2

function install
{
cp -r . /home/$USER/ubuntu-recentquicklists #copy everything from the current folder there
autorun_prompt;
}  

function make_autorun
{
echo [Desktop Entry] >>ubuntu-recentquicklists.py.desktop
echo Type=Application >>ubuntu-recentquicklists.py.desktop
echo Exec=/home/$USER/ubuntu-recentquicklists/ubuntu-recentquicklists.py >>ubuntu-recentquicklists.py.desktop
echo Hidden=false >>ubuntu-recentquicklists.py.desktop
echo NoDisplay=false >>ubuntu-recentquicklists.py.desktop
echo X-GNOME-Autostart-enabled=true >>ubuntu-recentquicklists.py.desktop
echo Name[en_US]=urq >>ubuntu-recentquicklists.py.desktop
echo Name=urq >>ubuntu-recentquicklists.py.desktop
echo Comment[en_US]=makes quicklists of recent files >>ubuntu-recentquicklists.py.desktop
echo Comment=makes quicklists of recent files >>ubuntu-recentquicklists.py.desktop

echo "link file created"
cp ubuntu-recentquicklists.py.desktop /home/$USER/.config/autostart/ubuntu-recentquicklists.py.desktop
echo "autorun entry added"
echo ""
echo "you may now delete this temporary folder"

bye;
}

function banner
{
echo ---------------------------------------------
echo --Ubuntu-Recentquicklists $VERSION Installation--
echo ---------------------------------------------
}

function install_prompt
{
banner;
echo "Do you wish to install this program?"
echo "Make sure to run this script from the extracted folder,"
echo "don't just open it inside the archive manager"
echo "(This copies everything in here to ~/ubuntu-recentquicklists/)"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install; break;;
        No ) run_now;;
    esac
done
}

function autorun_prompt
{
echo "Do you wish to make it autorun?"
echo "That creates a .desktop file in ~/.config/autostart"
echo "Can also be manipulated via the Ubuntu app  \"Startup-Applications\""
echo "or typing \"gnome-session-properties\" in the terminal"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) make_autorun; break;;
        No ) exit;;
    esac
done
}

function run_now
{
echo "Do you wish to run the script without installing?"
echo "(inside this very folder. script will close when terminal closed)"
echo "no sudo required, but it needs to be executable"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) ./ubuntu-recentquicklists.py break;;
        No ) exit;;
    esac
done
}

function bye
{
echo "now, just log off and on again to see it start,"
echo "(also displays a notification bubble on startup)"
select y in "Yes" ; do
    case $yn in
        Yes ) exit;;
    esac
done
}


install_prompt;
