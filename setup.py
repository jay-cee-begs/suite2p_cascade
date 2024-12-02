from setuptools import setup, find_packages
import yaml
import chardet

# Detect file encoding
def detect_encoding(filename):
    with open(filename, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def parse_requirements_yaml(filename, encoding):
    with open(filename, 'r', encoding=encoding) as file:
        data = yaml.safe_load(file)
        return [str(line) for line in data.get('dependencies', [])]
        # return [line.strip() for line in file if line.strip() and not line.startswith("#")]

def parse_requirements_txt(filename, encoding):
    """
    Parses a plain text requirements file to extract dependencies.
    """
    with open(filename, 'r', encoding=encoding) as file:
        return [
            line.strip()
            for line in file
            if line.strip() and not line.startswith("#")  # Exclude empty lines and comments
        ]


# encoding = detect_encoding('requirements.txt')  # Or 'requirements.yaml'
# print(f"Detected encoding: {encoding}")
# requirements = parse_requirements_yaml('requirements.txt', encoding)
env_requirements = {
    'suite2p': parse_requirements_yaml('suite2p-req.yml', detect_encoding('suite2p-req.yml')),
    'cascade': parse_requirements_yaml('cascade-req.yml', detect_encoding('cascade-req.yml')),
    'data_env': parse_requirements_txt('statannotations-req.txt', detect_encoding('statannotations-req.txt'))


}

setup(
    name='suite2p_cascade', 
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    extra_require = {
        "suite2p":env_requirements['suite2p'],
        'cascade':env_requirements['cascade'],
        'data_env':env_requirements['data_env']

    }
        # List your project dependencies here
    
)

"""File can be run in terminal with 
python setup.py develop"""