"""
This is a port from `spatial_efd` found here: https://spatial-efd.readthedocs.io/en/latest/index.html
"""
import warnings
import numpy as np
import matplotlib.pyplot as plt
import os.path as path
from shutil import copy2
from arcgis.geometry import Polygon

###########################################################################
class EFDAnalysis(object):
    _geom = None
    _points = None
    _X = None
    _Y = None
    _centroid = None
    #----------------------------------------------------------------------
    def __init__(self, geom:Polygon, normalize:bool=True, init:bool=False):
        self._geom = geom
        self._normalize = normalize
        if init:
            self._X, self._Y, self._centroid = \
                _process_geometry(geometry=geom, norm=normalize)
    #----------------------------------------------------------------------
    def normalize_efd(self, coeffs, size_invariant=True):
        '''
        Normalize the Elliptical Fourier Descriptor coefficients for a polygon.
    
        Implements Kuhl and Giardina method of normalizing the coefficients
        An, Bn, Cn, Dn. Performs 3 separate normalizations. First, it makes the
        data location invariant by re-scaling the data to a common origin.
        Secondly, the data is rotated with respect to the major axis. Thirdly,
        the coefficients are normalized with regard to the absolute value of A_1.
        This code is adapted from the pyefd module. See the original paper for
        more detail:
    
        Kuhl, FP and Giardina, CR (1982). Elliptic Fourier features of a closed
        contour. Computer graphics and image processing, 18(3), 236-258.
    
        Args:
            coeffs (numpy.ndarray): A numpy array of shape (n, 4) representing the
                four coefficients for each harmonic computed.
            size_invariant (bool): Set to True (the default) to perform the third
                normalization and false to return the data withot this processing
                step. Set this to False when plotting a comparison between the
                input data and the Fourier ellipse.
    
        Returns:
            tuple: A tuple consisting of a numpy.ndarray of shape (harmonics, 4)
                representing the four coefficients for each harmonic computed and
                the rotation in degrees applied to the normalized contour.
        '''    
        return _normalize_efd(coeffs, size_invariant=size_invariant)
    #----------------------------------------------------------------------
    @property
    def geometry(self) -> Polygon:
        """
        returns the original geometry
        
        :returns: Polygon
        """
        return self._geom
    #----------------------------------------------------------------------
    @property
    def normalized(self) -> bool:
        """Gets/Sets the Normalization Parameter of the Parameters"""
        return self._normalize
    #----------------------------------------------------------------------
    @normalized.setter
    def normalized(self, norm:bool):
        """Gets/Sets the Normalization Parameter of the Parameters"""
        if isinstance(norm, bool) and norm != self._normalize:
            self._normalize = norm
        elif isinstance(norm, bool) == False:
            raise ValueError("`norm` must be a Boolean Value (True/False)")
    #----------------------------------------------------------------------
    @property    
    def X(self):
        """the X-Coordinates"""
        if self._X is None:
            self._X, self._Y, self._centroid = \
                _process_geometry(geometry=self._geom, norm=self._normalize)
        return self._X
    #----------------------------------------------------------------------
    @property    
    def Y(self):
        """the Y-Coordinates"""
        if self._Y is None:
            self._X, self._Y, self._centroid = \
                _process_geometry(geometry=self._geom, norm=self._normalize)
        return self._Y
    #----------------------------------------------------------------------
    @property
    def centroid(self) -> list:
        """
        Returns the centroid of the elliptical descriptor
        
        :returns: list
        
        """
        if self._centroid is None:
            self._X, self._Y, self._centroid = \
                _process_geometry(geometry=self._geom, norm=self._normalize)
        return self._centroid
    #----------------------------------------------------------------------
    @property
    def nyquist(self):
        """
        Returns the maximum number of harmonics that can be computed for a given
        polygon, the nyquist freqency.

        See this paper for details:
        C. Costa et al. / Postharvest Biology and Technology 54 (2009) 38-47
        
        :returns: Integer

        """
        return _nyquist(X=self.X)
    #----------------------------------------------------------------------
    def fourier_power(self, coeffs, threshold=.999):
        '''
        Compute the total Fourier power and find the minium number of harmonics
        required to exceed the threshold fraction of the total power.
    
        This is a good method for identifying the number of harmonics to use to
        describe a polygon. For more details see:
    
        C. Costa et al. / Postharvest Biology and Technology 54 (2009) 38-47
    
        Warning:
            The number of coeffs must be >= the nyquist freqency.
    
        Args:
            coeffs (numpy.ndarray): A numpy array of shape (n, 4) representing the
                four coefficients for each harmonic computed.
            
            threshold (float): The threshold fraction of the total Fourier power,
                the default is 0.9999.
    
        Returns:
            int: The number of harmonics required to represent the contour above
            the threshold Fourier power.
    
        '''
        X = self.X
        return _fourier_power(coeffs, X, threshold=threshold)
    #----------------------------------------------------------------------
    def calculate_efd(self, harmonics=10):
        """
        Compute the Elliptical Fourier Descriptors for a polygon.

        Implements Kuhl and Giardina method of computing the coefficients
        An, Bn, Cn, Dn for a specified number of harmonics. This code is adapted
        from the pyefd module. See the original paper for more detail:
    
        Kuhl, FP and Giardina, CR (1982). Elliptic Fourier features of a closed
        contour. Computer graphics and image processing, 18(3), 236-258.
    
        Args:
            
            harmonics (int): The number of harmonics to compute for the given
                shape, defaults to 10.
    
        Returns:
            numpy.ndarray: A numpy array of shape (harmonics, 4) representing the
            four coefficients for each harmonic computed.
        """
        return _calculate_EFD(X=self.X, Y=self.Y, harmonics=harmonics)
