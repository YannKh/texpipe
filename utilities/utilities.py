#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import sys
import shutil

def compile_config(config_filename):
    """
    With a list of files, compile to have the more defined config informations
    TODO : Retun only the default config file for now, needs heritage system
    
    :config_filename: name of the config file, with extension
    :type config_filename: string
    """
    
    # Get the general base configuration, from the current directory
    base_config = getconfig(os.path.join(os.getcwd(), config_filename))
    return base_config

def getconfig(src):
    """
    Read the source cfg file.
    Return a dictionnary with each section itself a dictionnary
    :src: absolute name of the file to parse
    :type src: string
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


def get_files_by_extension(targetextension, foldername, recursive):
    """
    Get an extension type by name and a folder to check in
    Return the list of files using this extension
    Can be recursive or not.
    
    :targetextension: the extension of the files to list
    :type targetextension: string
    :foldername: the folder to list in (absolute name)
    :type foldername: string
    :recursive: Recursive search in the folder
    :type recursive: Boolean
    """
    fileList = []
    if recursive:
        for root, subFolders, files in os.walk(foldername):
            for file in files:
                f = os.path.join(root, file)
                if os.path.isfile(f):
                    if os.path.splitext(file)[1][1:] == targetextension:
                        fileList.append(f)
    else:
        for file in os.listdir(foldername):
            f = os.path.join(foldername, file)
            if os.path.isfile(f):
                if os.path.splitext(file)[1][1:] == targetextension:
                    fileList.append(f)

    return fileList

def copy_folder_content(source, destination, extension =''):
    """
    Copy all the files from a folder to another one
    Can restrict to an extension type if needed
    
    :source: absolute path of the source folder
    :type source: string
    :destination: absolute path of the destination folder
    :type destination: string
    :extension: Recursive search in the folder
    :type recursive: string
    """
    folder_content = os.listdir(source)

    for files in folder_content:
        files = os.path.join(source, files)
        if extension == '':
            shutil.copy(files, destination)
        else:
            for files in folder_content:
                if files.endswith('.{}'.format(extension)):
                    shutil.copy(files, destination)
