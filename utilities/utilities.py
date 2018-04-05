#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os


def getdefaultconfig():
    """
    Get the config file in the operating folder
    """
    currentfolder = os.getcwd()
    config = getconfig(os.path.join(currentfolder, 'texpipe.cfg'))
    return config


def getconfig(src):
    """
    Read the source cfg file.
    Return a dictionnary with each section itself a dictionnary
    """
    rslt={}
    config = configparser.ConfigParser()
    config.read(src)
    for section in config.sections():
        itemlist = {}
        for item in config[section]:
            itemlist[item] = config[section][item]
        rslt[section] = itemlist
    return rslt

def compileconfig():
    """
    With a list of files, compile to have the more defined config informations
    TODO : Retun only the default config file for now, needs heritage system
    """
    config = getdefaultconfig()
    return config
    
