#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests

def liberapay_json_read(name):
    """
    Read the public JSON information from a Liberapay account
    Return a dictionnary
    :name: name of the account to get info from
    : type name: string
    """
    url = 'https://liberapay.com/{}/public.json'.format(name)
    content = requests.get(url)
    return content.json()


if __name__ == '__main__':
    lp_infos = liberapay_json_read('YannKervran')
    lp_goal = lp_infos['goal']['amount']
    lp_received = lp_infos['receiving']['amount']
    lp_percentage = float(lp_received) / float(lp_goal) * 100
    print('Pourcentage de dons YannKervran: {} %'.format(lp_percentage))
