#! /usr/bin/env python3

import os, sys, argparse, time, hashlib, lzma, gzip, bz2
from tqdm import tqdm
from requests import get
from yaml import safe_load
from subprocess import call
from re import search, split
from shutil import copyfileobj, copy
from functools import wraps


def load_yaml(template):
    # Load yaml data
    with open(template, 'r') as fd:
        template_data = safe_load(fd)
    # Load yaml specifications
    global image_name, image_url, method, image_url, compression, input_format, output_format, compressed, convert, packages, customization, image_size, image_out_name
    image_name = template_data.get("image_name")
    method = template_data.get("method")
    image_url = template_data.get("image_url")
    compression = template_data.get("compression")
    input_format = template_data.get("input_format")
    output_format = template_data.get("output_format")
    compressed = template_data.get("compressed")
    convert = template_data.get("convert")
    packages = template_data.get("packages")
    customization = template_data.get("customization")
    image_size = template_data.get("image_size")
    image_out_name = f'{image_name}.{output_format}'

def hash_file(*args):
    # Create hash value for image
    with open(*args, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    # hash = sha.hexdigest() 
    print(f'SHA256 Hash: {sha.hexdigest()}')

class ImageTransfer:
    #transfer of image files, upload and download
    def __init__(self, image_name, image_url):
        self.image_name = image_name
        self.image_url = image_url     

    def download_image(self):
        # Downloads image from url passed from download_url() if available
        file = self.image_url.split('/')[-1]
        file_request = get(self.image_url, stream=True, allow_redirects=True)
        total_size = int(file_request.headers.get('content-length'))
        initial_pos = 0
        print(f'\nDownloading image from ({self.image_url}):')
        with open(file, 'wb') as file_download:
            with tqdm(total=total_size, unit='it', unit_scale=True,
                        desc=file, initial=initial_pos,
                        ascii=True) as progress_bar:
                for chunk in file_request.iter_content(chunk_size=1024):
                    if chunk:
                        file_download.write(chunk)
                        progress_bar.update(len(chunk))
        os.rename(file, self.image_name)
        print(f'\nImage download finished.\nImage Name:{self.image_name}')
        hash_file(self.image_name)

    '''
    Placeholder for upload functions (glance, amazon s3, minio, dockerhub, etc.)
    '''
    # def upload_glance(self):


class BuildImage:
    def __init__(self, *args):
        self.image_name = image_name
        self.image_out_name = image_out_name
        self.method = method
        self.input_format = input_format
        self.output_format = output_format
        self.image_size = image_size
        self.convert = convert
        self.packages = packages
        self.customization = customization
        self.verbose = verbose
    
    def create_user_script(self):
        # Creates custom user script file
        create_script = open('user_script.sh', 'w')
        create_script.write(self.customization)
        create_script.close()

    def convert_image(self):
        # Perform qemu image conversion for format type specified
        print(f'\nConverting {self.image_name} to {self.output_format} format with qemu-img utility...')
        call(f'qemu-img convert -f {self.input_format} -O {self.output_format} {self.image_name} {self.self.image_out_name}', shell=True)
        remove(self.image_name)

    def resize_image(self):
        # resize image partition to specification in template file
        new_image = f'{self.image_out_name}_new'
        if search('G', self.image_size):
            image_size_b = int(split('G', self.image_size)[0]) * (1024**3)
        if search('M', self.image_size):
            image_size_b = int(split('M', self.image_size)[0]) * (1024**2)
        with open(new_image, 'wb') as fh:
            os.truncate(new_image, image_size_b)
        call(f'virt-resize --expand /dev/sda1 {self.image_out_name} {new_image}', shell=True)
        copy(new_image, self.image_out_name)
        os.remove(new_image)
        print(f'\nImage finished resizing using virt-resize\nImage Name:{self.image_out_name}')
        hash_file(self.image_out_name)

    def build_method(self):
        if self.packages != 'NONE':
            self.packages = ",".join(self.packages)
        BuildImage.create_user_script(self)     
        if self.method == 'virt-customize':
            print(self.verbose)
            if self.verbose == True and self.packages != 'NONE':
                print(f'\n{self.image_out_name} image is being created with virt-customize in VERBOSE mode')
                call(f'virt-customize -v -x -a {self.image_out_name} -update --install {self.packages} --run user_script.sh', shell=True)
            elif self.verbose == False and self.packages != 'NONE':
                print(f'\n{self.image_out_name} image is being created with virt-customize')
                call(f'virt-customize -a {self.image_out_name} -update --install {self.packages} --run user_script.sh', shell=True)
            elif self.verbose == True and self.packages == 'NONE':
                print(f'\n{self.image_out_name} image is being created with virt-customize in VERBOSE mode')
                call(f'virt-customize -v -x -a {self.image_out_name} -update --run user_script.sh', shell=True)
            else:
                print(f'\n{self.image_out_name} image is being created with virt-customize')
                call(f'virt-customize -a {self.image_out_name} -update --run user_script.sh', shell=True)
        # if self.method == 'virt-builder':

    # def virt_customize(self):


    # def virt_builder(self):

        #      and verbose != 'NONE':

        # elif self.method == 'virt-customize' and verbose == 'NONE':
        #     call(f'virt-customize -a {self.image_out_name} -update --run user_script.sh', shell=True)
        #     virt_customize(self.image_out_name, self.packages, virt_customize_cmd)

        # def virt_customize(*args):
        #     print(f'\n{self.image_out_name} image is being created with virt-customize')
        #     if self.packages != 'NONE':
        #         virt_customize_cmd()
        #     else:
        #         print(f'\nInstalling the following packages:{self.packages}\n')
        #         call(f'virt-customize -v -x -a {self.image_out_name} -update --install {self.packages}\
        #             --run user_script.sh', shell=True)
        # elif self.customization != 'NONE' and self.method == 'virt-builder':   
        #     print(f'\n{self.image name} image is being created with virt-builder')
        #     if not packages:
        #         call(f'virt-builder {self.image_out_name} --update --run user_script.sh\
        #             --format {self.output_format} --output {self.image_out_name}', shell=True)
        #     else:
        #         print(f'\nInstalling the following packages: {self.packages}\n')
        #         call(f'virt-builder {self.image_out_name} --update --install {self.packages} --run user_script.sh\
        #             --format {self.output_format} --output {self.image_out_name}', shell=True)
        # print(f'\nImage customization finished using {self.method}\nImage Name:{self.image_out_name}')
        # hash_file(image_out_name)
        # os.remove('user_script.sh')

# def compress(image_out_name, compression):
#     # Compress image to specification in template file (gz, bz2, xz)
#     print(f'\nCompressing image using {compression} method....')
#     if compression == "gz":
#         with open(image_out_name, 'rb') as file_in, \
#             gzip.open(f'{image_out_name}.{compression}', 'wb') as file_out:
#             copyfileobj(file_in, file_out)
#     elif compression == "bz2":
#         with open(image_out_name, 'rb') as file_in, \
#             bz2.open(f'{image_out_name}.{compression}', 'wb') as file_out:
#             copyfileobj(file_in, file_out)
#     else:
#         with open(image_out_name, 'rb') as file_in, \
#             lzma.open(f'{image_out_name}.lzma', 'wb') as file_out:
#             copyfileobj(file_in, file_out)


def main():
    parser = argparse.ArgumentParser(prog='image_baker', description='Start baking an image.')
    parser.add_argument('-v', '--verbose', default='NONE', action='store_true', help='Verbose mode for troubleshooting image build')
    parser.add_argument('-a', '--all', default='NONE', action='store_true', help='Runs image baker on all template files in the specified directory')
    parser.add_argument('-T', '--type', default='NONE', action='store', choices=['vm', 'docker'], help='Specifies the type of image to build', )
    parser.add_argument('-t', '--template', default='NONE', action='store', help='Specifies template yaml file to build.')
    parser.add_argument('-d', '--dir_path', default='NONE', action='store', metavar=('./some/directory/'), help='Directory path for multiple template yaml files')
    parser.add_argument('-f', '--format', nargs=2, action='store', metavar=('input_format', 'output_format'), help='specifies the input and output format for image conversion')
    parser.add_argument('-o', '--output_name', action='store', help='Specifies the output file name for the image.')
    parser.add_argument('-s', '--image_size', action='store', help='Specifies the the output image size')
    parser.add_argument('-m', '--method', default='virt-customize', action='store', choices=['virt-customize', 'virt-builder'], help='Specifies the build method to use.')
    parser.add_argument('-c', '--compression', default='NONE', action='store', choices=['gz', 'bz2', 'lzma'], help='Specifies compression and type')
    parser.add_argument('-p', '--packages', action='store', help='Packages to install on the image')

    num_args = len(sys.argv)

    args = parser.parse_args()

    if num_args < 2:
        sys.stderr.write('ERROR: No options were present, refer to help (--help) if needed.\n')
    
    if args.all == 'NONE' and args.template == 'NONE' and args.dir_path == 'NONE' and num_args > 2:
        sys.stderr.write('ERROR: Specify a directory path, template file, or all. Refer to help (--help) if needed.\n')

    if args.dir_path != 'NONE' and args.all != 'NONE':
        #Bake images for all templates in a given dir path
        template_list = []
        templates = os.listdir(args.dir_path)
        for item in templates:
            if item.endswith('.yaml') or item.endswith('.yml'):
                item = f'{args.dir_path}{item}'
                template_list.append(item) 
        for template in template_list:
            load_yaml(template)
            # ImageTransfer(image_name, image_url).download_image()
            # BuildImage(image_size, image_out_name).resize_image()

            # --- old --- #
            # download_image(image_url)
            # qemu_convert(image_name, image_out_name, input_format, output_format)
            # resize_image(image_size)
            # create_user_script(customization)
            # build_method(method, input_format, output_format, image_out_name, packages, customization)
            # compress(image_out_name, compression)

    if args.template != 'NONE':
        load_yaml(args.template)

        verbose = args.verbose
        print(verbose)
        BuildImage(packages, method, image_out_name, verbose).build_method()

            # ImageTransfer.download_image(image_name, image_url)
            # download_image(image_url)
            # build_method(image_name, image_out_name, method, input_format, output_format, image_size, convert, packages, customization, compression)
            # qemu_convert(image_name, image_out_name, input_format, output_format)
            # resize_image(image_size)
            # create_user_script(customization)
            # build_method(method, input_format, output_format, image_out_name, packages, customization)
            # compress(image_out_name, compression)   
          
       
    # if args.template != 'NONE':
    #     #Bake images for a specifc yaml template
    #     template = args.template
    #     print(load_yaml(template))
    #     print(type(template))




            # YamlParse.load_yaml(dir_path, template)
            # print(template_data)
        
        # with os.scandir(args.dir_path) as templates:
        #     for template in templates:
        #         print(template)
                # print(templates)
                # image_template = load_yaml(template)
            # print(image_template)


    # args = parser.parse_args()

    # template_name = args.template

    # if args.template == 'NONE' and not args.dir_path:
    #     sys.stderr.write(f'Missing template name or directory:\n {args.template}')
    #     parser.usage()
    #     sys.exit(1)
    
    # if template_name not in dirs:
    #     sys.stderr.write(f'ERROR: Image named {template_name} not found.')
    #     sys.stderr.write('Make sure you spelled the template name correctly.')
    #     sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
