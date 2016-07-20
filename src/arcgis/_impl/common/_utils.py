"""set of common utilities"""
import json
import sys

list_types = (list, tuple)
number_type = (int, float)
#--------------------------------------------------------------------------
def is_valid(value):
    from _geom import Point, Polygon, Polyline, MultiPoint, Envelope
    """checks if the value is valid"""
    if isinstance(value, Point):
        if hasattr(value, 'x') and \
           hasattr(value, 'y') :
            return True
        elif 'x' in value and \
             (value['x'] is None or \
             value['x'] == "NaN"):
            return True
        return False
    elif isinstance(value, Envelope):
        if all(hasattr(value, a) for a in ('xmin', 'ymin',
                                           'xmax', 'ymax')) and \
           all(isinstance(getattr(value,a), number_type) for a in ('xmin', 'ymin',
                                                                   'xmax', 'ymax')):
            return True
        elif hasattr(value, "xmin") and \
           (value.xmin is None or value.xmin == "NaN"):
            return True
        else:
            return False
    elif isinstance(value, (MultiPoint,
                            Polygon,
                            Polyline)):
        if 'paths' in value:
            if len(value['paths']) == 0:
                return True
            else:
                return is_line(coords=value['paths'])
        elif 'rings' in value:
            if len(value['rings']) == 0:
                return True
            else:
                return is_polygon(coords=value['rings'])
        elif 'points' in value:
            if len(value['points']) == 0:
                return True
            else:
                return is_point(coords=value['points'])
        return False
    else:
        return False
    return False

def is_polygon(coords):
    lengths = all(len(elem) >= 4 for elem in coords)
    valid_pts = all(is_line(part) for part in coords)
    isring = all(elem[0] == elem[-1] for elem in coords)
    return lengths and isring and valid_pts
def is_line(coords):
    """
    checks to see if the line has at
    least 2 points in the list
    """
    all_valid = True
    if isinstance(coords, list_types) and \
       len(coords) > 0: # list of lists
        return all(is_point(elem) for elem in coords)
    else:
        return True
    return False
#--------------------------------------------------------------------------
def is_point(coords):
    """
    checks to see if the point has at
    least 2 coordinates in the list
    """
    if isinstance(coords, (list, tuple)) and \
       len(coords) > 1:
        for coord in coords:
            if isinstance(coord, number_type):
                return all(isinstance(v, number_type) for v in coords) and \
                       len(coords) > 1
            else:
                return is_point(coord)
    return False