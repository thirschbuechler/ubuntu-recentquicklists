#!/bin/bash
VERSION=V1.2

function get_cfg
{
cp /home/$USER/ubuntu-recentquicklists/urq.conf urq.conf
}


function banner
{
echo ---------------------------------------------
echo --Ubuntu-Recentquicklists $VERSION Update--
echo ---------------------------------------------
}

function update_prompt
{
banner;
echo "Do you wish to update this program?"
echo ""
echo "This assumes you've downloaded+extracted or cloned somewhere,"
echo "and ran this script from the new location"
echo "We will grab the config-file urq.conf,"
echo "after that you can proceed with uninstall.sh, then install.sh"
echo "which installs the new version with the old config-file."
echo ""
echo "(you could as well paste the new version over the old one in your home-dir manually, if you wanted to)"
echo "(just don't forget to restart the thing or logoff+logon if you've configured it to autorun)"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) get_cfg; break;;
        No ) exit;;
    esac
done
}

update_prompt;
