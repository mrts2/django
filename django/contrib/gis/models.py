"""
 Imports the SpatialRefSys and GeometryColumns models dependent on the
 spatial database backend.
"""
import re
from django.conf import settings

# Checking for the presence of GDAL (needed for the SpatialReference object)
from django.contrib.gis.gdal import HAS_GDAL
if HAS_GDAL:
    from django.contrib.gis.gdal import SpatialReference

class SpatialRefSysMixin(object):
    """
    The SpatialRefSysMixin is a class used by the database-dependent
    SpatialRefSys objects to reduce redundnant code.
    """

    # For pulling out the spheroid from the spatial reference string. This
    # regular expression is used only if the user does not have GDAL installed.
    #  TODO: Flattening not used in all ellipsoids, could also be a minor axis, or 'b'
    #        parameter.
    spheroid_regex = re.compile(r'.+SPHEROID\[\"(?P<name>.+)\",(?P<major>\d+(\.\d+)?),(?P<flattening>\d{3}\.\d+),')
    
    # For pulling out the units on platforms w/o GDAL installed.
    # TODO: Figure out how to pull out angular units of projected coordinate system and
    # fix for LOCAL_CS types.  GDAL should be highly recommended for performing 
    # distance queries.
    units_regex = re.compile(r'.+UNIT ?\["(?P<unit_name>[\w \'\(\)]+)", ?(?P<unit>[\d\.]+)(,AUTHORITY\["(?P<unit_auth_name>[\w \'\(\)]+)","(?P<unit_auth_val>\d+)"\])?\]([\w ]+)?(,AUTHORITY\["(?P<auth_name>[\w \'\(\)]+)","(?P<auth_val>\d+)"\])?\]$')
    
    @property
    def srs(self):
        """
        Returns a GDAL SpatialReference object, if GDAL is installed.
        """
        if HAS_GDAL:
            if hasattr(self, '_srs'):
                # Returning a clone of the cached SpatialReference object.
                return self._srs.clone()
            else:
                # Attempting to cache a SpatialReference object.

                # Trying to get from WKT first.
                try:
                    self._srs = SpatialReference(self.wkt)
                    return self.srs
                except Exception, msg:
                    pass
                
                raise Exception('Could not get OSR SpatialReference from WKT: %s\nError:\n%s' % (self.wkt, msg))
        else:
            raise Exception('GDAL is not installed.')

    @property
    def ellipsoid(self):
        """
        Returns a tuple of the ellipsoid parameters:
        (semimajor axis, semiminor axis, and inverse flattening).
        """
        if HAS_GDAL:
            return self.srs.ellipsoid
        else:
            m = self.spheroid_regex.match(self.wkt)
            if m: return (float(m.group('major')), float(m.group('flattening')))
            else: return None

    @property
    def name(self):
        "Returns the projection name."
        return self.srs.name

    @property
    def spheroid(self):
        "Returns the spheroid for this spatial reference."
        return self.srs['spheroid']

    @property
    def datum(self):
        "Returns the datum for this spatial reference."
        return self.srs['datum']

    @property
    def projected(self):
        "Is this Spatial Reference projected?"
        if HAS_GDAL:
            return self.srs.projected
        else:
            return self.wkt.startswith('PROJCS')

    @property
    def local(self):
        "Is this Spatial Reference local?"
        if HAS_GDAL:
            return self.srs.local
        else:
            return self.wkt.startswith('LOCAL_CS')

    @property
    def geographic(self):
        "Is this Spatial Reference geographic?"
        if HAS_GDAL:
            return self.srs.geographic
        else:
            return self.wkt.startswith('GEOGCS')

    @property
    def linear_name(self):
        "Returns the linear units name."
        if HAS_GDAL:
            return self.srs.linear_name
        elif self.geographic: 
            return None
        else:
            m = self.units_regex.match(self.wkt)
            return m.group('unit_name')
                
    @property
    def linear_units(self):
        "Returns the linear units."
        if HAS_GDAL:
            return self.srs.linear_units
        elif self.geographic:
            return None
        else:
            m = self.units_regex.match(self.wkt)
            return m.group('unit')

    @property
    def angular_name(self):
        "Returns the name of the angular units."
        if HAS_GDAL:
            return self.srs.angular_name
        elif self.projected:
            return None
        else:
            m = self.units_regex.match(self.wkt)
            return m.group('unit_name')

    @property
    def angular_units(self):
        "Returns the angular units."
        if HAS_GDAL:
            return self.srs.angular_units
        elif self.projected:
            return None
        else:
            m = self.units_regex.match(self.wkt)
            return m.group('unit')

    @property
    def units(self):
        "Returns a tuple of the units and the name."
        if self.projected or self.local:
            return (self.linear_units, self.linear_name)
        elif self.geographic:
            return (self.angular_units, self.angular_name)
        else:
            return (None, None)

    @classmethod
    def get_units(cls, wkt):
        """
        Class method used by GeometryField on initialization to
        retrive the units on the given WKT, without having to use
        any of the database fields.
        """
        if HAS_GDAL:
            return SpatialReference(wkt).units
        else:
            m = cls.units_regex.match(wkt)
            return m.group('unit'), m.group('unit_name')

    def __unicode__(self):
        """
        Returns the string representation.  If GDAL is installed,
        it will be 'pretty' OGC WKT.
        """
        try:
            return unicode(self.srs)
        except:
            return unicode(self.wkt)

# The SpatialRefSys and GeometryColumns models
if settings.DATABASE_ENGINE == 'postgresql_psycopg2':
    from django.contrib.gis.db.backend.postgis.models import GeometryColumns, SpatialRefSys
elif settings.DATABASE_ENGINE == 'oracle':
    from django.contrib.gis.db.backend.oracle.models import GeometryColumns, SpatialRefSys
else:
    raise NotImplementedError('No SpatialRefSys or GeometryColumns models for backend: %s' % settings.DATABASE_ENGINE)