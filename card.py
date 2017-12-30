#!/usr/bin/env python3
import glob, os
from yaml import load, dump
from common import Model
import config
from figure import Figure

class Card(Model):
    filename = ""#filename without extentions
    title = "title"
    figure = ["code"]
    figure_source = "material-icons"
    figure_parsed = []
        #material-icons = https://material.io/icons/
        #mdi            = https://materialdesignicons.com/
        #fa             = http://fontawesome.io/icons/
        #svg            = the svgs/ folder
    description = ""
    steps = []
    effects = []
    cost = ""
    stats = {}
    power = None
    cp = None
    gp = None#gold
    flags = []
    notes = ""#not shown, but used to keep track of things
    copies_owned = 1
    tag = ""
    
    def has_flag(self, flag):
        return flag.lower() in map(lambda x: x.lower(), self.flags)

    # def parse_figures(self):
    #     parsed = []
    #     for line in self.figure:
    #         line = line.split(",")
    #         fig = {"filename": line[0], "top":0, "bottom":0, "left":0, "right":0}
    #         if len(line) > 1:
    #             for key, val in [[y.strip() for y in x.split(":")] for x in line]:
    #                 if key.lower() in ("top", "bottom", "left", "right"):
    #                     val = float(val)
    #                 fig[key] = val
    #
    #         l = 0
    #         r = 0
    #         t = 0
    #         b = 0
    #         s = 100
    #
    #         s = s - fig["top"] - fig["bottom"]
    #         l += (fig["top"] + fig["bottom"]) / 2
    #         r += (fig["top"] + fig["bottom"]) / 2
    #
    #         if fig["left"] <= r:
    #             r -= fig["left"]
    #         else:
    #             temp = fig["left"] - r
    #             r = 0
    #             s -= temp
    #             t += temp / 2
    #             b += temp / 2
    #
    #         if fig["right"] <= l:
    #             l -= fig["right"]
    #         else:
    #             temp = fig["right"] - l
    #             l = 0
    #             s -= temp / 2
    #             t += temp / 2
    #             b += temp / 2
    #
    #
    #         fig["left"] += l
    #         fig["right"] += r
    #         fig["top"] += t
    #         fig["bottom"] += b
    #
    #         parsed.append(fig)
    #     self.figure_parsed = parsed


#todo: make the relevant ones into coroutines:

def from_file(filename, in_carddir=True):#yaml syntax
    if filename[-5:] != ".yaml":
        filename += ".yaml"
    name = ".".join(os.path.basename(filename).split(".")[:-1])
    with open(os.path.join(config.carddir, filename) if in_carddir else filename, "r") as f:
        return from_yaml(f.read(), name)

def to_file(card, in_carddir=True):
    assert card.filename, "no filename set"
    filename = card.filename+".yaml"
    
    with open(os.path.join(config.carddir, filename) if in_carddir else filename, "w") as f:
        f.write(to_yaml(card))

def del_file(card, in_carddir=True):
    assert card.filename, "no filename set"
    filename = card.filename+".yaml"
    os.remove(os.path.join(config.carddir, filename) if in_carddir else filename)

def from_yaml(data, filename="from_yaml"):
    card = Card()
    card.filename = filename
    for key, val in load(data).items():
        setattr(card, key, val)
        if key == "figure":
            setattr(card, "figure_parsed", [Figure(line) for line in val])
    return card

def to_yaml(card):
    out = {}
    for key in dir(card):
        if "_" not in key[0] and key not in ("filename", "has_flag", "figure_parsed"):
            val = getattr(card, key)
            if (val or val==0) and val != getattr(Card, key):
                out[key] = val
    return dump(out, default_flow_style=False)

def from_dir(path):
    return [from_file(i, in_carddir=False) for i in glob.glob(os.path.join(path, "*.yaml"))]

def from_form(form):#sanic's request.form
    card = Card()
    for key, val in form.items():
        print(key, ",", val)
        if not val[0]: continue
        if key in ("save", "delete"): continue
        if type(getattr(Card, key)) in (tuple, list):
            if len(val) == 1 and "\n" in val[0]:
                val = val[0].strip().replace("\r\n", "\n").split("\n")
                #val = [i for i in val if i]
            setattr(card, key, val)
        elif type(getattr(Card, key)) is dict:
            if len(val) == 1 and "\n" in val[0]:
                val = val[0].strip().replace("\r\n", "\n").split("\n")
            val = dict([[y.strip() for y in x.split(":")] for x in val])
            setattr(card, key, val)
        else:
            setattr(card, key, val[0].strip().replace("\r\n", "\n"))
    setattr(card, "figure_parsed", [Figure(line) for line in getattr(card, "figure")])
    return card

def is_filename_vacant(filename, in_carddir=True):
    if in_carddir:
        filename = os.path.join(config.carddir, filename)
    if filename[-5:] != ".yaml":
        filename += ".yaml"
    return not os.path.exists(filename)

def get_vacant_filename():
    i = 1
    while 1:
        if is_filename_vacant("card-%s" % str(i).zfill(4)):
            return "card-%s" % str(i).zfill(4)
        i += 1

class open_file:#contextmanager
    def __init__(self, filename):
        self.filename = filename
    def __enter__(self):
        self.card = from_file(self.filename)
        return self.card
    def __exit__(self, *args):
        to_file(self.card)