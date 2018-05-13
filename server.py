#!/usr/bin/env python3
import sys, os, airspeed, glob, json
from sanic import Sanic, response
from common import mergeTemplate, withResource, call
import card
import colorscheme
import svg
import img
import config

app = Sanic()

@app.get("/")
async def root(request):
    return response.redirect('/cards/')

@app.get("/cards/")
@app.post("/cards/")
@mergeTemplate("cards/cardlist.vm")
async def show_cardlist(request):
    if "action" in request.form and "filename" in request.form:
        with card.open_file(request.form.get("filename")) as c:
            if request.form.get("action") == "increment_stock":
                c.copies_owned = int(c.copies_owned) + 1
            elif request.form.get("action") == "decrement_stock":
                c.copies_owned = int(c.copies_owned) - 1
    cards = card.from_dir(config.carddir)

    write_cookies = {}
    delete_cookies = []

    if "removefilter" in request.args:
        delete_cookies.append("filter")

    filter_keys = []
    if "removefilter" not in request.args:
        if "filter" in request.args:
            filter_keys = [x.lower() for x in request.args["filter"]]
        if "filter" in request.cookies:
            if not filter_keys:
                filter_keys = json.loads(request.cookies.get("filter"))
            elif filter_keys != json.loads(request.cookies.get("filter")):
                write_cookies["filter"] = json.dumps(filter_keys)
        elif filter_keys:
            write_cookies["filter"] = json.dumps(filter_keys)

    if filter_keys:
        cards = [c for c in cards if c.has_tags(filter_keys)]

    sorting_key = ""
    if "sort" in request.args:
        sorting_key = request.args["sort"][0]
    if "sort" in request.cookies:
        if not sorting_key:
            sorting_key = request.cookies.get("sort")
        elif sorting_key != request.cookies.get("sort"):
            write_cookies["sort"] = sorting_key
    elif sorting_key:
        write_cookies["sort"] = sorting_key

    if sorting_key:
        reverse = False
        if sorting_key.endswith("asc"):
            reverse = True
            sorting_key = sorting_key[:-3]
        if sorting_key.startswith("filename"):
            cards = sorted(cards, key=lambda x: x.filename.lower(), reverse=reverse)
        elif sorting_key == "cp":
            cards = sorted(cards, key=lambda x: -int(x.cp or 0), reverse=reverse)
        elif sorting_key == "description":
            cards = sorted(cards, key=lambda x: x.description or "", reverse=reverse)
        elif sorting_key == "copies":
            cards = sorted(cards, key=lambda x: -int(x.copies_owned), reverse=reverse)
        elif sorting_key == "title":
            cards = sorted(cards, key=lambda x: x.title.lower(), reverse=reverse)
        elif sorting_key == "tags":
            cards = sorted(cards, key=lambda x: sorted(map(lambda t: t.lower(), x.tags)) if x.tags else ["\0"], reverse=reverse)
            if filter_keys:
                def order_tags(card):
                    if len(filter_keys) == len(card.tags):
                        return ["\0"]
                    else:
                        return [t for t in card.tags if t.lower() not in filter_keys]
                cards = sorted(cards, key=lambda x: order_tags(x))
        if reverse:
            sorting_key += "asc"

    sum_cp = sum(int(i.copies_owned) * int(i.cp or 0) for i in cards)
    sum_copies = sum(int(i.copies_owned) for i in cards)

    return locals()

@app.get('/cards/creator')
@mergeTemplate("cards/creator.vm")
async def show_creator(request):
    if "filename" in request.args:
        initialcard = card.from_file(str(request.args["filename"][0])+".yaml")
    else:
        initialcard = card.Card()
        initialcard.filename = card.get_vacant_filename()
        #initialcard.power = ""
        #initialcard.cp = ""
        #initialcard.steps = ""
        #initialcard.effects = ""
        #initialcard.flags = ""
    
    return {"card":initialcard}

@app.post('/cards/creator')
@mergeTemplate("cards/creator.vm")
async def show_creator(request):#not used atm
    initialcard = card.from_form(request.form)
    
    #find vacant fileame:
    if not initialcard.filename:
        initialcard.filename = card.get_vacant_filename()
    
    return {"card":initialcard}

