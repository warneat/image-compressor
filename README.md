## Image-Compressor

(tl,dr:) compress your images in IMG_YYYYMMDD_xxxxxx.jpg format into subfolders sorted by years with reduced filesize.<br />

If you run out of storage on your smartphone and don't want to spend hours deleting and sorting out pictures, this is an easy solution.<br />

Reduce the file-size of your images on the backup device (NAS?) and shove them back to your phone.

### Notes:
- The naming-Convention IMG_YYYYMMDD_xxxxxx.jpg is assumed (mostly Android standard Camera-App).
- The image_compressor only deals with .jpg files.
- By default, file size will be reduced to about 25% of the original size, while maintaining acceptable quality.
- No files will be deleted!
- .jpg files that do not fit the pattern (e.g. have weird numbers after the extension, as i experienced in my case) are copied without changes is file size.
- Files without '.jpg' are ignored.
- The image_compressor does **not** run through subdirectories.

Simply place `image_compressor.py` in the directory, where your pictures are sitting and run it. 

### Installation
Assuming Python and Pip3 is installed, in terminal:

clone this repository, cd into it:

        git clone https://github.com/warneat/image-compressor && cd image-compressor

Install dependencies:

        pip3 install -r requirements.txt

move the script to your image folder e.g: 
    
        mv image_compressor.py ~/foo/bar/images

clean up with

        cd .. &&  sudo rm -r image-compressor

### Run

In your image directory run the script with 
    
        python3 image_compressor.py
    or
        ./image_compressor.py





### Further reading

- By default, compressing value is set to `quality=50`, Antialiasing is enabled. To modify settings:
  - change `quality=xx`to your liking (line 55) and/or: 
  - remove `, Image.ANTIALIAS` in line 54 to disable antialising (i don't see a reason to do so...)
  
- The script runs on 4 processes (Raspberry Pi: All 4 cores 100%) :)

- As the processing might take hours or days for large amounts of data, when acessing via remote/ssh you might want to use screen ([ultra-quick tutorial](https://linuxize.com/post/how-to-use-linux-screen/)) to keep it running without an open terminal session.<br> 
In a nutshell: Install it, `$screen` to start, [do stuff], `ctr+a` and `d` to detach. Reattach with `$screen -r`

- To automate (image) backups e.g Phone to NAS/Cloud-Server/Online-Account... i highly recommend the app [FolderSync](https://play.google.com/store/apps/details?id=dk.tacit.android.foldersync.lite) 

#### Feedback is very much apprechiated
