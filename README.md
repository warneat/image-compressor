## image-compressor

(tl;dr) compress your images in .jpg format into subfolders sorted by years with reduced filesize.<br />
For videos, see also: [video-compressor](https://github.com/warneat/video-compressor) 
<br />

### Use-case:
If you run out of storage on your smartphone and don't want to spend hours deleting and sorting out pictures, one easy solution is to simply reduce the file-size of your images on the backup device (Computer/HDD/NAS?) by using this script and shove them back to your phone.<br />

### Notes:
- The image_compressor script only deals with .jpg files.
- By default, file size will be reduced to about 10-25% of the original size, while maintaining absolutely acceptable quality (see also: [Quality adjustments](https://github.com/warneat/image-compressor#quality-adjustments)).
- For every .jpg file the year of its creation is taken eighter from metadata or several fallback options (see also: [Further Reading](https://github.com/warneat/image-compressor#further-reading))
- No files will be deleted!
- A directory 'IMG_compressed' is created which will hold the subdirectories IMG_2019, IMG_2020 ... per year respectively.
- .jpg files that have weird numbers after the extension (as i experienced in my case) are copied without changes.
- Files without '.jpg' are being ignored.
- The image-compressor does **not** run through subdirectories.

Simply place `image_compressor.py` at the place your pictures are sitting and run it. <br />

### Installation (Unix-like, MacOS)
Assuming Python (version >= 3.4) is installed, in terminal:

clone this repository, cd into it:

        git clone https://github.com/warneat/image-compressor && cd image-compressor

Install dependencies:

        pip3 install -r requirements.txt

copy the script to your image folder e.g: 
    
        cp image_compressor.py ~/foo/bar/images

Optionally, clean up/delete repository with

        cd .. &&  sudo rm -r image-compressor

#### Run

In your image directory run the script with 
    
        python3 image_compressor.py
    or
        ./image_compressor.py


### On Windows 

- Download this repository or `git clone https://github.com/warneat/image-compressor` like above.
- Install dependencies: Command-Line from within the new folder `pip3 install -r requirements.txt`
- move the image-compressor.py script to desired location and run it from there with `python .\image_compressor.py`


### Quality adjustments
-  2 settings are available:
  - overall quality-value, by default set to `quality=50` 
  - reduction of image-resolution (pixles) is off by default (dividing by 2 further reduces filesize by factor 0.25!)
  
  To modify settings:
  - change `quality=xx` to your liking (line 61) and/or
  - uncomment (remove `#`) from line 57 and 57 and adjust values
  
### Further reading

- If the information is not available in the 'exif data', the file name is analyzed for common naming-patterns (e.g.) IMG_20220301_134230.jpg, Screenshot_20220301_134230.jpg or similar. Next fallbacks are the 'OS-known' creation-time, which is often not as acurate, especially in case of Linux, where 'YYYY' is used instead.

- The script runs on 4 processes (Raspberry Pi: All 4 cores 100%) :)

- As the processing might take hours or days for a large amount of data, when accessing via remote/ssh you might want to use screen ([ultra-quick tutorial](https://linuxize.com/post/how-to-use-linux-screen/)) to keep it running in background without an open terminal session.<br> 
In a nutshell: Install it, `$screen` to start, [do stuff], `ctr+a` and `d` to detach. Reattach with `$screen -r`

- To automate (image) backups e.g Phone to NAS/Cloud-Server/Online-Account... i highly recommend the app [FolderSync](https://play.google.com/store/apps/details?id=dk.tacit.android.foldersync.lite) 

#### Feedback is very much apprechiated
