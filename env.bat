rmdir /s /q env
py -m venv env
Call .\env\Scripts\activate.bat
python -m pip install -r requirements.txt
cmd \k