import numpy as np


def create_circular_mask(w, h, center=None, radius=None):
    """
    Generates a circular mask based on width, height, centre and
    radius of an image.

    :param h:
    :param w:
    :param center:
    :param radius:
    :return:
    """

    if center is None:
        # use the middle of the image
        center = [int(w/2), int(h/2)]

    if radius is None:
        # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    yc, xc = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((xc - center[0])**2 + (yc-center[1])**2)

    mask = dist_from_center <= radius
    return mask
