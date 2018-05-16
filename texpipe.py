import subprocess
import click
import os
import sys
import shutil
import zipfile
import zlib
from PIL import Image


# Personnal libraries
sys.path.insert(0, 'utilities')
import utilities
import pipe_substance
import imaging
from pysbs import batchtools, substance, context

def texpipe():
    
    # Get configuration informations
    config = utilities.compile_config('texpipe.cfg')
    logo_file = config['logo']['logofile']
    scale_logo = float(config['logo']['scale'])
    margin_logo = float(config['logo']['margin'])
    opacity_logo = float(config['logo']['opacity'])
    destination_logo = config['folder']['final_previews']
    #### Compute Tex files from asked .sbs and graph ####
    # Get the .sbs files list
    foldername = config['folder']['sbs']
    sbsfiles = utilities.check_new_sbs_files(foldername)
    print('Sbsfiles list : {}'.format(sbsfiles))
    # Cook the corresponding .sbsar files
    for sbsfile in sbsfiles:
        proceed_sbs = os.path.splitext(os.path.split(sbsfile)[1])[0]
        # Cook the sbsar file
        pipe_substance.cooksbsar(sbsfile, config['folder']['sbsar'])
        # Get the metadata from the sbs file (a list of dicts)
        sbs_content = pipe_substance.read_sbs(sbsfile)
        
        # For each graph of each .sbs, write the usefull metadata to a sidecar file in final_outputs folder
        for dictionnary in sbs_content:
            sidecar_path = os.path.join(config['folder']['final_previews'], '{}.nfo'.format(dictionnary['identifier']))
            with open(sidecar_path, 'w') as my_sidecar_file: 
                for item in dictionnary:
                    if item == 'description' or item == 'usertags' or item == 'label':
                        my_sidecar_file.write('{}:{}\n'.format(item, dictionnary[item]))
        
            # Render the textures from the corresponding graph of the cooked .sbsar
            material_name = dictionnary['identifier']
            # :random_seed: use a random seed or not (then the seed would be 0)
            random_seed = 0 
            # :param params: Instantiated parameters
            params = {}
            # :type params: {string: [...]}
            # :param sbsar_file: The sbsar file to render
            sbsar_file = os.path.join(config['folder']['sbsar'], '{}.sbsar'.format(proceed_sbs))
            # :param output_size: the output size for the rendered image. In format 2^n where n is the parameter
            output_size = int(config['tex_render_parameters']['size'])
            # :param output_path: The directory to put the result
            output_path = config['folder']['textures']
            # :param use_gpu_engine: Use GPU engine when rendering
            use_gpu_engine = True
            pipe_substance.render_textures(material_name, random_seed, params, sbsar_file, output_size, output_path, use_gpu_engine)
            
            # Copy the sbsar to final folder
            shutil.copyfile(sbsar_file, os.path.join(config['folder']['final_previews'], '{}.sbsar'.format(proceed_sbs)))
            
            # Make a composite picture of the textures in the final folder
            texture_composite = imaging.make_composite_texture(material_name,
                                            config['folder']['textures'],
                                            config['folder']['final_previews'],
                                            int(config['3dscene']['size']))
            # Watermarking in the same time than Blender images
            imaging.watermark(texture_composite, destination_logo, logo_file, scale_logo, margin_logo, opacity_logo)
            
            # Make a zip file with copy of all the textures, in final_outputs folder
            zip_path = os.path.join(config['folder']['final_previews'], '{}.zip'.format(dictionnary['identifier']))
            tex_path = config['folder']['textures']
            with zipfile.ZipFile(zip_path, 'w') as newzip:
                for item in os.listdir(tex_path):
                    if dictionnary['identifier'] in item:
                        newzip.write(os.path.join(config['folder']['textures'], item), item, zipfile.ZIP_DEFLATED)

    
    # #### 3D renderings ####
    for file in sbsfiles:

        # get config file for this sbs folder, replace the default generic ones if needed
        config_folder = os.path.join(os.path.dirname(file), 'texpipe.cfg')
        folder_configuration = utilities.getconfig(config_folder)
        for key in folder_configuration:
            config[key] = folder_configuration[key]
        # Get config file for this sbs, replace the latest one if needed
        sbsname = os.path.splitext(os.path.basename(file))[0]
        config_file = os.path.join(os.path.dirname(file), os.path.splitext(os.path.basename(file))[0] + '.cfg')
        sbs_configuration = utilities.getconfig(config_file)
        for key in sbs_configuration:
            config[key] = sbs_configuration[key]
        print('sbs_configuration :{}'.format(sbs_configuration))
        
        for graphname in sbs_configuration:

            # Render the corresponding sbs
            if config['blender']:
                # Render module with blender engine
                blender_path = config['blender']['engine_path']
                
                # Render all the files for the wanted type
                for style in config['renderstyle']:
                    if config['renderstyle'][style] == "True":
                        for scene in config[style]:
                            render_scene = os.path.join(config['folder']['3dfiles'], config[style][scene])
                            print('\nRendering : {} with style {} and material graph {} from file {}.sbs\n'.format(config[style][scene], style, graphname, sbsname))
                            
                            # Using argparse in Blender python script as click is not recognized
                            subprocess.call([blender_path, render_scene, '--background', '--python', 'blender3drender.py', '--', '--graph=' + graphname, '--sbs=' + sbsname, '--style=' +style])

    # Copy all the 3D renders files to operating folder
    utilities.copy_folder_content(config['folder']['finals'], config['folder']['operating'])
    
    # Brand the operating files
    filelist = os.listdir(config['folder']['operating'])
    for image in filelist:
        image_path = os.path.join(config['folder']['operating'], image)
        # Put them with correct definition
        image_content = Image.open(image_path) 
        image_content = image_content.resize((int(config['3dscene']['size']), int(config['3dscene']['size'])))
        image_content.save(image_path)
        # Brand them
        imaging.watermark(image_path, destination_logo, logo_file, scale_logo, margin_logo, opacity_logo)
   
    
    
if __name__ == '__main__':
    texpipe()