@app.get('/cards/show')
@mergeTemplate("cards/card.vm")
async def show_cards(request):
    cards = []
    if "card" in request.args:
        for i in request.args["card"]:
            if "/" in i or "\\" in i: return response.redirect('/cards/')
            c = card.from_file(i+".yaml")
            for _ in range(abs(c.copies_owned)):
                cards.append(c)
    elif "stock" in request.args:
        for i in card.from_dir(config.carddir):
            cards.extend([i]*int(i.copies_owned))
    else:  
        return response.redirect('/cards/')
    return locals()

@app.post('/cards/preview')
@mergeTemplate("cards/card.vm")
async def preview_card(request):
    cards = [card.from_form(request.form)]
    if "save" in request.form:
        if not cards[0].filename:
            cards[0].filename = card.get_vacant_filename()
        card.to_file(cards[0])
        was_saved = True
    if "delete" in request.form:
        card.del_file(cards[0])
        was_deleted = True
    return locals()

@app.get("/cards/colors")
@mergeTemplate("cards/colors.vm")
async def get_color_picker(request):
    colorschemes = colorscheme.list_all()
    print(colorschemes)
    return locals()

@app.get("/card/colors/preview")
@mergeTemplate("cards/card.vm")
async def get_color_preview(request):
    cards = [card.Card()]
    cards[0].colorscheme = request.args.get(schemename) or ""
    cards[0].title = cards[0].colorscheme or "Default Colors"
    cards[0].figure = ""
    cards[0].figure_source = ""
    cards[0].description = "This is a description"
    cards[0].steps = ["Do A", "Then B"]
    cards[0].cost = "Something"
    cards[0].power = 5
    cards[0].cp = 50
    
    return locals()

@app.post("/card/colors/preview")
@mergeTemplate("cards/card.vm")
async def get_color_preview(request):
    cards = [card.Card()]
    cards[0].colorscheme = request.args.get(schemename) or ""
    cards[0].title = cards[0].colorscheme or "Default Colors"
    cards[0].figure = ""
    cards[0].figure_source = ""
    cards[0].description = "This is a description"
    cards[0].steps = ["Do A", "Then B"]
    cards[0].cost = "Something"
    cards[0].power = 5
    cards[0].cp = 50
    
    return locals()


@app.get("/cards/svg")
@mergeTemplate("cards/svg.vm")
async def svg_list(request):
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
    
    return locals()

@app.post("/cards/svg")
@mergeTemplate("cards/svg.vm")
async def svg_add(request):
    file = request.files.get("file")
    name = request.form.get("name") or file.name
    if name[-4:] == ".svg": name = name[:-4]
    
    page = 1
    current_collection = None
    collections = svg.list_collections()
    filter = None
    
    svg.store(name, file.body)
    
    uploaded = True
    svgs = svg.list_all()
    return locals()

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
            async def card_style(request, file):
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

#add images:
@app.get(f"/img/<name>.png")
async def get_img(request, name):
    return response.raw(img.get(f"{name}", "png"), headers={"Content-Type": f"image/png"})

@app.get(f"/img/<collection>/<name>.png")
async def get_img(request, collection, name):
    return response.raw(img.get(os.path.join(collection, name), "png"), headers={"Content-Type": f"image/png"})

@app.get(f"/img/<name>.jpg")
async def get_img(request, name):
    return response.raw(img.get(f"{name}", "jpg"), headers={"Content-Type": f"image/jpeg"})

@app.get(f"/img/<collection>/<name>.jpg")
async def get_img(request, collection, name):
    return response.raw(img.get(os.path.join(collection, name), "jpg"), headers={"Content-Type": f"image/jpeg"})

@app.get(f"/img/<name>.gif")
async def get_img(request, name):
    return response.raw(img.get(f"{name}", "gif"), headers={"Content-Type": f"image/gif"})

@app.get(f"/img/<collection>/<name>.gif")
async def get_img(request, collection, name):
    return response.raw(img.get(os.path.join(collection, name), "gif"), headers={"Content-Type": f"image/gif"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    print("Exiting...\n")
