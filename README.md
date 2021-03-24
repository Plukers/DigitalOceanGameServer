# Server hosting script for Digital Ocean and Factorio

## Using the script
The script uses python.

Install the newest version of python on your PC.
Download the repo and unzip it. Create a virtual environment in the root folder.

on Windows
`py -m venv env`


`venv` will create a virtual Python installation in the `env` folder.

Activate the virtual environment
You may want to enable powershell to activate scripts use:
`set-executionpolicy remotesigned`

Then use this
On Windows:

`.\env\Scripts\activate`

Check if the virtual envirnment is activated:

On Windows:

```where python
.../env/bin/python.exe``` 

As long as your virtual environment is activated pip will install packages into that specific environment and you’ll be able to import and use packages in your Python application.
To leave the environment run:
`deactivate`

To install all requirements you can use

`python3 -m pip install -r requirements.txt`