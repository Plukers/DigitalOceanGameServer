# Server hosting script for Digital Ocean and Factorio
This script hosts a Droplet on Digital Ocean and starts a factorio docker server and automatically loads a specific savegame. This script can be easily modified to run other docker servers.

## Using the script
The script uses python.

Install the newest version of python on your PC.
Download the repo and unzip it. Create a virtual environment in the root folder.

on Windows
`py -m venv env`


`venv` will create a virtual Python installation in the `env` folder.

Activate the virtual environment.
You may want to enable powershell to run scripts:
`set-executionpolicy remotesigned`

Then use this
On Windows:

`.\env\Scripts\Activate.ps1`

As long as your virtual environment is activated pip will install packages into that specific environment and you’ll be able to import and use packages in your Python application. If you change or close the console the environment will be automatically deactivated. 

To install all requirements you can use

`python3 -m pip install -r requirements.txt`

Now you only need to run the script:

`python main.py`

For more information regarding virtual environments look up:
https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
