#!/usr/bin/env python3
import glob, os
from yaml import load, dump
from common import Model
import config

class Card(Model):
    filename = "[[filename_without_file_extention]]"
    title = "[[title]]"
    figure = "code"#https://material.io/icons/
    description = "[[description]]"
    steps = []
    effects = []
    cost = "free action"
    power = None
    cp = None
    flags = []

    def has_flag(self, flag): return flag in self.flags

def from_file(filename, in_carddir=True):#yaml syntax
    name = ".".join(os.path.basename(filename).split(".")[:-1])
    with open(os.path.join(config.carddir, filename) if in_carddir else filename, "r") as f:
        return from_yaml(f.read(), name)

def from_yaml(data, filename="from_yaml"):
    card = Card()
    card.filename = filename
    for key, val in load(data).items():
        setattr(card, key, val)
    return card

def from_dir(path):
    return [from_file(i, in_carddir=False) for i in glob.glob(os.path.join(path, "*.yaml"))]
