# cardmaker

This is a simple cardmaker i made for our homebrew tabletop RPG. It is a simple webserver running locally, allowing you to make and manage your card deck. It uses *sanic+uvloop* to serve http, *airspeed* to render velocity templates and pyYAML to store and parse the cards.

## dependencies:

This requires python 3.6 or newer, and could perhaps be reworked into working with python 3.5.
The required python dependencies are listed in requirements.txt:

    pip install -r requirements.txt

## running the server

If you have a working install of [entr](http://entrproject.org/), then you can start the server running:

    ./dev.sh

This will automatically restart the server any time you write any changes to it.

If can otherwise run the server using

    python server.py

When the server is running, you should be able to access it at [localhost:8000](http://localhost:8000)

## Lisence

This is release under BSD 3-clause license, see the file LICENSE for more information
