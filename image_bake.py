from os import remove, truncate
from re import search, split
from subprocess import call
from shutil import copyfileobj, copy
import hashlib
import lzma
import gzip
import bz2


def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))


def create_user_script(customization):
    # creates custom user script file
    create_script = open('user_script.sh', 'w')
    create_script.write(customization)
    create_script.close()


class ImageConvert:
    def __init__(self, image_name, image_url, input_format,
                 output_format, file_name):
        # Set all common variables for the ImageConvert class
        self.image_name = image_name
        self.image_url = image_url
        self.input_format = input_format
        self.output_format = output_format
        self.file_name = file_name

    def qemu_convert(self):
        # Perform qemu image conversion for format type specified
        print(f'\nConverting {self.image_name} to {self.output_format} format with qemu-img utility...')
        call(f'qemu-img convert -f {self.input_format} -O {self.output_format} {self.image_name} {self.file_name}', shell=True)
        remove(self.image_name)


class ImageCustomize():
    def __init__(self, image_name, packages,
                 customization, method, output_format,
                 file_name, image_size):
        # Set all common variables for the ImageCustomization class
        self.image_name = image_name
        self.packages = ",".join(packages)
        self.customization = customization
        self.method = method
        self.output_format = output_format
        self.file_name = file_name
        self.image_size = image_size

    def image_resize(self):
        # resize image partition to specification in template file
        new_image = f'{self.file_name}_new'

        if search('G', self.image_size):
            # convert gigabytes to bytes for new file size
            image_size_b = int(split('G', self.image_size)[0]) * (1024**3)
        if search('M', self.image_size):
            # convert megabytes to bytes for new file size
            image_size_b = int(split('M', self.image_size)[0]) * (1024**2)

        # create new image file for truncation
        with open(new_image, 'wb') as fh:
            truncate(new_image, image_size_b)

        # call virt resize to expand sda1 partition to
        #  truncated image's new size
        call(f'virt-resize --expand /dev/sda1 {self.file_name} {new_image}', shell=True)

        # copy newly truncated file to current directory as originally
        #  named image file and remove temp image_file
        copy(new_image, self.file_name)
        remove(new_image)

    def build_method(self):
        # Determine build method type (virt-customize or virt-builder)
        if self.method == 'virt-customize':
            print(f'\nCustomizing {self.image_name} image with virt-customize\
                  utility...\n')
            print(f'\nInstalling the following packages:{self.packages}\n')
            # creates custom user script ran via CLI in virtcustomize
            create_user_script(self.customization)
            # user_script = open('user_script.sh', 'r').read()
            # print(f'\nApplying the following user script:\
            #       \n {user_script}')
            # update package cache and install packages
            call(f'virt-customize -a {self.file_name} -update --install {self.packages}\
                 --run user_script.sh', shell=True)
            remove('user_script.sh')
        elif self.method == 'virt-builder':
            # update package cache and install packages
            print(f'\nCustomizing {self.image_name} image with virt-builder utility')
            print(f'\nInstalling the following packages: {self.packages}\n')
            # creates custom user script ran via CLI in virtcustomize
            create_user_script(self.customization)
            # user_script = open('user_script.sh', 'r').read()
            # print(f'\nApplying the following user script:\n {user_script}')
            call(f'virt-builder -v -x {self.image_name} --update --install {self.packages} --run user_script.sh\
                 --format {self.output_format} --output {self.file_name}', shell=True)
            remove('user_script.sh')

class ImageCompress:
    # Compress image to specification in template file (gz, bz2, xz)
    def __init__(self, compression, compressed_name, file_name):
        self.compression = compression
        self.compressed_name = compressed_name
        self.file_name = file_name

    def compress(self):
        print(f'\nCompressing image using {self.compression} method....')
        if self.compression == "gz":
            with open(self.file_name, 'rb') as file_in, \
                gzip.open(self.compressed_name, 'wb') as file_out:
                copyfileobj(file_in, file_out)
        elif self.compression == "bz2":
            with open(self.file_name, 'rb') as file_in, \
                bz2.open(self.compressed_name, 'wb') as file_out:
                copyfileobj(file_in, file_out)
        else:
            with open(self.file_name, 'rb') as file_in, \
                lzma.open(self.compressed_name, 'wb') as file_out:
                copyfileobj(file_in, file_out)
