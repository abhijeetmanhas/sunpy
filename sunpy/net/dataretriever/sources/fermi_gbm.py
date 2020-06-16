from sunpy.net.dataretriever import GenericClient

__all__ = ['GBMClient']


class GBMClient(GenericClient):
    """
    Provides access to data from the Gamma-Ray Burst Monitor (GBM) instrument
    on board the Fermi satellite.

    Although GBMs primary objective is to detect gamma-ray bursts,
    it provides high quality high energy solar flare observations.

    The instrument consists of 12 Sodium Iodide (NaI) scintillation
    detectors, which are sensitive to an energy range of 4keV to 1MeV.
    At any one time, 6 of the NaI detectors are Sunward facing.
    The detectors are numbered 'n1' to 'n11'. This client supports the user
    to choose which detector to use through the `a.Detector <sunpy.net.attrs.Detector>` attribute.
    The default detector is 'n5'.

    The GBM data comes in daily version files in two formats:

        * CSPEC - counts accumulated every  4.096 seconds in 128 energy channels for each detector.
        * CTIME - counts accumulated every 0.256 seconds in 8 energy channels

    Both of which can be accessed through the attrs `a.Resolution <sunpy.net.attrs.Resolution>`.
    The default data type is CSPEC unless the user defines.

    Examples
    --------
    >>> from sunpy.net import Fido, attrs as a
    >>> res = Fido.search(a.Time('2015-06-21 00:00', '2015-06-23 23:59'),
    ...                   a.Instrument.gbm, a.Detector.n3,
    ...                   a.Resolution.ctime) #doctest: +REMOTE_DATA
    >>> print(res) #doctest: +REMOTE_DATA
    Results from 1 Provider:
    <BLANKLINE>
    3 Results from the GBMClient:
         Start Time     Source Provider Physobs Instrument Resolution Detector
    ------------------- ------ -------- ------- ---------- ---------- --------
    2015-06-21 00:00:00  FERMI     NASA    flux        GBM      ctime       n3
    2015-06-22 00:00:00  FERMI     NASA    flux        GBM      ctime       n3
    2015-06-23 00:00:00  FERMI     NASA    flux        GBM      ctime       n3
    <BLANKLINE>
    <BLANKLINE>
    """
    baseurl = (r'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/daily/'
               r'%Y/%m/%d/current/glg_(\w){5}_(\w){2,3}_%y%m%d_v00.pha')
    extractor = ('https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/daily/{4d}/'
                 '{2d}/{2d}/current/glg_{Resolution:5w}_{Detector:2w}_{}_v00.pha')

    def _makeimap(self):
        """
        Helper function used to hold information about source.
        """
        self.map_['source'] = 'FERMI'
        self.map_['instrument'] = 'GBM'
        self.map_['physobs'] = 'flux'
        self.map_['provider'] = 'NASA'

    @classmethod
    def _can_handle_query(cls, *query):
        """
        Answers whether a client can service the query.

        Parameters
        ----------
        query : `list`
            A list of of query objects.

        Returns
        -------
        `bool`
            `True` if this client can service the query, otherwise `False`.
        """
        chkattr = ['Time', 'Instrument', 'Detector', 'Resolution']
        chklist = [x.__class__.__name__ in chkattr for x in query]
        for x in query:
            if x.__class__.__name__ == 'Instrument' and x.value.lower() == 'gbm':
                return all(chklist)
        return False

    @classmethod
    def register_values(cls):
        from sunpy.net import attrs
        adict = {attrs.Instrument: [('GBM', 'Gamma-Ray Burst Monitor on board the Fermi satellite.')],
                 attrs.Physobs: [('CSPEC', 'counts accumulated every 4.096 seconds in 128 energy channels for each detector.'),
                                 ('CTIME', 'counts accumulated every 0.256 seconds in 8 energy channels')],
                 attrs.Detector: [
            (f"n{x}", f"GBM Detector short name for the detector NAI_{x:02}") for x in range(12)],
            attrs.Resolution: [
            ("CSPEC", "CSPEC 128 channel spectra every 4.096 seconds."),
            ("CTIME", "CTIME provides 8 channel spectra every 0.256 seconds")]
        }
        return adict


def _check_detector(detector, **kwargs):
    """
    checks to see if detector is in right format.
    """
    detector_numbers = [str(i) for i in range(12)]
    detector_list = ['n' + i for i in detector_numbers]
    if detector.lower() in detector_list:
        return detector.lower()
    elif detector in detector_numbers:
        return 'n' + detector
    else:
        raise ValueError('Detector number needs to be a string. Available detectors are n0-n11')


def _check_type(datatype, **kwargs):
    """
    checks is datatype is either "CSPEC" or "CTIME".
    """
    if not isinstance(datatype, str):
        raise ValueError(f'{datatype} is not str - either cspec or ctime')

    if datatype.lower() != 'cspec' and datatype.lower() != 'ctime':
        raise ValueError(f'{datatype} not value datatype - either cspec or ctime')
    else:
        return datatype.lower()
