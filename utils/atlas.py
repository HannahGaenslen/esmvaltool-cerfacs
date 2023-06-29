#!/usr/bin/env python3

'''
Writing of an html website (atlas) to view models and their ESMValTool diagnostics

Hannah-Theresa Gaenslen 2023
''' 

from yattag import Doc
from yattag import indent
from jinja2 import Environment, FileSystemLoader

doc, tag, text = Doc().tagtext()

import os
import os.path
from argparse import ArgumentParser

def main():
    parse_args()
    
    path = options["DIRECTORY"][0]
    atlas_dict = create_nestdic(path)
    html_list(atlas_dict, indent=0)
    tree = indent(doc.getvalue())
    
    atlas_filename = "atlas.html"
    environment = Environment(loader=FileSystemLoader("templates/"))
    atlas_template = environment.get_template("atlas_template.html")
    
    with open(path + atlas_filename, mode="w", encoding="utf=8") as atlas:
        atlas.write(atlas_template.render(tree=tree))
        #print(f'... wrote {atlas_filename}')    

options = {}
def parse_args():
    '''Parses the command line arguments'''
    global options
    parser = ArgumentParser()
    parser.description = "creates an ESMValTool atlas"
    parser.add_argument("DIRECTORY", nargs="*",
                        help="path to the output directory as definied initially in config-user.yml")
    op = parser.parse_args()
    options = vars(op)
   
    
def get_dirtree(output_dir):  
    '''get a list of all directories'''
    dirtree = []
    for dirpath, dirnames, filenames in os.walk(output_dir):
        for filename in [f for f in filenames if f.endswith(".html")]:
            dirpath = dirpath.removeprefix(output_dir)
            if dirpath[:6] != 'recipe':
                dirtree.append(os.path.join(dirpath, filename))
    return dirtree

def create_nestdic(output_dir):
    '''create a nested dictionary out of the paths'''
    nested_dict = {}
    print(get_dirtree(output_dir))
    for item in get_dirtree(output_dir):
        p = nested_dict
        for x in item.split('/'):
            if len(x.split('.')) > 1: 
                if x.split('.')[0] == 'index':
                    p['overview'] = output_dir + item
                else:
                    None
            else: 
                p = p.setdefault(x, {})
    return nested_dict

def html_list(d, indent=0):
    '''convert nested dictionary into html text'''
    for key, value in d.items():
        with tag('li'):
            with tag('span', klass='caret'):
                text(str(key))
            with tag('ul', klass='nested'): 
                if isinstance(value, dict):
                    if list(value.keys())[0]=='overview': 
                        with tag('li'):
                            with tag('a', href=str(list(value.values())[0])):
                                text('recipe overview')
                    else: 
                        html_list(value, indent+1)
                elif isinstance(value, list):
                    for element in value:
                        with tag('li'):
                            text(str(element))
                elif value==None:
                    None
                else:
                    with tag('li'):
                        text(str(value))

    
if __name__ == "__main__":
    main()