##########################################################################
def _rotate_contour(X, Y, rotation, centroid):
    '''
    Rotates a contour about a point by a given amount expressed in degrees.

    Operates by calling rotatePoint() on each x,y pair in turn. X and Y must
    have the same dimensions.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.
        rotation (float): The angle in degrees for the contour to be rotated
            by.
        centroid (tuple): A tuple containing the x,y coordinates of the
            centroid to rotate the contour about.

    Returns:
        tuple: A tuple containing a list of x coordinates and a list of y
        coordinates.
    '''

    rxs = []
    rys = []

    for nx, ny in zip(X, Y):
        rx, ry = _rotatePoint((nx, ny), centroid, rotation)
        rxs.append(rx)
        rys.append(ry)

    return rxs, rys
#--------------------------------------------------------------------------
def _norm_contour(X, Y, rawCentroid):
    '''
    Normalize the coordinates which make up a contour.

    Rescale the coordinates to values between 0 and 1 in both the x and y
    directions. The normalizing is performed using x or y width of the minimum
    bounding rectangle of the contour, whichever is largest. X and Y must have
    the same dimensions.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.
        rawCentroid (tuple): A tuple containing the x,y coordinates of the
            centroid of the contour.

    Returns:
        tuple: A tuple containing a list of normalized x coordinates, a list of
        normalized y coordinate and the normalized centroid.
    '''

    # find longest axis of rotated shape
    xwidth, ywidth, xmin, ymin = _getBBoxDimensions(X, Y)
    if (xwidth > ywidth):
        normshape = xwidth
    elif (ywidth >= xwidth):
        normshape = ywidth

    norm_x = [(value - xmin) / normshape for value in X]
    norm_y = [(value - ymin) / normshape for value in Y]

    centroid = ((rawCentroid[0] - xmin) / normshape,
                (rawCentroid[1] - ymin) / normshape)

    return norm_x, norm_y, centroid
#--------------------------------------------------------------------------
def _close_contour(X, Y):
    '''
    Close an opened polygon.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.

    Returns:
        tuple: A tuple containing the X and Y lists of coordinates where the
        first and last elements are equal.
    '''
    if ((X[0] != X[-1]) or (Y[0] != Y[-1])):
        X = X + [X[0]]
        Y = Y + [Y[0]]

    return X, Y
#--------------------------------------------------------------------------
def _contour_area(X, Y):
    '''
    Compute the area of an irregular polygon.

    Ensures the contour is closed before processing, but does not modify
    X or Y outside the scope of this method. Algorithm taken from
    http://paulbourke.net/geometry/polygonmesh/.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.

    Returns:
        float: The area of the input polygon.
    '''

    # Check the contour provided is closed
    X, Y = _close_contour(X, Y)

    Sum = 0

    for i in range(len(X) - 1):
        Sum += (X[i] * Y[i + 1]) - (X[i + 1] * Y[i])

    return abs(0.5 * Sum)
