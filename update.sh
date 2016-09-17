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
echo "(This will grab the config-file urq.conf,"
echo "after that you can proceed with unistall.sh, then install.sh"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) get_cfg; break;;
        No ) exit;;
    esac
done
}

update_prompt;
