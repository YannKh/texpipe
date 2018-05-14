#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from pysbs import batchtools, substance, context

def param_vec(name_value_pair):
    """
    Generates a string command line parameter string for sbsrender

    :param name_value_pair: name and value of the parameter set as a tuple
    :type name_value_pair: (string, [val])
    :return: string The parameter merged with its value in a batch processor compatible way
    """
    return '%s@%s' % name_value_pair
    
def get_gpu_engine_for_platform():
    """
    Gets the gpu engine string for the current platform

    :return: string the gpu engine string
    """
    from sys import platform
    if 'linux' in platform:
        return "ogl3"
    elif 'darwin' in platform:
        return 'ogl3'
    elif 'win' in platform:
        return 'd3d10pc'
    raise BaseException("Failed to identify platform")

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
    myContext = context.Context()
    sbsDoc = substance.SBSDocument(myContext,src_file)
    sbsDoc.parseDoc()
    graph = sbsDoc.getSBSGraphList()[0]
    batchtools.sbscooker(inputs=src_file,
                         output_path=output_path,
                         expose_random_seed=False,
                         quiet=True,
                         verbose=False,
                         includes='/opt/Allegorithmic/Substance_Designer/resources/packages'
                         ).wait()


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
    engine_params = {'engine' : get_gpu_engine_for_platform()} if use_gpu_engine else {}
    batchtools.sbsrender_render(inputs=sbsar_file,
                                input_graph = material_name,
                                output_path=output_path,
                                output_name='%s-{outputNodeName}' % (material_name),
                                set_value=values,
                                **(engine_params)).wait()

def read_sbs(sbsfile):
    # Documentation about SBSGraph : https://support.allegorithmic.com/documentation/display/SAT/graph#graph.graph.SBSGraph
    content = []
    myContext = context.Context()
    sbsDoc = substance.SBSDocument(myContext, sbsfile)
    sbsDoc.parseDoc()
    graphs = sbsDoc.getSBSGraphList()
    for item in graphs:
        graph = {}
        # Doc : https://support.allegorithmic.com/documentation/display/SAT/inputparameters#graph.inputparameters.SBSParamInput
        graph['identifier'] = item.mIdentifier
        graph['label'] = item.mAttributes.mLabel
        graph['description'] = item.mAttributes.mDescription
        graph['author'] = item.mAttributes.mAuthor
        graph['usertags'] = item.mAttributes.mUserTags
        graph['parameters'] = {}
        for param in item.mParamInputs:
            graph['parameters'][param.mIdentifier] = {}
            graph['parameters'][param.mIdentifier]['identifier'] = param.mIdentifier
            graph['parameters'][param.mIdentifier]['defaultvalue'] = param.mDefaultValue.getValue()
        content.append(graph)
    return content
    