#--------------------------------------------------------------------------
def _contour_centroid(X, Y):
    '''
    Compute the centroid of an irregular polygon.

    Ensures the contour is closed before processing, but does not modify
    X or Y outside the scope of this method. Algorithm taken from
    http://paulbourke.net/geometry/polygonmesh/.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.

    Returns:
        tuple: A tuple containing the (x,y) coordinate of the center of the
        input polygon.
    '''

    # Check the contour provided is closed
    X, Y = _close_contour(X, Y)

    Area = _contour_area(X, Y)

    Cx = 0
    Cy = 0

    for i in range(len(X) - 1):
        const = (X[i] * Y[i + 1]) - (X[i + 1] * Y[i])

        Cx += (X[i] + X[i + 1]) * const
        Cy += (Y[i] + Y[i + 1]) * const

    AreaFactor = (1 / (6 * Area))

    Cx *= AreaFactor
    Cy *= AreaFactor

    return (abs(Cx), abs(Cy))
#--------------------------------------------------------------------------
def _calculate_EFD(X, Y, harmonics=10):
    '''
    Compute the Elliptical Fourier Descriptors for a polygon.

    Implements Kuhl and Giardina method of computing the coefficients
    An, Bn, Cn, Dn for a specified number of harmonics. This code is adapted
    from the pyefd module. See the original paper for more detail:

    Kuhl, FP and Giardina, CR (1982). Elliptic Fourier features of a closed
    contour. Computer graphics and image processing, 18(3), 236-258.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.
        harmonics (int): The number of harmonics to compute for the given
            shape, defaults to 10.

    Returns:
        numpy.ndarray: A numpy array of shape (harmonics, 4) representing the
        four coefficients for each harmonic computed.
    '''
    contour = np.array([(x, y) for x, y in zip(X, Y)])

    dxy = np.diff(contour, axis=0)
    dt = np.sqrt((dxy ** 2).sum(axis=1))
    t = np.concatenate([([0, ]), np.cumsum(dt)]).reshape(-1, 1)
    T = t[-1]

    phi = (2. * np.pi * t)/T

    coeffs = np.zeros((harmonics, 4))

    n = np.arange(1, harmonics + 1)
    const = T / (2 * n * n * np.pi * np.pi)
    phi_n = phi * n
    d_cos_phi_n = np.cos(phi_n[1:, :]) - np.cos(phi_n[:-1, :])
    d_sin_phi_n = np.sin(phi_n[1:, :]) - np.sin(phi_n[:-1, :])
    a_n = const * np.sum((dxy[:, 1] / dt).reshape(-1, 1) * d_cos_phi_n, axis=0)
    b_n = const * np.sum((dxy[:, 1] / dt).reshape(-1, 1) * d_sin_phi_n, axis=0)
    c_n = const * np.sum((dxy[:, 0] / dt).reshape(-1, 1) * d_cos_phi_n, axis=0)
    d_n = const * np.sum((dxy[:, 0] / dt).reshape(-1, 1) * d_sin_phi_n, axis=0)

    coeffs = np.vstack((a_n, -1 * b_n, c_n, -1 * d_n)).T
    return coeffs
