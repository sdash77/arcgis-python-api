


def geocode(self,
            address,
            searchExtent=None,
            location=None,
            distance=None,
            outSR=None,
            category=None,
            outFields="*",
            maxLocations=20,
            magicKey=None,
            forStorage=False):
    """
    The geocode function geocodes one location per request.

    Inputs:
       address - Specifies the location to be geocoded. This can be a string
       containing the street address, place name, postal code, or POI.

        Alternatively, this can be a dictionary containing the various address fields accepted by the corresponding geocode service. These fields are listed in the addressFields property of the associated geocode service resource. For example, if the addressFields of a geocode service resource includes fields with the following names: Street, City, State and Zone, then the address argument is of the form:
        {
          Street: "1234 W Main St",
          City: "Small Town",
          State: "WA",
          Zone: "99027"
        }

       searchExtent - A set of bounding box coordinates that limit the search
        area to a specific region. This is especially useful for
        applications in which a user will search for places and
        addresses only within the current map extent.
       location - Defines an origin point location that is used with
        the distance parameter to sort geocoding candidates based upon
        their proximity to the location. The distance parameter
        specifies the radial distance from the location in meters. The
        priority of candidates within this radius is boosted relative
        to those outside the radius.
       distance - Specifies the radius of an area around a point
        location which is used to boost the rank of geocoding
        candidates so that candidates closest to the location are
        returned first. The distance value is in meters.
       outSR - The spatial reference of the x/y coordinates returned by
        a geocode request. This is useful for applications using a map
        with a spatial reference different than that of the geocode
        service.
       category - A place or address type which can be used to filter
        find results. The parameter supports input of single category
        values or multiple comma-separated values. The category
        parameter can be passed in a request with or without the text
        parameter.
       outFields - The list of fields to be returned in the response.
       maxLocation - The maximum number of locations to be returned by
        a search, up to the maximum number allowed by the service. If
        not specified, then one location will be returned.

       magicKey - The find operation retrieves results quicker when you
        pass in valid text and magicKey values than when you don't pass
        in magicKey. However, to get these advantages, you need to make
        a prior request to suggest, which provides a magicKey. This may
        or may not be relevant to your workflow.

       forStorage - Specifies whether the results of the operation will
        be persisted. The default value is false, which indicates the
        results of the operation can't be stored, but they can be
        temporarily displayed on a map for instance. If you store the
        results, in a database for example, you need to set this
        parameter to true.
    """
    pass


def reverse_geocode(self, location, distance=None, outSR=None, langCode=None, returnIntersection=False,
                    forStorage=False):
    """
    The reverseGeocode operation determines the address at a particular
    x/y location. You pass the coordinates of a point location to the
    geocoding service, and the service returns the address that is
    closest to the location.
    Input:
       location - a list defined as [X,Y] or a JSON Point
    """
    pass


def batch_geocode(self,
                  addresses,
                  sourceCountry=None,
                  category=None,
                  outSR=None):
    """
    The batch_geocode() method geocodes an entire list of addresses. Geocoding many addresses at once is also known as bulk geocoding.


    Inputs:
       addresses - A list of addresses to be geocoded.
       For passing in the location name as a single line of text —
       single field batch geocoding — use a string.
       For passing in the location name as multiple lines of text
       multifield batch geocoding — use the address fields described
       in the Geocoder documentation.
        The maximum number of addresses that can be geocoded in a
        single request is limited to the SuggestedBatchSize property of
        the locator.
        Syntax:
         addresses = ["380 New York St, Redlands, CA",
         "1 World Way, Los Angeles, CA",
         "1200 Getty Center Drive, Los Angeles, CA",
         "5905 Wilshire Boulevard, Los Angeles, CA",
         "100 Universal City Plaza, Universal City, CA 91608",
         "4800 Oak Grove Dr, Pasadena, CA 91109"]

         OR

         addresses= [{
            "Address": "380 New York St.",
            "City": "Redlands",
            "Region": "CA",
            "Postal": "92373"
        },{
            "Address": "1 World Way",
            "City": "Los Angeles",
            "Region": "CA",
            "Postal": "90045"
        }]

       sourceCountry - The sourceCountry parameter is only supported by
        geocode services published using StreetMap Premium locators.
        Added at 10.3 and only supported by geocode services published
        with ArcGIS 10.3 for Server and later versions.
       category - The category parameter is only supported by geocode
        services published using StreetMap Premium locators.
       outSR - The well-known ID of the spatial reference, or a spatial
        reference json object for the returned addresses. For a list of
        valid WKID values, see Projected coordinate systems and
        Geographic coordinate systems.
    """
    pass


def find_best_match(self,
                    address,
                    searchExtent=None,
                    location=None,
                    distance=None,
                    outSR=None,
                    category=None,
                    outFields="*", magicKey=None,
                    forStorage=False):
    """Returns the (latitude, longitude) or (y, x) coordinates of the best match for specified address"""
    pass


def suggest(self,
            text,
            location,
            distance=None,
            category=None
            ):
    """
    The result of this operation is a resource representing a list of
    suggested matches for the input text. This resource provides the
    matching text as well as a unique ID value, which links a
    suggestion to a specific place or address.
    A geocode service must meet the following requirements to support
    the suggest operation:
      The address locator from which the geocode service was published
      must support suggestions. Only address locators created using
      ArcGIS 10.3 for Desktop and later can support suggestions. See
      the Create Address Locator geoprocessing tool help topic for more
      information.
      The geocode service must have the Suggest capability enabled.
      Only geocode services published using ArcGIS 10.3 for Server or
      later support the Suggest capability.
    The suggest operation allows character-by-character auto-complete
    suggestions to be generated for user input in a client application.
    This capability facilitates the interactive search user experience
    by reducing the number of characters that need to be typed before
    a suggested match is obtained. A client application can provide a
    list of suggestions that is updated with each character typed by a
    user until the address they are looking for appears in the list.
    Inputs:
       text - The input text provided by a user that is used by the
        suggest operation to generate a list of possible matches. This
        is a required parameter.
       location -  Defines an origin point location that is used with
        the distance parameter to sort suggested candidates based on
        their proximity to the location. The distance parameter
        specifies the radial distance from the location in meters. The
        priority of candidates within this radius is boosted relative
        to those outside the radius.
        This is useful in mobile applications where a user wants to
        search for places in the vicinity of their current GPS
        location. It is also useful for web mapping applications where
        a user wants to find places within or near the map extent.
        The location parameter can be specified without specifying a
        distance. If distance is not specified, it defaults to 2000
        meters.
        The object can be an common.geometry.Point or X/Y list object
       distance - Specifies the radius around the point defined in the
        location parameter to create an area, which is used to boost
        the rank of suggested candidates so that candidates closest to
        the location are returned first. The distance value is in
        meters.
        If the distance parameter is specified, the location parameter
        must be specified as well.
        It is important to note that the location and distance
        parameters allow searches to extend beyond the specified search
        radius. They are not used to filter results, but rather to rank
        resulting candidates based on their distance from a location.
       category - The category parameter is only supported by geocode
        services published using StreetMap Premium locators.
    """
    pass
