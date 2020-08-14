#!/usr/bin/env bash

REPO_URI=https://github.com/katharinekurz/epu-covid-memo.git
REPO_DIR=$HOME/covid-memo

ENTRYPOINT=countydata.py

# install homebrew
echo "[*] installing homebrew..."
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# install python
echo "[*] installing python3..."
brew install python@3.8

# install requests, xlwt
echo "[*] install dependencies..."
pip3 install -U requests xlwt

# cloning repository
rm -rf $REPO_DIR
git clone $REPO_URI $REPO_DIR

# run the script
echo "[*] running script..."
cd $REPO_DIR
python3 $ENTRYPOINT

files=`ls`

echo
echo "[*] successfully ran the script..."
echo
echo "[!] headfile.xls has been generated"
echo "current directory:"
echo
echo "$files"

# open directory and generated excel sheet
open .
open headfile.xls\