#--------------------------------------------------------------------------
def _inverse_transform(coeffs, locus=(0, 0), n_coords=300, harmonic=10):
    '''
    Perform an inverse fourier transform to convert the coefficients back into
    spatial coordinates.

    Implements Kuhl and Giardina method of computing the performing the
    transform for a specified number of harmonics. This code is adapted
    from the pyefd module. See the original paper for more detail:

    Kuhl, FP and Giardina, CR (1982). Elliptic Fourier features of a closed
    contour. Computer graphics and image processing, 18(3), 236-258.

    Args:
        coeffs (numpy.ndarray): A numpy array of shape (harmonic, 4)
            representing the four coefficients for each harmonic computed.
        locus (tuple): The x,y coordinates of the centroid of the contour being
            generated. Use calculate_dc_coefficients() to generate the correct
            locus for a shape.
        n_coords (int): The number of coordinate pairs to compute. A larger
            value will result in a more complex shape at the expense of
            increased computational time. Defaults to 300.
        harmonics (int): The number of harmonics to be used to generate
            coordinates, defaults to 10. Must be <= coeffs.shape[0]. Supply a
            smaller value to produce coordinates for a more generalized shape.

    Returns:
        numpy.ndarray: A numpy array of shape (harmonics, 4) representing the
        four coefficients for each harmonic computed.
    '''

    t = np.linspace(0, 1, n_coords).reshape(1, -1)
    n = np.arange(harmonic).reshape(-1, 1)

    xt = (np.matmul(coeffs[:harmonic, 2].reshape(1, -1),
                    np.cos(2. * (n + 1) * np.pi * t)) +
          np.matmul(coeffs[:harmonic, 3].reshape(1, -1),
                    np.sin(2. * (n + 1) * np.pi * t)) +
          locus[0])

    yt = (np.matmul(coeffs[:harmonic, 0].reshape(1, -1),
                    np.cos(2. * (n + 1) * np.pi * t)) +
          np.matmul(coeffs[:harmonic, 1].reshape(1, -1),
                    np.sin(2. * (n + 1) * np.pi * t)) +
          locus[1])

    return xt.ravel(), yt.ravel()
#--------------------------------------------------------------------------
def _InitPlot():
    '''
    Set up the axes for plotting, ensuring that x and y dimensions are equal.

    Returns:
        matplotlib.axes.Axes: Matplotlib axis instance.
    '''
    ax = plt.gca()
    ax.axis('equal')

    return ax
#--------------------------------------------------------------------------
def _plot_ellipse(x, y, color='k', width=1.):
    '''
    Plots an ellipse represented as a series of x and y coordinates on a given
    axis.

    Args:
        ax (matplotlib.axes.Axes): Matplotlib axis instance.
        x (list): A list (or numpy array) of x coordinate values.
        y (list): A list (or numpy array) of y coordinate values.
        color (string): A matplotlib color string to color the line used to
           plot the ellipse. Defaults to k (black).
        width (float): The width of the plotted line. Defaults to 1.
    '''
    ax = _InitPlot()
    ax.plot(x, y, color, linewidth=width)
    #ax.set_title('Harmonic: {0}'.format(harmonic))
    plt.show();   
    return ax
#--------------------------------------------------------------------------
def _plotComparison(coeffs, harmonic, x, y, rotation=0, color1='k',
                   width1=2, color2='r', width2=1):
    '''
    Convenience function which plots an EFD ellipse and a shapefile polygon in
    the same coordate system.

    Warning:
        If passing in normalized coefficients, they must be created with the
        size_invariant parameter set to False.

    Args:
        ax (matplotlib.axes.Axes): Matplotlib axis instance.
        x (list): A list (or numpy array) of x coordinate values.
        y (list): A list (or numpy array) of y coordinate values.
        rotation (float): The angle in degrees for the contour to be rotated
            by. Generated by normalize_efd(). Leave as 0 if non-normalized
            coefficients are being plotted.
        harmonic (int): The number of harmonics to be used to generate
            coordinates. Must be <= coeffs.shape[0]. Supply a smaller value to
            produce coordinates for a more generalized shape.
        color1 (string): A matplotlib color string to color the line used to
            plot the Fourier ellipse. Defaults to k (black).
        width1 (float): The width of the plotted fourier ellipse. Defaults
            to 1.
        color2 (string): A matplotlib color string to color the line used to
            plot the shapefile. Defaults to r (red).
        width2 (float): The width of the plotted shapefile. Defaults to 1.
    '''
    locus = _calculate_dc_coefficients(x, y)
    xt, yt = _inverse_transform(coeffs, locus=locus, harmonic=harmonic)

    if rotation:
        x, y = _rotate_contour(x, y, rotation, locus)
    ax = _InitPlot()
    _plot_ellipse(ax, xt, yt, color1, width1)
    _plot_ellipse(ax, x, y, color2, width2)
    return ax
