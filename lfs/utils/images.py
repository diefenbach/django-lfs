from StringIO import StringIO

try:
    import ImageFile
    import Image
except ImportError:
    from PIL import Image
    from PIL import ImageFile


def scale_to_min_size(image, min_width, min_height):
    """Returns an image, that isn't smaller than min_width and min_height.
    That means one side is exactly given value and the other is greater.

    This may only makes sense if the image is cut after it is scaled.
    """

    # resize proportinal
    width, height = image.size

    prop_x = float(min_width) / width
    prop_y = float(min_height) / height

    # TODO: Translate to english
    # Die groessere Proportion (oder Faktor oder Quotient) zwischen Soll-Groesse
    # und Ist-Groesse kommt fuer beide Kanten (da proportional) zur Anwendung.
    # Das bedeutet die uebrige Kante ist auf jeden Fall groesser als gewuenscht
    # (da Multiplikation mit Faktor).

    if prop_x > prop_y:
        height = int(prop_x * height)
        image = image.resize((min_width, height), Image.ANTIALIAS)
    else:
        width = int(prop_y * width)
        image = image.resize((width, min_height), Image.ANTIALIAS)

    return image


def scale_to_max_size(image, max_width, max_height):
    """Returns an image, that isn't bigger than max_width and max_height.

    That means one side is exactly given value and the other is smaller. In
    other words the image fits at any rate in the given box max_width x
    max_height.
    """
    # resize proportinal
    width, height = image.size

    # TODO: Translate to english
    # Erechne Proportionen zwischen Soll-Weite und Ist-Weite und zwischen
    # Soll-Hoehe und Ist-Hoehe

    prop_width = float(max_width) / width
    prop_height = float(max_height) / height

    # TODO: Translate to english
    # Die kleinere Proportion (oder Faktor oder Quotient) der beiden kommt fuer
    # beide Kanten (da Proportional) zur Anwendung. Das bedeutet die uebrige
    # Kante ist auf jeden Fall kleiner als gewuenscht (da Multiplikation mit
    # Faktor).

    if prop_height < prop_width:
        width = int(prop_height * width)
        image = image.resize((width, max_height), Image.ANTIALIAS)
    else:
        height = int(prop_width * height)
        image = image.resize((max_width, height), Image.ANTIALIAS)

    return image


def scale_to_width(image, target_width):
    """Returns an image that has the exactly given width and scales height
    proportional.
    """
    width, height = image.size

    prop_width = float(target_width) / width
    new_height = int(prop_width * height)

    image = image.resize((target_width, new_height), Image.ANTIALIAS)

    return image


def scale_to_height(image, target_height):
    """Returns an image that has the exactly given height and scales width
    proportional.
    """
    width, height = image.size

    prop_height = float(target_height) / height
    new_width = int(prop_height * width)

    image = image.resize((new_height, target_height), Image.ANTIALIAS)

    return image
