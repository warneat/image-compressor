#!/usr/bin/env python3
import datetime
import os
import inspect
import time
import shutil
import platform
from PIL import Image, ImageOps
from multiprocessing import Process


def chunk_list(lst, n):
    """yields n evenly spaced arrays."""
    for i in range(0, n):
        yield lst[i::n]


def compressing_loop(compressed_dir, script_dir, chunked_list):
    for jpg in chunked_list:

        # path to work with
        old_path = os.path.join(script_dir, jpg)

        with Image.open(fp=old_path) as image:

            date = jpg_date(image, jpg)
            year = date[:4]

            
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
                    continue

                # happened once, not sure why
            except FileExistsError:
                continue

            # necessary to keep orientation
            try:
                image = ImageOps.exif_transpose(image)
            except AttributeError:
                pass

            # resize
            # newsize = image.width//2, image.height//2
            # image = image.resize(newsize, Image.ANTIALIAS)

            # save with new name, new size and lower quality
            try:
                # with available exif data 
                image.save(new_path, quality=50, subsampling=0, exif=image.info["exif"])
                image.close()
            except KeyError:
                # without available exif data 
                image.save(new_path, quality=50, subsampling=0)
                image.close()
        try:
            set_modified_date(new_path, date)
        except Exception:
            pass

def copying_loop(compressed_dir, script_dir, copy_targets):
    for copy_target in copy_targets:

        # files and directory infos
        jpg_dt = jpg_date(old_path, copy_target)
        jpg_year = jpg_dt[:4]
        old_path = os.path.join(script_dir, copy_target)
        new_dir = os.path.join(compressed_dir, str('IMG_'+jpg_year))
        new_path = str(os.path.join(new_dir, copy_target)
                       ).replace('.jpg', '_copy.jpg')

        try:
            # new dir available?
            if os.path.exists(new_dir) is False:
                os.mkdir(new_dir)

            # image already copied?
            if os.path.exists(new_path):
                pass

        # happened once, not sure why... ignore
        except FileExistsError:
            continue

        # copy file
        shutil.copyfile(src=old_path, dst=new_path)
        print(f'Copied without compressing: {copy_target}')

        #set modification date
        try:
            set_modified_date(new_path, jpg_dt)
        except Exception:
            pass


def jpg_targets_lists(script_dir):
    """returns lists of valid .jpg file names including extension for a)compressing and b)copying"""
    all_filenames = os.listdir(script_dir)

    target_jpg_list = []
    copy_list = []
    for filename in all_filenames:
        if (filename.split('.')[-1] == 'jpg' and                # extension is '.jpg'
                filename[0] != '.'):                            # not hidden
            target_jpg_list.append(filename)

        # contains '.jpg', not hidden
        elif ('.jpg' in filename and filename[0] != '.'):
            copy_list.append(filename)

    return target_jpg_list, copy_list



def jpg_date(img, filename):
    """takes eighter PIL Image-Object or filepath for "img" and a filename. returns date as string in yyyy:mm:dd, see fallback options"""

    if isinstance(img, str):
        # it's not a PIL-object!
        date = date_from_name_pattern(filename)  # risky, but effective
    else:
        # It's a PIL-object!
        date = date_from_PIL_exif(img)

    if date is None:
        date = date_from_name_pattern(filename)
        img = img.filename  # (img is now filepath)
    if date is None:
        # ...not found, fallback
        date = date_from_os(img)
    if date is None:
        date = "0000:01:01"
    
    return date

def date_from_os(filepath):
    '''takes filepath to file'''

    date = None
    if platform.system() == 'Windows':
        c_timestamp = time.ctime(os.path.getctime(filepath))
        c_date_obj = datetime.datetime.fromtimestamp(c_timestamp) #datetime obj
        date = c_date_obj.strftime("%Y:%m:%d") # formated
    else:
        try:
            stat = os.stat(filepath)
            c_time = time.ctime(stat.st_birthtime)
            c_date_obj = datetime.datetime.strptime(c_time, "%a %b %d %H:%M:%S %Y") #datetime obj
            date = c_date_obj.strftime("%Y:%m:%d") # formated
        except Exception:
            # We're probably on Linux. No easy way to get creation dates here
            # or something else went wrong
            # -> take YYYY
            date = '0000:01:01'
    return date


def date_from_name_pattern(filename):
    '''search in filename for common naming-convention...)'''

    date = None
    filename = str(filename).upper()
    prefix_list = ['IMG_', 'IMG-', 'IMG', 'WHATSAPP_IMAGE_',
                'SCREENSHOT_', 'SCREENSHOT-', 'SIGNAL-', 'PXL_']

    for prefix in prefix_list:
        if prefix in filename:
            try:
                #TODO: fix this...
                date = int(filename.split(prefix)[1][:8])
                # trying to convert as double-check
                date_obj = datetime.datetime.strptime(date, '%Y%m%d')
                # and bring to exif format
                date = date_obj.strftime("%Y:%m:%d")
            except Exception:
                continue
        
    return date


def date_from_PIL_exif(img):
    try:
        date = str(img._getexif()[36867])
        #exif date output example:
        # 2018:08:25 16:38:43
        return date[:10]
    except Exception:
        return None

def count_files_in_dirs(output_dir):
    # recursive
    file_amount = 0
    for dirpath, dirnames, filenames in os.walk(output_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                file_amount += 1
    return file_amount

def set_modified_date(filepath, date):
    # set modification date of the copy to creation date.
    # change creation date not yet possible os-wide
    date_timestamp = datetime.datetime.strptime(date, "%Y:%m:%d").timestamp()
    os.utime(filepath, (time.time(), date_timestamp))


def progress_bar(compressed_dir, total, barLength=20):
    '''prints out a nice progress bar by checking number of files'''
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
                print(
                    'For the following copying-targets, year is taken from file creation date, wich is not always acurate')

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
        print('[ctr+c -> byebye]]')


if __name__ == '__main__':
    main()
