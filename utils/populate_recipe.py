#!/usr/bin/env python

'''
population of ESMValTool single model recipes

Hannah-Theresa Gaenslen 2023

This script produces recipes modified with a given dataset information 
and writes a sbatch job file to run them all at once and saves the output 
into a dataset specific directory.
'''

#If ESMValTool is installed with singularity this script must be executed within a singularity shell:

#module load tools/singularity
#singularity shell -B/data/home/globc -B/data/scratch /data/softs/local/singularity/images/esmvaltool28.sif

#Singularity> PATH=/opt/conda/envs/esmvaltool/bin:$PATH

import yaml
from esmvalcore.config import CFG
from esmvalcore._main import ESMValTool
from argparse import ArgumentParser
import summarize

# cutsomize your dataset here
dataset = {
    'institute': 'CNRM-CERFACS', 
    'activity': 'CMIP', 
    'project': 'CMIP6', 
    'dataset': 'CNRM-ESM2-1', 
    'exp': 'historical', 
    'ensemble': 'r1i1p1f2', 
    'grid': 'gr'
}
        
def main():
    parse_args()
    recipes = options["RECIPES"]
    # specifiy the path to your recipes
    path = '/data/home/globc/gaenslen/ESMValTool/hannah_test/'
    search_ESGF = options["search_esgf"][0]
    output_dir = options["output_dir"][0]
    
    # name the path to your sbatch job file
    #job_file(recipes, path, '/data/home/globc/gaenslen/ESMValTool/esmvaltool_singularity_auto.job', \
    #       search_ESGF, output_dir)
       
    submit_directly(recipes, path, search_ESGF, output_dir)
    summarize.main()
	
options = {}
def parse_args():
    '''Parses the command line arguments'''
    global options
    parser = ArgumentParser()
    parser.description = "populates recipes and produces sbatch job file"
    parser.add_argument("RECIPES", nargs="*",
                        help="names of (multiple) single model recipe(s)")
    parser.add_argument("-d", "--dataset", nargs="*",
                        help="dataset in dictionary form, eg: \n \
                        {'institute': 'CNRM-CERFACS', 'activity': 'CMIP', 'project': 'CMIP6', \n \
                        'dataset': 'CNRM-ESM2-1', 'exp': 'historical', 'ensemble': 'r1i1p1f2', 'grid': 'gr'}",
                        default = dataset)
    parser.add_argument("-s", "--search_esgf", nargs="*",
                        help="search ESGF: never/when_missing/always, default: config_user",
                        default = 'none')
    parser.add_argument("-o", "--output_dir", nargs="*",
                        help="custom output directory or None, default: dataset specific dir",
                        default = new_output_dir(dataset))
    op = parser.parse_args()
    options = vars(op)

def populate_dataset(orig_recipe, dataset, new_path, path):
    '''Overwrites dataset of a given recipe and saves it as modified one'''
    with open(path + orig_recipe, 'r') as file:  
        recipe = yaml.safe_load(file)
        
    for elem in recipe['datasets']:
        if 'obs' not in elem['project'].casefold():  
            elem['dataset'] = dataset['dataset']
            elem['ensemble'] = dataset['ensemble']
            elem['institute'] = dataset['institute']
            elem['grid'] = dataset['grid']
            elem['exp'] = dataset['exp']
            elem['project'] = dataset['project']
        else:
            print(elem['project'])
        
    with open(new_path, 'w') as file:
        recipe = yaml.safe_dump(recipe, file)
    
def new_output_dir(dataset):
    '''Adds dataset specific dir to the output dir specified in the config-user file'''
    return str(CFG['output_dir']) \
        +'/'+ dataset['project'] \
        +'/'+ dataset['activity'] \
        +'/'+ dataset['institute'] \
        +'/'+ dataset['dataset'] \
        +'/'+ dataset['exp'] \
        +'/'+ dataset['ensemble'] 
        

def job_file(recipes, path, jobfile_path, search_ESGF, output_dir):
    '''write sbatch job file'''

    with open('templates/template.job', 'r') as file:
        template = file.read()
        file.close
    
    with open(jobfile_path, 'w') as file:  
        file.write(template)
        for elm in recipes:
            new_path = path + elm.split('.')[0] + '_modified.yml'
            populate_dataset(elm, dataset, new_path, path)
            
            cmd = f'$cmd run {new_path} --log_level debug'
            if search_ESGF != 'none':
                cmd += f' --search_esgf {search_ESGF}'
            if output_dir.casefold() != 'none':
                cmd += f' --output_dir {output_dir}'
            cmd += '\n'
            
            file.write(cmd)
            
        file.close

def submit_directly(recipes, path, search_ESGF, output_dir):
    '''submit modified recipes directly without sbatch job'''
    for elm in recipes:
        new_path = path + elm.split('.')[0] + '_modified.yml'
        populate_dataset(elm, dataset, new_path, path)

        esm = ESMValTool()
        if search_ESGF != 'none' and output_dir.casefold() != 'none':
            esm.run(recipe=new_path)
        elif search_ESGF != 'none':
            esm.run(recipe=new_path,  search_esgf=search_ESGF)
        elif output_dir.casefold() != 'none':
            esm.run(recipe=new_path,  output_dir=output_dir)
        else:
            esm.run(recipe=new_path,  search_esgf=search_ESGF, output_dir=output_dir)

if __name__ == "__main__":
    main()