#--------------------------------------------------------------------------
def _average_coefficients(coeffList):
    '''
    Average the coefficients contained in the list of coefficient arrays,
    coeffList.

    This method is outlined in:

    2-D particle shape averaging and comparison using Fourier descriptors:
    Powder Technology Volume 104, Issue 2, 1 September 1999, Pages 180-189

    Args:
        coeffList (list): A list of coefficient arrays to be averaged.

    Returns:
        numpy.ndarray: A numpy array containing the average An, Bn, Cn, Dn
        coefficient values.
    '''

    nHarmonics = coeffList[0].shape[0]
    coeffsum = np.zeros((nHarmonics, 4))

    for coeff in coeffList:
        coeffsum += coeff

    coeffsum /= float(len(coeffList))

    return coeffsum
#--------------------------------------------------------------------------
def _average_SD(coeffList, avgcoeffs):
    '''
    Use the coefficients contained in the list of coefficient arrays,
    coeffList, and the average coefficient values to compute the standard
    deviation of series of ellipses.

    This method is outlined in:

    2-D particle shape averaging and comparison using Fourier descriptors:
    Powder Technology Volume 104, Issue 2, 1 September 1999, Pages 180-189

    Args:
        coeffList (list): A list of coefficient arrays to be averaged.
        avgcoeffs (numpy.ndarray): A numpy array containing the average
            coefficient values, generated by calling average_coefficients().

    Returns:
        numpy.ndarray: A numpy array containing the standard deviation
        An, Bn, Cn, Dn coefficient values.
    '''
    nHarmonics = avgcoeffs.shape[0]
    coeffsum = np.zeros((nHarmonics, 4))

    for coeff in coeffList:
        coeffsum += (coeff ** 2)

    return (coeffsum / float(len(coeffList) - 1)) - (avgcoeffs ** 2)
#--------------------------------------------------------------------------
def _nyquist(X):
    '''
    Returns the maximum number of harmonics that can be computed for a given
    contour, the nyquist freqency.

    See this paper for details:
    C. Costa et al. / Postharvest Biology and Technology 54 (2009) 38-47

    Args:
        X (list): A list (or numpy array) of x coordinate values.

    Returns:
        int: The nyquist frequency, expressed as a number of harmonics.
    '''
    return len(X) // 2
#--------------------------------------------------------------------------
def _fourier_power(coeffs, X, threshold=0.9999):
    '''
    Compute the total Fourier power and find the minium number of harmonics
    required to exceed the threshold fraction of the total power.

    This is a good method for identifying the number of harmonics to use to
    describe a polygon. For more details see:

    C. Costa et al. / Postharvest Biology and Technology 54 (2009) 38-47

    Warning:
        The number of coeffs must be >= the nyquist freqency.

    Args:
        coeffs (numpy.ndarray): A numpy array of shape (n, 4) representing the
            four coefficients for each harmonic computed.
        X (list): A list (or numpy array) of x coordinate values.
        threshold (float): The threshold fraction of the total Fourier power,
            the default is 0.9999.

    Returns:
        int: The number of harmonics required to represent the contour above
        the threshold Fourier power.

    '''
    rnyquist = _nyquist(X)

    totalPower = 0
    currentPower = 0

    for n in range(rnyquist):
            totalPower += ((coeffs[n, 0] ** 2) + (coeffs[n, 1] ** 2) +
                           (coeffs[n, 2] ** 2) + (coeffs[n, 3] ** 2)) / 2

    for i in range(rnyquist):
        currentPower += ((coeffs[i, 0] ** 2) + (coeffs[i, 1] ** 2.) +
                         (coeffs[i, 2] ** 2) + (coeffs[i, 3] ** 2.)) / 2

        if (currentPower / totalPower) > threshold:
            return i + 1
