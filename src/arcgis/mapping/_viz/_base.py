import json
class _Renderer(object):
    """base renderer"""
    _dict = None
    _type = None
    _vv_color = None
    _vv_rotation = None
    _vv_size = None
    _vv_transparency = None

    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s>' % type(self).__name__
    #----------------------------------------------------------------------
    def __str__(self):
        return self.__repr__()
    #----------------------------------------------------------------------
    @property
    def json(self):
        """returns the renderer as JSON"""
        raise NotImplementedError("Not Implemented")


