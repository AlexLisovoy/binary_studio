# binary_studio

This app provides a converting files from one format to another. This is demo.

Supported formats:

 - json
 - xml
 - csv


## Installation

 1. Clone this repo
 2. Install requirements
 3. Run syncdb command
 
 
**Installation sequence:**

    git clone git@github.com:AlexLisovoy/binary_studio.git
    cd binary_studio
    pip install -r requirements.txt
    python manage.py syncdb
 
 
## Usage

 Start server:
 
     python manage.py runserver
     
 and go to [link](http://127.0.0.1:8000/):
 
     http://127.0.0.1:8000/


## Requirements

- Python 2.7
- Django 1.6+
- xmltodict 0.9+


## Known limitations

 - app is not designed to convert large files. Max limit - 5 mb.
 - some formats(for example xml) with large attachments can not be correctly converted to other formats (for example csv)
 - this is just demo, it's not ready for use to production :)