#--------------------------------------------------------------------------
def _normalize_efd(coeffs, size_invariant=True):
    '''
    Normalize the Elliptical Fourier Descriptor coefficients for a polygon.

    Implements Kuhl and Giardina method of normalizing the coefficients
    An, Bn, Cn, Dn. Performs 3 separate normalizations. First, it makes the
    data location invariant by re-scaling the data to a common origin.
    Secondly, the data is rotated with respect to the major axis. Thirdly,
    the coefficients are normalized with regard to the absolute value of A_1.
    This code is adapted from the pyefd module. See the original paper for
    more detail:

    Kuhl, FP and Giardina, CR (1982). Elliptic Fourier features of a closed
    contour. Computer graphics and image processing, 18(3), 236-258.

    Args:
        coeffs (numpy.ndarray): A numpy array of shape (n, 4) representing the
            four coefficients for each harmonic computed.
        size_invariant (bool): Set to True (the default) to perform the third
            normalization and false to return the data withot this processing
            step. Set this to False when plotting a comparison between the
            input data and the Fourier ellipse.

    Returns:
        tuple: A tuple consisting of a numpy.ndarray of shape (harmonics, 4)
            representing the four coefficients for each harmonic computed and
            the rotation in degrees applied to the normalized contour.
    '''
    # Make the coefficients have a zero phase shift from
    # the first major axis. Theta_1 is that shift angle.
    theta_1 = (0.5 * np.arctan2(2 * ((coeffs[0, 0] * coeffs[0, 1]) +
               (coeffs[0, 2] * coeffs[0, 3])),
              ((coeffs[0, 0] ** 2) -
               (coeffs[0, 1] ** 2) +
               (coeffs[0, 2] ** 2) -
               (coeffs[0, 3] ** 2))))

    # Rotate all coefficients by theta_1.
    for n in range(1, coeffs.shape[0] + 1):
        coeffs[n - 1, :] = np.dot(np.array([[coeffs[n - 1, 0],
                                  coeffs[n - 1, 1]], [coeffs[n - 1, 2],
                                                      coeffs[n - 1, 3]]]),
                                  np.array([[np.cos(n * theta_1),
                                           -np.sin(n * theta_1)],
                                           [np.sin(n * theta_1),
                                           np.cos(n * theta_1)]])).flatten()

    # Make the coefficients rotation invariant by rotating so that
    # the semi-major axis is parallel to the x-axis.
    psi_1 = np.arctan2(coeffs[0, 2], coeffs[0, 0])
    psi_r = np.array([[np.cos(psi_1), np.sin(psi_1)],
                     [-np.sin(psi_1), np.cos(psi_1)]])

    # Rotate all coefficients by -psi_1.
    for n in range(1, coeffs.shape[0] + 1):
        rot = np.array([[coeffs[n - 1, 0], coeffs[n - 1, 1]],
                        [coeffs[n - 1, 2], coeffs[n - 1, 3]]])
        coeffs[n - 1, :] = psi_r.dot(rot).flatten()

    if size_invariant:
        # Obtain size-invariance by normalizing.
        coeffs /= np.abs(coeffs[0, 0])

    return coeffs, np.degrees(psi_1)
#--------------------------------------------------------------------------
def _calculate_dc_coefficients(X, Y):
    '''
    Compute the dc coefficients, used as the locus when calling
    inverse_transform().

    This code is adapted from the pyefd module. See the original paper for
    more detail:

    Kuhl, FP and Giardina, CR (1982). Elliptic Fourier features of a closed
    contour. Computer graphics and image processing, 18(3), 236-258.

    Args:
        X (list): A list (or numpy array) of x coordinate values.
        Y (list): A list (or numpy array) of y coordinate values.

    Returns:
        tuple: A tuple containing the c and d coefficients.

    '''

    contour = np.array([(x, y) for x, y in zip(X, Y)])

    dxy = np.diff(contour, axis=0)
    dt = np.sqrt((dxy ** 2).sum(axis=1))
    t = np.concatenate([([0, ]), np.cumsum(dt)])
    T = t[-1]

    diff = np.diff(t ** 2)
    xi = np.cumsum(dxy[:, 0]) - (dxy[:, 0] / dt) * t[1:]
    A0 = (1 / T) * np.sum(((dxy[:, 0] / (2 * dt)) * diff) + xi * dt)
    delta = np.cumsum(dxy[:, 1]) - (dxy[:, 1] / dt) * t[1:]
    C0 = (1 / T) * np.sum(((dxy[:, 1] / (2 * dt)) * diff) + delta * dt)

    # A0 and CO relate to the first point of the contour array as origin.
    # Adding those values to the coeffs to make them relate to true origin
    return (contour[0, 0] + A0, contour[0, 1] + C0)
