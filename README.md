# Stitchbuddy

A PyQt4 GUI wrapped Python script to stitch MicroManager multiwell mosaiks
 
MicroManager has the option to generate mosaik images and to save each position of the mosaik as a separate tiff-stack.
This program, Stitch Buddy, scans a directory containing OME-tiff files generated by Micrommanager and stitches all mosaiks it finds.
The original purpose of the program was to automatically stitch all mosaiks in a multiwell plate.
It also possible to scale down the stitched mosaik, and to retain all relevant metadata, such as pixel size, time resolution, and OME-XML data.
If the image is rescaled, the imageJ-metadata is also rescaled, but currently not the OME-OXM metadata.

If the image mosaik is too large to fit in to RAM, there is an option to stitch the file frame-by-frame but this is very, very slow.

All tiff file reading/writing and metadata is handled by  [tifffile.py](http://www.lfd.uci.edu/~gohlke/code/tifffile.py.html)
 
