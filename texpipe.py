import subprocess
import click
import os
import sys

# Personnal libraries
sys.path.insert(0, 'utilities')
import utilities

# Get input from command line
#############################

# - sbsname : without .sbs extension, with absolute or relative path or, by default, in the current directory
# - graphname : name of the Graph in the .sbs file
# - foldername : with absolute or relative path or, by default, the current directory containing the .sbs files

@click.command()
@click.option('--sbsname', default = '', help='.sbs filename to use, with no extension. Mandatory')
@click.option('--graphname', default = '', help='The included Graph name. First one by default.')
@click.option('--foldername', default = os.getcwd(), help='With absolute or relative path or, by default, the current directory containing the .sbs files.')
def main(sbsname, graphname, foldername):
    
    # Get configuration informations
    config = utilities.compileconfig()
    
    # 3D renderings
    
    if config['blender']:
        # Render module with blender engine
        blender_path = config['blender']['engine_path']
        
        # Render all the files for the wanted type
        for style in config['renderstyle']:
            if config['renderstyle'][style] == "True":
                for scene in config['scene_dielectric']:
                    render_scene = os.path.join(config['folder']['3dfiles'], config['scene_dielectric'][scene])
                    # Using argparse in Blender python script as click is not recognized
                    subprocess.call([blender_path, render_scene, '--background', '--python', 'blender3drender.py', '--', '--graph=' + graphname, '--sbs=' + sbsname])

if __name__ == '__main__':
	main()
