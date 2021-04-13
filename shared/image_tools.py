import numpy
from PIL import Image


def imresize(arr, 
             size, 
             interp: str ='bilinear', 
             mode=None):
    """
    Converted from Scipy V1.1.0

    Resize an image.

    Parameters
    ----------
    arr : ndarray
        The array of image to be resized.
    size : int, float or tuple
        * int   - Percentage of current size.
        * float - Fraction of current size.
        * tuple - Size of the output image (height, width).

    interp : str, optional
        Interpolation to use for re-sizing ('nearest', 'lanczos', 'bilinear',
        'bicubic' or 'cubic').
    mode : str, optional
        The PIL image mode ('P', 'L', etc.) to convert `arr` before resizing.
        If ``mode=None`` (the default), 2-D images will be treated like
        ``mode='L'``, i.e. casting to long integer.  For 3-D and 4-D arrays,
        `mode` will be set to ``'RGB'`` and ``'RGBA'`` respectively.

    Returns
    -------
    imresize : ndarray
        The resized array of image.
    """

    im = Image.fromarray(arr, mode=mode)
    ts = type(size)
    if numpy.issubdtype(ts, numpy.signedinteger):
        percent = size / 100.0
        size = tuple((array(im.size)*percent).astype(int))
    elif numpy.issubdtype(type(size), numpy.floating):
        size = tuple((array(im.size)*size).astype(int))
    else:
        size = (size[1], size[0])
    func = {'nearest': 0, 'lanczos': 1, 'bilinear': 2, 'bicubic': 3, 'cubic': 3}
    imnew = im.resize(size, resample=func[interp])
    return numpy.asarray(imnew)