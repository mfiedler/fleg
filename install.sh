#!/bin/bash

echo 'Installing FLEG...'

mkdir ~/.FLEG
sudo mkdir /usr/share/FLEG
sudo cp FLEG.py /usr/share/FLEG
sudo cp icon.png /usr/share/FLEG
cp history.fleg ~/.FLEG
cp logo.pdf ~/.FLEG

cp FLEG.desktop ~/.local/share/applications 

echo 'Done!'

exit 0
