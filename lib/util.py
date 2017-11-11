import numpy as np
import cv2
from scipy.misc import imsave
from scipy.ndimage import imread

def openImg(fname):
    if "/perims/" in fname:
        img = cv2.imread(fname, 0)
        img = img.astype(np.float32)
    # elif "landsat.png" in fname:
    #     img = cv2.imread(fname, cv2.IMREAD_COLOR)
    #     # img = imread(fname, flatten=False, mode='F')
    #     print('imported landsat shape is ', img.shape)
    #     img = img.astype(np.float32)
    #     print('landat right after import is', img.shape)
    #     np.savetxt('importedlandsetrightafter.csv', img[:,:,0], delimiter=',')
    else:
        img = cv2.imread(fname, cv2.IMREAD_UNCHANGED)
        img = img.astype(np.float32)
    # print('img type is ', img.type)
    # img = img.astype(np.float32)
    channels = cv2.split(img)
    for c in channels:
        c[invalidPixelIndices(c)] = np.nan
    return cv2.merge(channels)

def saveImg(fname, img):
    to_save = np.array(img.astype('float32'))
    print('datatype of saveimg is ', to_save.dtype)
    max_float = np.finfo(np.float32).max
    print("to save shape is", to_save.shape)
    print('max is ', max_float)
    to_save[np.where(np.isnan(to_save))] = max_float
    # for listed in to_save: 
    #     for e in listed: 
    #         if np.isnan(e):
    #             print('e is ', e)
    #             listed[e] = max_float
    print('after conversions', to_save)
    if 'landsat' in fname:
        print('landsat to_save shape is ', to_save.shape)
        # np.savetxt('landsatrightafter32bitconversion.csv', to_save[:,:,0], delimiter=',')
    # imsave(fname, to_save.astype(np.uint8))
    cv2.imwrite(fname, to_save.astype(np.uint16))
    
def validPixelIndices(layer):
    validPixelMask = 1-invalidPixelMask(layer)
    return np.where(validPixelMask)

def invalidPixelIndices(layer):
    return np.where(invalidPixelMask(layer))

def invalidPixelMask(layer):
    # If there are any massively valued pixels, just return those
    HUGE = 1e10
    huge = np.absolute(layer) > HUGE
    if np.any(huge):
        return huge

    # floodfill in from every corner, all the NODATA pixels are the same value so they'll get found
    h,w = layer.shape[:2]
    noDataMask = np.zeros((h+2,w+2), dtype = np.uint8)
    fill = 1
    seeds = [(0,0), (0,h-1), (w-1,0), (w-1,h-1)]
    for seed in seeds:
        cv2.floodFill(layer.copy(), noDataMask, seed, fill)
        # plt.figure('layer')
        # plt.imshow(layer)
        # plt.figure('noDataMask')
        # plt.imshow(noDataMask)
        # plt.show()

    # extract ouf the center of the mask, which corresponds to orig image
    noDataMask = noDataMask[1:h+1, 1:w+1]
    return noDataMask

if __name__ == '__main__':
    import glob
    import matplotlib.pyplot as plt
    folder = 'data/**/'
    types = ('*.tif', '*.png') # the tuple of file types
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(folder+files))
    for f in files_grabbed:
        # print(f)
        # if 'riceRidge' not in f:
        #     continue
        img = openImg(f)
        plt.figure(f)
        if len(img.shape) > 2 and img.shape[2] > 3:
            plt.imshow(img[:,:,:3])
        else:
            plt.imshow(img)
        plt.show()
