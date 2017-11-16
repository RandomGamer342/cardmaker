#!/usr/bin/env python3
import sys, os, airspeed, glob
from sanic import Sanic, response
from common import withTemplate, withResource, call
import card
import svg
import config

app = Sanic()

@app.get("/")
async def root(request):
    return response.redirect('/cards/')

@app.get("/cards/")
@app.post("/cards/")
@withTemplate("cards/cardlist.vm")
async def show_cardlist(request, template={}):
    if "action" in request.form and "filename" in request.form:
        with card.open_file(request.form.get("filename")) as c:
            if request.form.get("action") == "increment_stock":
                c.copies_owned = int(c.copies_owned) + 1
            elif request.form.get("action") == "decrement_stock":
                c.copies_owned = int(c.copies_owned) - 1
    cards = card.from_dir(config.carddir)
    
    sorting_key = ""
    if "sort" in request.args:
        sorting_key = request.args["sort"][0]
    if "sort" in request.form:
        sorting_key = request.form["sort"][0]
    
    if sorting_key:
        if sorting_key == "filename":
            cards = sorted(cards, key=lambda x: x.filename.lower())
        elif sorting_key == "cp":
            cards = sorted(cards, key=lambda x: -int(x.cp or 0))
        elif sorting_key == "description":
            cards = sorted(cards, key=lambda x: x.description or "")
        elif sorting_key == "copies":
            cards = sorted(cards, key=lambda x: -int(x.copies_owned))
        elif sorting_key == "title":
            cards = sorted(cards, key=lambda x: x.title.lower())
        elif sorting_key == "tag":
            cards = sorted(cards, key=lambda x: x.tag or "\0")

    filter_key = ""
    if "filter" in request.args:
        filter_key = request.args["filter"][0]
    if "filter" in request.form:
        filter_key = request.form["filter"][0]
    
    if filter_key:
        cards = [i for i in cards if i.tag.lower() == filter_key.lower()]
    
    sum_cp = sum(int(i.copies_owned) * int(i.cp or 0) for i in cards)
    sum_copies = sum(int(i.copies_owned) for i in cards)
    
    return response.html(template["cardlist.vm"].merge(locals()))

@app.get('/cards/creator')
@withTemplate("cards/creator.vm")
async def preview_card(request, template={}):
    if "filename" in request.args:
        initialcard = card.from_file(str(request.args["filename"][0])+".yaml")
    else:
        initialcard = card.Card()
        
        #find vacant fileame:
        i = 1
        while 1:
            if card.is_filename_vacant("card-%s" % str(i).zfill(4)):
                initialcard.filename = "card-%s" % str(i).zfill(4)
                break
            i += 1
        #initialcard.power = ""
        #initialcard.cp = ""
        #initialcard.steps = ""
        #initialcard.effects = ""
        #initialcard.flags = ""
    
    return response.html(template["creator.vm"].merge({"card":initialcard}))

@app.post('/cards/creator')
@withTemplate("cards/creator.vm")
async def preview_card(request, template={}):
    initialcard = card.from_form(request.form)
    
    #find vacant fileame:
    if not initialcard.filename:
        i = 1
        while 1:
            if card.is_filename_vacant("card-%s" % str(i).zfill(4)):
                initialcard.filename = "card-%s" % str(i).zfill(4)
                break
            i += 1
    return response.html(template["creator.vm"].merge({"card":initialcard}))

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
    cards = [card.from_form(request.form)]
    if "save" in request.form:
        card.to_file(cards[0])
        was_saved = True
    if "delete" in request.form:
        card.del_file(cards[0])
        was_deleted = True
    return response.html(template["card.vm"].merge(locals()))

@app.get("/cards/svg")
@withTemplate("cards/svg.vm")
async def svg_list(request, template={}):
    filter = request.args.get("filter")
    page = int(request.args.get("page") or 1)
    current_collection = request.args.get("collection")
    
    collections = svg.list_collections()
    svgs = svg.list_all(current_collection)
    
    if filter:
        svgs = [i for i in svgs if filter in i]
    
    if len(svgs) > page*config.svg_page_size:
        has_next = True
    
    svgs.sort()
    svgs = svgs[(page-1)*config.svg_page_size:page*config.svg_page_size]
    
    return response.html(template["svg.vm"].merge(locals()))

@app.post("/cards/svg")
@withTemplate("cards/svg.vm")
async def svg_add(request, template={}):
    file = request.files.get("file")
    name = request.form.get("name") or file.name
    if name[-4:] == ".svg": name = name[:-4]
    
    svg.store(name, file.body)
    
    uploaded = True
    svgs = svg.list_all()
    return response.html(template["svg.vm"].merge(locals()))

#add static resources (with caching):
for file in glob.iglob(os.path.join(config.resourcedir, "**","*"), recursive=True):
    @call
    def temp():#namespace hack to store filetype
        filetype = file.split('.')[-1]
        if filetype in ("html", "css", "js"):
            route = os.path.relpath(file, config.resourcedir)
            if filetype == "js": filetype = "javascript"
            
            print("Adding static resource", repr(route))
            
            @app.get(f"/{route}")
            @withResource(route)
            async def card_style(request, file={}):
                file = tuple(file.values())[0]
                return response.text(file, headers={"Content-Type": f"text/{filetype}"})

#add svgs:
@app.get(f"/svg/<name>.svg")
async def get_svg(request, name):
    color = request.args.get("color")
    return response.text(svg.get(name, color), headers={"Content-Type": "image/svg+xml"})

@app.get(f"/svg/<collection>/<name>.svg")
async def get_svg(request, collection, name):
    color = request.args.get("color")
    return response.text(svg.get(os.path.join(collection, name), color), headers={"Content-Type": "image/svg+xml"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    print("Exiting...\n")
