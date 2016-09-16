#!/bin/bash
VERSION=V1.2

function uninstall
{
rm -r -f /home/$USER/ubuntu-recentquicklists
}  

function del_autorun
{
rm -f /home/$USER/.config/autostart/ubuntu-recentquicklists.py.desktop
echo "autorun entry deleted"
echo ""
}

function banner
{
echo ---------------------------------------------
echo --Ubuntu-Recentquicklists $VERSION Installation--
echo ---------------------------------------------
}

function uninstall_prompt
{
banner;
echo "Do you wish to uninstall this program or disable its autorun?"
echo "(Make sure to run this script from another folder for total"
echo "removal: Copy it to Desktop or somewhere else and run from there,"
echo " delete it afterwards"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) uninstall; break;;
        No ) exit;;
    esac
done
}

function autorun_prompt
{
echo "Do you wish to delete the autorun entry?"
echo "(in ~/.config/autostart)"
echo "Can also be manipulated via the Ubuntu-app \"Startup-Applications\""
echo "or by typing \"gnome-session-properties\" in the terminal"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) del_autorun; break;;
        No ) uninstall_prompt;;
    esac
done
}


autorun_prompt;
