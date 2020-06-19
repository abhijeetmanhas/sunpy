# Author: Rishabh Sharma <rishabh.sharma.gunner@gmail.com>
# This module was developed under funding by
# Google Summer of Code 2014

from sunpy.net.dataretriever import GenericClient

__all__ = ['EVEClient']


class EVEClient(GenericClient):
    """
    Provides access to Level 0C Extreme ultraviolet Variability Experiment (EVE) data.

    To use this client you must request Level 0 data.
    It is hosted by `LASP <http://lasp.colorado.edu/home/eve/data/data-access/>`__.

    Examples
    --------

    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2016/1/1", "2016/1/2"),
    ...                       a.Instrument.eve, a.Level("0cs"))  #doctest: +REMOTE_DATA
    >>> results  #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    2 Results from the EVEClient:
         Start Time     Source Provider  Physobs   Instrument Level
    ------------------- ------ -------- ---------- ---------- -----
    2016-01-01 00:00:00    SDO     LASP irradiance        eve   0CS
    2016-01-02 00:00:00    SDO     LASP irradiance        eve   0CS
    <BLANKLINE>
    <BLANKLINE>

    """
    baseurl = (r'http://lasp.colorado.edu/eve/data_access/evewebdata/quicklook/'
               r'L0CS/SpWx/%Y/%Y%m%d_EVE_L0CS_DIODES_1m.txt')
    extractor = ('http://lasp.colorado.edu/eve/data_access/evewebdata/quicklook/L0CS/SpWx/'
                 '{}/{:8d}_EVE_L{Level:w}_DIODES_1m.txt')

    def _makeimap(self):
        """
        Helper Function: used to hold information about source.
        """
        self.map_['source'] = 'SDO'
        self.map_['provider'] = 'LASP'
        self.map_['instrument'] = 'eve'
        self.map_['physobs'] = 'irradiance'

    @classmethod
    def _can_handle_query(cls, *query):
        """
        Answers whether client can service the query.

        Parameters
        ----------
        query : list of query objects

        Returns
        -------
        boolean
            answer as to whether client can service the query
        """
        from sunpy.net import attrs as a

        required = {a.Time, a.Instrument, a.Level}
        # Level should really be in here, but VSO doesn't correctly provide
        # Level information currently.
        optional = {}
        if not cls.check_attr_types_in_query(query, required, optional):
            return False

        matches = True
        for x in query:
            if isinstance(x, a.Instrument) and x.value.lower() != 'eve':
                matches = False
            if isinstance(x, a.Level):
                # Level can be basically anything, this function should never
                # really error. If level is a string we try and convert it to
                # an int, if it's the string "0CS" we match it. Otherwise we
                # check it's equal to 0
                value = x.value
                if isinstance(value, str):
                    if value.lower() == '0cs':
                        value = 0
                    else:
                        try:
                            value = int(value)
                        except ValueError:
                            matches = False
                if value != 0:
                    matches = False

        return matches

    @classmethod
    def register_values(cls):
        from sunpy.net import attrs
        adict = {attrs.Instrument: [
            ('EVE', 'Extreme ultraviolet Variability Experiment, which is part of the NASA Solar Dynamics Observatory mission.')],
                 attrs.Level: [
            ('0CS', 'EVE: The specific EVE client can only return Level 0C data. Any other number will use the VSO Client.')]}
        return adict
