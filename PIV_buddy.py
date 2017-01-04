from __future__ import print_function
from stitch_buddy import *
import openpiv.tools
import openpiv.process
import openpiv.scaling



def filenamesToDict(indir, wellNameDict=None):

    """
    Transforms the .tif-files in a directory into a dictionary.

    Filenames must conform to the following general pattern:
    ..._wellID-xxx_threeDigitRowNumber_threeDigitColNumber...

    :param
    indir: path to directory with files from a multiwell mosaic experiment
    wellNameDict: Dictionary of names to give the wells from the wellID-number

    property_dict = 'nrows': (int) No. of rows in well
                    'ncols': (int) No. of columns in well
                    'nChans': (int) No. of channels in image
                    'xpix': (int) No. pixels in X-dimension of images
                    'ypix': (int) No. pixels in Y-dimension of images
                    'frame_interval': (float) No. of time units between frames
                    'timeUnit': (str) time unit
                    'pixres': (float) size of pixels in resolution units
                    'resUnit': (str) spatial resolution unit
                    'pixelType':(str) pixeldepth of image
                    'positions': position_dict gives file at position (row,col)
                    'files':(list) names of files in well
                    'isConcat':(bool) If the sequence is split in to multiple files
                    'OME-XML':None <- Not implemented yet

    position_dict = {(row, col):filename(s)}



    :return: Dictionary with wellID:property_dict
    """
    # Ingore non-.tif files in indir
    filenames = [fname for fname in os.listdir(indir) if ".tif" in fname]

    wellDict = {}

    isConcat = False

    #Regex used to flexibly identify wells, rows, columns, and split files from filenames

    #Matches any number of digits preceded by "MMStack_" and followed by "-"
    well_regex = re.compile("(?<=MMStack_)\d+(?=-)")

    #Matches three digits preceded by three digits and "_"
    column_regex = re.compile("(?<=\d{3}_)\d{3}")

    #Matches three digits preceded by three digits and "_"
    row_regex = re.compile("(?<=_)\d{3}(?=_)")

    #Matches a digit preceded by three digits and "_", followed by ".ome"
    concat_regex = re.compile("(?<=\d{3}_\d{3}_)\d(?=\.ome)")

    first_file = os.path.join(indir, filenames[0])

    with tiffile.TiffFile(first_file) as tif:
        meta_data = tif.micromanager_metadata
        frames = len(tif.pages)
        page=tif[0]
        pixres=page.tags['x_resolution'].value #Assumes equal x/y resolution
        resoloution_unit = page.tags['resolution_unit'].value
        pixelDepth = page.tags['bits_per_sample'].value
        omexml = page.tags['image_description'].value



    frame_interval = meta_data['summary']['WaitInterval']
    ypix, xpix = meta_data['summary']['Height'], meta_data['summary']['Width']
    nChannels =  meta_data['summary']['Channels']
    nSlices =  meta_data['summary']['Slices']
    nTimepoints = frames/(nChannels*nSlices)
    resoloution_unit =  {1: 'none', 2: 'inch', 3: 'centimeter'}[resoloution_unit]

    for f in filenames:
        #Extract positioning information from filename with regex
        wellID = int(well_regex.search(f).group())


        if wellNameDict != None:
            wellID = wellNameDict[wellID]


        rowNumber = int(row_regex.search(f).group())
        columnNumber = int(column_regex.search(f).group())
        concat = concat_regex.search(f)
        if concat != None:
            isConcat = True

        #If there is no key for wellID in wellDict -> create a dict of properties
        if wellDict.get(wellID) == None:
            wellDict[wellID] = {'nrows':1,
                                'ncols':1,
                                'nChannels':int(nChannels),
                                'nSlices': int(nSlices),
                                'xpix':int(xpix),
                                'ypix':int(ypix),
                                'nTimepoints':int(nTimepoints),
                                'frame_interval':frame_interval,
                                'timeunit':'ms',
                                'pixel_resolution':pixres, #resolution stored as rational in tif tag
                                'resoloution_unit': resoloution_unit,
                                'pixelDepth':pixelDepth,
                                'positions':{},
                                'files':[],
                                'isConcat':isConcat,
                                'OME-XML':omexml
                                }

        #Populate Properties
        wellDict[wellID]['nrows'] = max(rowNumber+1, wellDict[wellID]['nrows'])
        wellDict[wellID]['ncols'] = max(columnNumber+1, wellDict[wellID]['ncols'])

        #List of filenames for the well
        wellDict[wellID]['files'].append(f)

        #Dict with (row, column):(list) filename(s)
        if wellDict[wellID]['positions'].get((rowNumber, columnNumber)) == None:
            wellDict[wellID]['positions'][(rowNumber, columnNumber)]=[f]
        else:
            wellDict[wellID]['positions'][(rowNumber, columnNumber)].append(f)
            wellDict[wellID]['positions'][(rowNumber, columnNumber)].sort()
            wellDict[wellID]['isConcat'] = isConcat

    return wellDict




frame_a  = openpiv.tools.imread( 'exp1_001_a.bmp' )
frame_b  = openpiv.tools.imread( 'exp1_001_b.bmp' )

u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a, frame_b, window_size=24, overlap=12, dt=0.02, search_area_size=64, sig2noise_method='peak2peak' )

x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size=24, overlap=12 )

u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = 1.3 )

u, v = openpiv.filters.replace_outliers( u, v, method='localmean', n_iter=10, kernel_size=2)

x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 96.52 )

openpiv.tools.save(x, y, u, v, 'exp1_001.txt' )
