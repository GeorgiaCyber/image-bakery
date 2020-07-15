import os
import subprocess as sp
import hashlib
import yaml
import requests
from tqdm import tqdm

class LoadYaml:
    def __init__(self, template_file):
        self.template_file = template_file
        # self.build_method = build_method    
    def load_yaml(self):
    # Loads a yaml file
        with open(self.template_file, "r") as file_descriptor:
            data = yaml.safe_load(file_descriptor,)
        return data

class ParseYaml:
    def __init__(self, image_config):
        self.image_config = image_config
    def image_name(self):
    # Parses yaml for image_name
        for item, value in list(self.image_config.items()):
            if item == '':
                return value
    def method(self):
    # Parses yaml for method
        for item, value in list(self.image_config.items()):
            if item == 'method':
                return value
    def image_url(self):
    # Parses yaml for image_url
        for item, value in list(self.image_config.items()):
            if item == 'image_url':
                return value
    def output_format(self):
    # Parses yaml for output_format
        for item, value in list(self.image_config.items()):
            if item == 'output_format':
                return value
    def compressed(self):
    # Parses yaml for ocompression
        for item, value in list(self.image_config.items()):
            if item == 'compressed':
                return value
    def convert(self):
    # Parses yaml for conversion
        for item, value in list(self.image_config.items()):
            if item == 'convert':
                return value
    def packages(self):
    # Parses yaml for packages
        for item, value in list(self.image_config.items()):
            if item == 'packages':
                return value
    def customization(self):
    # Parses yaml for customization
        for item, value in list(self.image_config.items()):
            if item == 'customization':
                return value

class DownloadImage:
    def __init__(self, image_url):
        self.image_url = image_url
       
    def download_image(self):
    # Downloads image from url passed from download_url() if available
        file = self.image_url.split('/')[-1].replace(".img", ".qcow2")
        # file = file.replace("img", "qcow2")
        r = requests.get(self.image_url, stream=True, allow_redirects=True)
        total_size = int(r.headers.get('content-length'))
        initial_pos = 0

        print('\nDownloading image from ({}):'.format(self.image_url))
        with open(file, 'wb') as f:
            with tqdm(total=total_size, unit='it', unit_scale=True, desc=file, initial=initial_pos, ascii=True) as pbar:
                for ch in r.iter_content(chunk_size=1024):
                    if ch:
                        f.write(ch)
                        pbar.update(len(ch))
    def hash_download_image(self):
    # Create hash value for image downloaded with download_image()
        file = self.image_url.split('/')[-1].replace(".img", ".qcow2")
        with open(file, 'rb') as file:
            content = file.read()
        sha = hashlib.sha256()
        sha.update(content)
        hash_file = sha.hexdigest()
        print('\nImage SHA256 Hash: {}'.format(hash_file))
    

class QemuImgConvert:
    def __init__(self, image_name, image_url, output_format, convert, packages, customization):
    #  Set all common variables for the class
        self.image_name = image_name
        self.image_url = image_url
        self.output_format = output_format
        self.convert = convert
        self.packages = packages
        self.customization = customization
    def qemu_convert(self):
    #  Perform qemu image conversion for format type specified
        file = self.image_url.split('/')[-1].replace(".img", ".qcow2")
        orig_format = file.split('.')[-1]
        new_filename = file.replace("qcow2", (self.output_format))
        print('\nConverting {} to {} format with qemu-img utility:'.format(file, self.output_format))
        sp.call('qemu-img convert -f {} -O {} {} {} && rm {}'.format(orig_format, self.output_format, file, new_filename,  file))
        

def print_config(image_config):
        print('\nYAML loaded with the following specification:\n')
	# Print YAML properties to terminal    Z
        for key, value in image_config.items():
            print(str(key)+': ' + str(value))
        return 

# Specify template dir/file and load with yaml parser
template_file = '../templates/ubuntu.yaml'
image_config = LoadYaml(template_file).load_yaml()

# Associate keys with item variables
config_item = ParseYaml(image_config)

# Prints build specification
print_config(image_config)

#Parses YAML configuration and sets variables for each item
image_name = config_item.image_name()
method = config_item.method()
image_url = config_item.image_url()
output_format = config_item.output_format()
compressed = config_item.compressed()
convert = config_item.convert()
packages = config_item.packages()
customization = config_item.customization()

# if method == 'qemu-img':
#     qemubuild = QemuImgConvert(image_name, image_url, output_format, convert, packages, customization)
#     DownloadImage(image_url).download_image()
#     DownloadImage(image_url).hash_download_image()
if convert == True:
    qemubuild.qemu_convert()

# elif method == 'virt-builder':

# elif method == 'docker':

# elif method == 'podman':







