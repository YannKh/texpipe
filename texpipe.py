import subprocess
import click
import os
import sys

# Personnal libraries
sys.path.insert(0, 'utilities')
import utilities
import substance

# Get input from command line
#############################

# - sbsname : without .sbs extension, with absolute or relative path or, by default, in the current directory
# - graphname : name of the Graph in the .sbs file
# - foldername : with absolute or relative path or, by default, the current directory containing the .sbs files

# @click.command()
# @click.option('--sbsname', default = '', help='.sbs filename to use, with no extension. Mandatory')
# @click.option('--graphname', default = '', help='The included Graph name. First one by default.')
# @click.option('--foldername', default = os.getcwd(), help='With absolute or relative path or, by default, the current directory containing the .sbs files.')
def main():
    
    # Get configuration informations
    config = utilities.compile_config('texpipe.cfg')
    
    #### Compute Tex files from asked .sbs and graph ####
    # Get the .sbs files list
    foldername = config['folder']['sbs']
    sbsfiles = utilities.get_files_by_extension('sbs', foldername, True)
    # # Cook the corresponding.sbsar files
    # for sbsfile in sbsfiles:
        # utilities.cooksbsar(sbsfile, config['folder']['sbsar'])
    # # Render the textures from the coked .sbsar
    # # TODO FIXME
    # # render_textures(material_name, random_seed, params, sbsar_file, output_size, output_path, use_gpu_engine)
    

    
    
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
        print(sbs_configuration)
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

if __name__ == '__main__':
	main()
