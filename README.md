# AetherOnePy
![RadionicsBox AetherOnyPy](https://raw.githubusercontent.com/isuretpolos/AetherOnePy/refs/heads/main/py/docs/aetherOnePyBox.jpg)

AetherOnePy is a Web-based Desktop Application, which means the application runs on your computer but uses a web browser as its interface. You can run it on a Raspberry Pi or a PC (Windows, Linux or Mac).

## Install
1) Install Python, from https://python.org/downloads/, Version 3.12.x
2) Install Git, from https://git-scm.com, latest version is fine
3) Create a folder for your AetherOnePy somewhere on you computer
4) Open a shell there and type:
```shell
git clone https://github.com/isuretpolos/AetherOnePy.git
```
5) Inside the AetherOnePy folder run the setup first and finally run the main.py
```shell
python setup.py
python main.py
```

## Start
Just run the main.py if you already runned the setup.py.
```shell
python main.py
```

Some systems don't allow a port below 1024, like for example Windows WSL subsystem (ubuntu). In this case use a different port:

```shell
python main.py --port 7000
```

## Update
For updating you call **git pull** followed by **setup.py** which will download new dependencies.
```shell
git pull
python setup.py
python main.py
```
# Raspberry Pi
Some notes for users installing the application on the Raspberry Pi.

- Raspberry Pi 5 needs extra cable for the Camera. For example the older ones has a broader cable, the new a slim one. Search for a camera cable extension.
- Installation is a little bit more complex than on a Windows PC, but I will write a script taking care of the installation process

Helpful commands
```shell
sudo apt update
sudo apt upgrade
# install pip for package management for python libraries
sudo apt-get install python3-pip
# install a python virtual environment (required by restrictions inside RaspyOS
python -m venv aetherone
cd aetherone
git clone https://github.com/isuretpolos/AetherOnePy.git
cd AetherOnePy
cd py

sudo apt install vim
# now you can edit the hidden file .bashrc and set the alias
vim .bashrc
# now enable the alias for ll (like DIR in Windows)
alias ll='ls -la'
```

# History
- 2024-12-04 SQLlite Database Design
- 2024-05-28 automatic dependency install

# Ideas
- ReactFlow evaluate
- Element Periodic Table as main analysis and then Schuessle Salts, Minerals, Bacteria, Plants, Fungi, Animals and Imponderabilia, in a specific order, with links to the materia medica (textbooks), with additional description of rows and columns and kingdoms, miasma and so on, which also helps to learn homeopathy
- relate the clinical symptoms (Clarke Materia Medica) to the remedy and display it in a way the user immediately recognize the pattern (without having deeper knowledge of homeopathy)
- Open API for connecting different devices ([radionics protocol](https://github.com/isuretpolos/RadionicsProtocol))

# Resources
- https://github.com/Bowserinator/Periodic-Table-JSON/blob/master/PeriodicTableJSON.json
- https://modelviewer.dev/