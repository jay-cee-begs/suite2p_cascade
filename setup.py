from setuptools import setup, find_packages

setup(
    name='suite2p_cascade', 
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},

    
)

"""File can be run in terminal with 
python setup.py develop"""