#--------------------------------------------------------------------------
def _process_geometry(geometry, norm=False):
    '''
    Method to handle all the geometry processing that may be needed by the rest
    of the EFD code.

    Method which takes a single shape instance from a shapefile
    eg shp.Reader('shapefile.shp').shapeRecords()[n]
    where n is the index of the shape within a multipart geometry. This results
    in the contour, coordinate list and centroid data computed for the input
    polygon being normalized and returned to the user.

    Args:
        shapefile._ShapeRecord: A shapefile object representing the geometry
            and attributes of a single polygon from a multipart shapefile.

    Returns:
        tuple: A tuple containing a list of normalized x coordinates, a list of
        normalized y coordinates, contour (a list of [x,y] coordinate pairs,
        normalized about the shape's centroid) and the normalized coordinate
        centroid.
    '''
    x = []
    y = []
    if norm:
        return _process_geometry_norm(geometry=geometry)
    for point in geometry.points:
        x.append(point[0])
        y.append(point[1])

    centroid = _contour_centroid(x, y)

    return x, y, centroid
#--------------------------------------------------------------------------
def _process_geometry_norm(geometry):
    '''
    Method to handle all the geometry processing that may be needed by the rest
    of the EFD code. This method normalizes the input data to allow spatially
    distributed data to be plotted in the same cartesian space.

    Method which takes a single `Geometry` instance from an SeDF
    where n is the index of the shape within a multipart geometry. This results
    in the contour, coordinate list and centroid data computed for the input
    polygon being normalized and returned to the user.

    Args:
        `Geometry`: A single geometry object.

    Returns:
        tuple: A tuple containing a list of normalized x coordinates, a list of
        normalized y coordinates, contour (a list of [x,y] coordinate pairs,
        normalized about the shape's centroid) and the normalized coordinate
        centroid.
    '''
    x = []
    y = []

    for point in geometry.points:
        x.append(point[0])
        y.append(point[1])

    centroid = _contour_centroid(x, y)
    X, Y, NormCentroid = _norm_contour(x, y, centroid)

    return X, Y, NormCentroid
#--------------------------------------------------------------------------
def writeGeometry(coeffs, x, y, harmonic, sr=4326):
    '''
    Converts the Ellipse to a Polygon

    Returns:
        Polygon.

    '''

    locus = _calculate_dc_coefficients(x, y)
    xt, yt = _inverse_transform(coeffs, locus=locus, harmonic=harmonic)

    contour = [(x_, y_) for x_, y_ in zip(xt, yt)]
    return Polygon({'rings': [contour],
                    'spatialReference' : sr
                    })
#--------------------------------------------------------------------------
def _rotatePoint(point, centerPoint, angle):
    '''
    Rotates a point counter-clockwise around centerPoint.

    The angle to rotate by is supplied in degrees. Code based on:
    https://gist.github.com/somada141/d81a05f172bb2df26a2c

    Args:
        point (tuple): The point to be rotated, represented as an (x,y) tuple.
        centerPoint (tuple): The point to be rotated about, represented as
            an (x,y) tuple.
        angle (float): The angle to rotate point by, in the counter-clockwise
            direction.

    Returns:
        tuple: A tuple representing the rotated point, (x,y).
    '''
    angle = np.radians(angle)
    temp_point = point[0] - centerPoint[0], point[1] - centerPoint[1]
    temp_point = (temp_point[0] * np.cos(angle) - temp_point[1] *
                  np.sin(angle), temp_point[0] * np.sin(angle) +
                  temp_point[1] * np.cos(angle))

    temp_point = temp_point[0] + centerPoint[0], temp_point[1] + centerPoint[1]
    return temp_point[0], temp_point[1]
#--------------------------------------------------------------------------
def _getBBoxDimensions(x, y):
    '''
    Returns the width in the x and y dimensions and the maximum x and y
    coordinates for the bounding box of a given list of x and y coordinates.

    Args:
        x (list): A list (or numpy array) of x coordinate values.
        y (list): A list (or numpy array) of y coordinate values.
    Returns:
        tuple: A four-tuple representing (width in the x direction, width in
        the y direction, the minimum x coordinate and the minimum y
        coordinate).
    '''
    xmin = min(x)
    ymin = min(y)

    xmax = max(x)
    ymax = max(y)

    return xmax - xmin, ymax - ymin, xmin, ymin
