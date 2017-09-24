#!/usr/bin/env python3
import sys, os, airspeed, glob
from sanic import Sanic, response
from common import withTemplate, withResource
import card
import config

app = Sanic()

@app.get("/")
async def root(request):
    return response.redirect('/cards/')

@app.get("/cards/")
@withTemplate("cards/cardlist.vm")
async def show_cardlist(request, template={}):
    cards = card.from_dir(config.carddir)

    return response.html(template["cardlist.vm"].merge(locals()))

@app.get('/cards/creator')
@withTemplate("cards/creator.vm")
async def preview_card(request, template={}):
    return response.html(template["creator.vm"].merge(locals()))

@app.get('/cards/show')
@withTemplate("cards/card.vm")
async def show_cards(request, template={}):
    if "card" not in request.args:
        return response.redirect('/cards/')

    cards = []
    for i in request.args["card"]:
        if "/" in i or "\\" in i:
            return response.redirect('/cards/')
        cards.append(card.from_file(i+".yaml"))
    return response.html(template["card.vm"].merge(locals()))

@app.post('/cards/preview')
@withTemplate("cards/card.vm")
async def preview_card(request, template={}):
    cards = [card.Card()]

    for key, val in request.form.items():
        if not val[0]: continue
        if type(getattr(card.Card, key)) in (tuple, list):
            setattr(cards[0], key, val)
        else:
            setattr(cards[0], key, val[0])

    return response.html(template["card.vm"].merge(locals()))

#add static files:
for i in glob.iglob(os.path.join(config.resourcedir, "**","*"), recursive=True):
    if i.split(".")[-1] in ("html", "css", "js"):
        i = os.path.relpath(i, config.resourcedir)
        print(i)
        @app.get(f"/{i}")
        @withResource(i)
        async def card_style(request, file={}):
            return response.text(tuple(file.values())[0], headers={"Content-Type": f"text/{i.split('.')[-1]}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
