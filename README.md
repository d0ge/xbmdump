# xbmdump
ReadXBMImage in coders/xbm.c in ImageMagick before 7.0.8-9 (https://github.com/ImageMagick/ImageMagick/commit/216d117f05bff87b9dc4db55a1b1fadb38bcb786) leaves data uninitialized when processing an XBM file that has a negative pixel value. If the affected code is used as a library loaded into a process that includes sensitive information, that information sometimes can be leaked via the image data. Exploit for ImageMagick's uninitialized memory disclosure in xbm coder. This exploit is based on https://github.com/neex/gifoeb source code. 
# How to
1. Run `./xbmdump gen 128x128 dump.xbm`. The script needs ImageMagick (default) or GraphicsMagick (use `--tool GM`) to generate the images.
2. Change file extension from xbm to any in web server whitelist (png, gif, jpg, jpeg, etc.)
3. Upload `dump.gif` somewhere. If the following conditions hold true
   1. A preview is generated
   2. It changes significantly from one upload to another

   then you're lucky.
4. Download and save the preview as `output.ext`.
5. Run `./xbmdump recover 128x128 output.ext`
