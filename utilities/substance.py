#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from pysbs import batchtools

def cooksbsar(src_file, output_path):
    """
    Cooks an sbsfile to an sbsar file

    :param src_file: path to the sbs file to cook
    :type src_file: string
    :param resources_path: The path to the substance resources
    :type resources_path: string
    :param output_path: The directory to put the result
    :type output_path: string

    :return: None
    """
    print('Operating {}'.format(src_file))
    batchtools.sbscooker(inputs=src_file,
                         output_path=output_path,
                         expose_random_seed=False,
                         quiet=True).wait()

def render_textures(material_name, random_seed, params, sbsar_file, output_size, output_path, use_gpu_engine):
    """
    Invokes sbsrender to render out maps for a material with a set of parameters

    :param material_name: name of the material being rendered
    :type material_name: string
    :random_seed: use a random seed or not (then the seed would be 0)
    :type random_seed: boolean
    :param params: Instantiated parameters
    :type params: {string: [...]}
    :param sbsar_file: The sbsar file to render
    :type sbsar_file: string
    :param output_size: the output size for the rendered image. In format 2^n where n is the parameter
    :type output_size: int
    :param output_path: The directory to put the result
    :type output_path: string
    :param use_gpu_engine: Use GPU engine when rendering
    :type use_gpu_engine: bool

    :return: None
    """
    if random_seed:
        random_number = rd.uniform(0, 10000)
    else:
        random_number = 0
    values = ['$outputsize@%d,%d' % (output_size, output_size),
              '$randomseed@%d' % random_number] + list(map(param_vec, params.items()))
    engine_params = {'engine' : batchtools_utilities.get_gpu_engine_for_platform()} if use_gpu_engine else {}
    batchtools.sbsrender_render(inputs=sbsar_file,
                                output_path=output_path,
                                output_name='%s-{outputNodeName}' % (material_name),
                                set_value=values,
                                **(engine_params)).wait()
