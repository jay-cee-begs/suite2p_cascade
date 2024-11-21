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
        return data.get('dependencies', [])
        # return [line.strip() for line in file if line.strip() and not line.startswith("#")]


# encoding = detect_encoding('requirements.txt')  # Or 'requirements.yaml'
# print(f"Detected encoding: {encoding}")
# requirements = parse_requirements_yaml('requirements.txt', encoding)
env_requirements = {
    'suite2p': parse_requirements_yaml('suite2p-req.yml', detect_encoding('suite2p-req.yml')),
    'cascade': parse_requirements_yaml('cascade-req.yml', detect_encoding('cascade-req.yml')),
    'data_env': parse_requirements_yaml('data_env', detect_encoding('data_env'))

}

setup(
    name='suite2p_cascade', 
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    extra_require = {
        "suite2p":env_requirements['suite2p'],
        'cascade':env_requirements['cascade']

    }
        # List your project dependencies here
    
)

"""File can be run in terminal with 
python setup.py develop"""