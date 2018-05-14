import argparse
import sys
import os
import bpy

# Personnal libraries
sys.path.insert(0, 'utilities')
import utilities

###### OPERATIONS #####

# Get input from command line
#############################

def main():
    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
            "Run blender in background mode with this script:"
            "  blender --background --python " + __file__ + " -- [options]"
            )

    parser = argparse.ArgumentParser(description=usage_text)

    # Arguments list
    parser.add_argument("-s", "--sbs", dest="sbs", type=str, required=True,
            help="This is the sbs filename")
    parser.add_argument("-g", "--graph", dest="graph", type=str, required=True,
            help="This is the graph filename")
    parser.add_argument("-st", "--style", dest="style", type=str, required=True,
            help="This is the style of the material, to use proper shading")
    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    if not args.sbs:
        print("Error: --text=\"some string\" argument not given, aborting.")
        parser.print_help()
        return

    # Run the rendering function
    blender3drender(args.sbs, args.graph, args.style)

def blender3drender(sbsfile, graphname, style):
    
    # TODO FIXME : Use different Shader style according to args.style
    
    # Get configuration informations
    config = utilities.compile_config('texpipe.cfg')
    
    ###### VARIABLES ##### 
    renderobject = config['3dscene']['renderobject']
    rendermaterial = config['3dscene']['rendermaterial']
    uvmapname = config['3dscene']['uvmapname']
    
    # Render size
    w = int(config['3dscene']['size'])
    h = w
    
    # Texture set
    basecolor_path = os.path.join(config['folder']['textures'], graphname + '-basecolor.png')
    normal_path = os.path.join(config['folder']['textures'], graphname + '-normal.png')
    roughness_path = os.path.join(config['folder']['textures'], graphname + '-roughness.png')
    height_path = os.path.join(config['folder']['textures'], graphname + '-height.png')

    # Add displacement with height texture to the target object
    heightTex = bpy.data.textures.new('Texture name', type = 'IMAGE')
    heightTex.image = bpy.data.images.load(height_path)
    dispMod = bpy.data.objects[renderobject].modifiers.new("Displace", type='DISPLACE')
    dispMod.texture = heightTex
    dispMod.texture_coords = 'UV'
    dispMod.uv_layer = "UVTex"
    dispMod.strength = 0.02
    
    
    # Give the material name to change in the file and clear then set the nodes
    mat = (bpy.data.materials.get(rendermaterial) or
           bpy.data.materials.new(rendermaterial))
    
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    
    while(nodes): nodes.remove(nodes[0])
    
    output  = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    texture = nodes.new("ShaderNodeTexImage")
    uvmap   = nodes.new("ShaderNodeNormalMap")
    uvmaptexture = nodes.new("ShaderNodeTexImage")
    roughnesstexture = nodes.new("ShaderNodeTexImage")
    
    texture.image = bpy.data.images.load(basecolor_path)
    
    uvmap.uv_map = uvmapname
    uvmaptexture.image = bpy.data.images.load(normal_path)
    uvmaptexture.color_space = 'NONE'
    
    roughnesstexture.image = bpy.data.images.load(roughness_path)
    roughnesstexture.color_space = 'NONE'
    
    links.new(output.inputs['Surface'], principled.outputs['BSDF'])
    links.new(principled.inputs['Base Color'],   texture.outputs['Color'])
    links.new(principled.inputs['Roughness'],   roughnesstexture.outputs['Color'])
    links.new(principled.inputs['Normal'],    uvmap.outputs['Normal'])
    links.new(uvmap.inputs['Color'],    uvmaptexture.outputs['Color'])
    
    # Save the file ? For debugging purpose
    # If so, distribute nodes along the x axis to ease the reading
    # for index, node in enumerate((uvmaptexture, uvmap, texture, principled, output)):
    #    node.location.x = 200.0 * index
    # outfile_path = '~/Documents/Programmation/python/allegorithmic/texpipe/tests/result/result.blend'
    # bpy.ops.wm.save_as_mainfile(filepath=outfile_path)
    
    # Render the result
    sceneid = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    render_path = os.path.join(config['folder']['finals'], graphname + '_' + sceneid + '.png')
        
    bpy.context.scene.render.filepath = render_path
    bpy.context.scene.render.resolution_x = w
    bpy.context.scene.render.resolution_y = h
    bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
	main()
