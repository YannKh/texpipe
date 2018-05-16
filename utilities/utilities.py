#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import sys
import shutil
import time

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

def check_new_sbs_files(path):
    """
    Check for modified files in hierarchy
    Add the modified .sbs files since last check
    If the texpipe.cfg of a folder has changed -> add all the .sbs files of this folder
    If the .cfg of a file has changed -> add the corresponding .sbs file

    Return a list of sbs files
    """
    # Get the time from time_stamp_file if it exists, if not, it will rebake everything
    # Stores last check epoch in last_check var

    now = time.time()
    if os.path.exists(os.path.join(path, 'time_stamp_ref.cfg')):
        with open (os.path.join(path, 'time_stamp_ref.cfg'), 'r') as time_stamp:
            content = time_stamp.read().splitlines()
            last_check = float(content[0])
    else:
        last_check = float(0)

    with open (os.path.join(path, 'time_stamp_ref.cfg'), 'w') as time_stamp:
        time_stamp.write(str(now))
    
    # Check for more recent files in the root folder (and sub-dirs)
    files = []
    sbs_files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            file_full_path = os.path.abspath(os.path.join(root, filename))
            file_epoch = os.path.getmtime(file_full_path)
            if file_epoch > last_check:
                files.append(file_full_path)

    # print('Recent files : {}'.format(files))
    
    for filename in files:
        file_dirname = os.path.dirname(filename)
        file_basename = os.path.basename(filename)
        file_basename_no_extension = os.path.splitext(os.path.basename(filename))[0]
        file_extension = os.path.splitext(os.path.basename(filename))[1][1:]
        sbs_corresponding_file = os.path.join(file_dirname, file_basename_no_extension + '.sbs')
        
        if file_basename == 'texpipe.cfg':
            for item in get_files_by_extension('sbs', file_dirname, False):
                if item not in sbs_files:
                    sbs_files.append(item)

        elif file_extension == 'cfg' and os.path.exists(sbs_corresponding_file):
            if sbs_corresponding_file not in sbs_files:
                sbs_files.append(sbs_corresponding_file)
            
        elif file_extension == 'sbs':
            if filename not in sbs_files:
                sbs_files.append(filename)
        else:
            pass

    return sbs_files
