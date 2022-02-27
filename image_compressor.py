#!/usr/bin/env python3
import os
import inspect
import time
import shutil
from PIL import Image, ImageOps
from multiprocessing import Process


def chunk_list(lst, n):
    """yields n evenly spaced arrays."""
    for i in range(0, n):
        yield lst[i::n]


def compressing_loop(compressed_dir, script_dir, chunked_list):

    # which process is doing what??
    #print(f"Process ID: {os.getpid()}. I'll do {len(chunked_list)} images...")

    for jpg in chunked_list:

        # path to work with
        old_path = os.path.join(script_dir, jpg)

        with Image.open(fp=old_path) as image:

            # from Metadata
            year = jpg_year(image)

            # name of new dir and path from specific year
            new_dir = os.path.join(compressed_dir, str('IMG_'+year))
            new_path = str(os.path.join(new_dir, jpg)).replace(
                '.jpg', '_compressed.jpg')

            try:
                # new dir available?
                if os.path.exists(new_dir) is False:
                    os.mkdir(new_dir)

                # image already available -> skip
                if os.path.exists(new_path):
                    pass

                # happened once, not sure why... try ignoring
            except FileExistsError:
                continue

            # necessary to keep orientation
            image = ImageOps.exif_transpose(image)

            # resize
            #newsize = image.width//2, image.height//2
            #image = image.resize(newsize, Image.ANTIALIAS)

            # save with new name, new size and lower quality
            image.save(new_path, quality=50, subsampling=0)
            image.close()


def copying_loop(compressed_dir, script_dir, copy_targets):
    for copy_target in copy_targets:

        # files and directory infos
        year = jpg_year(copy_target)
        new_dir = os.path.join(compressed_dir, str('IMG_'+year))
        old_path = os.path.join(script_dir, copy_target)
        new_path = str(os.path.join(new_dir, copy_target)
                       ).replace('.jpg', '_copy.jpg')

        try:
            # new dir available?
            if os.path.exists(new_dir) is False:
                os.mkdir(new_dir)

            # image already copied?
            if os.path.exists(new_path):
                pass

        # happened once, not sure why... try ignoring
        except FileExistsError:
            continue

        # copy file
        shutil.copyfile(src=old_path, dst=new_path)
        #print(f'Copied without compressing: {copy_target}')


def jpg_targets_lists(script_dir):
    """returns lists of valid .jpg file names including extension for a)compressing and b)copying"""
    all_filenames = os.listdir(script_dir)

    target_jpg_list = []
    copy_list = []
    for filename in all_filenames:
        if (filename.split('.')[-1] == 'jpg' and
                filename[0] != '.'):
            target_jpg_list.append(filename)

        elif ('.jpg' in filename and filename[0] != '.'):
            copy_list.append(filename)

    return target_jpg_list, copy_list

# not hidden
# contains '.jpg'


def jpg_year(image):
    """ takes image object, returns year when taken from Metadata """
    try:
        # take year from image metadata
        year = str(image._getexif()[36867][:4])
        return year

    except AttributeError:
        # try with file creation year
        year = str(time.ctime(os.path.getctime(image))[-4:])

    return year


def count_files_in_dirs(output_dir):
    # recursive
    file_amount = 0
    for dirpath, dirnames, filenames in os.walk(output_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                file_amount += 1
    return file_amount


def progress_bar(compressed_dir, total, barLength=20):
    # prints out a nice progress bar by checking number of files
    count = True
    while count is True:
        current = count_files_in_dirs(compressed_dir)

        percent = float(current) * 100 / total
        arrow = '-' * int(percent/100 * barLength - 1) + '>'
        spaces = ' ' * (barLength - len(arrow))

        # print actual bar:
        print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
        if percent >= 100:
            count = False
            print('Progress: [%s%s] %d %%' % (arrow, spaces, percent))
        else:
            time.sleep(1)


def main():
    try:
        # where am i? Path infos
        scrip_path = inspect.getframeinfo(inspect.currentframe()).filename
        script_dir = os.path.dirname(os.path.abspath(scrip_path))
        compressed_dir = os.path.join(script_dir, 'IMG_compressed')

        # find targets
        compress_jpg_targets, copy_jpg_targets = jpg_targets_lists(script_dir)
        jpg_compress_amout = len(compress_jpg_targets)
        jpg_copy_amount = len(copy_jpg_targets)

        # 0 targets ->stop
        if not jpg_compress_amout and not jpg_copy_amount:
            print('No files to compress in this directory')
        else:
            print(f'\nFound {jpg_compress_amout} valid .jpg files to compress')
            print(
                f'Found {jpg_copy_amount} .jpg files to copy without compressing\n')

            if not copy_jpg_targets:
                print()
            else:
                print('Copying only: (year taken from file creation date)')
                for _ in copy_jpg_targets:
                    print(_)

            # chunk targets for 4 processes
            chunk_1, chunk_2, chunk_3, chunk_4 = chunk_list(
                compress_jpg_targets, 4)

            # ...foo/bar/IMG_compressed folder available?
            try:
                if os.path.exists(compressed_dir) is False:
                    os.mkdir(compressed_dir)
            except FileExistsError:
                pass

            # copy strange .jpg files without compressing
            copying_loop(compressed_dir, script_dir, copy_jpg_targets)

            # go!
            p1 = Process(target=compressing_loop, args=(
                compressed_dir, script_dir, chunk_1))
            p2 = Process(target=compressing_loop, args=(
                compressed_dir, script_dir, chunk_2))
            p3 = Process(target=compressing_loop, args=(
                compressed_dir, script_dir, chunk_3))
            p4 = Process(target=compressing_loop, args=(
                compressed_dir, script_dir, chunk_4))

            process_list = [p1, p2, p3, p4]

            # start processes
            for p in process_list:
                p.start()

            # verbosity while running
            progress_bar(compressed_dir, (jpg_compress_amout +
                         jpg_copy_amount), barLength=40)
            print()

            # close processes
            for p in process_list:
                p.join()

            for p in process_list:
                p.close

    except KeyboardInterrupt:
        # close processes
        for p in process_list:
            p.join()

        for p in process_list:
            p.close
        print('bye')


if __name__ == '__main__':
    main()
