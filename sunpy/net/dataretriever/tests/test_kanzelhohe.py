"""
This module tests the Kanzelhohe Client
"""
# This module was developed with funding provided by
# the Google Summer of Code 2016.
import pytest
import datetime

from astropy import units as u
from sunpy.time.timerange import TimeRange
from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import QueryResponse
from sunpy.net.fido_factory import UnifiedResponse
from sunpy.net import Fido
import sunpy.net.dataretriever.sources.kanzelhohe as kanzelhohe

KClient = kanzelhohe.KanzelhoheClient()


@pytest.mark.online
@pytest.mark.parametrize("timerange, wavelength, url_start, url_end",
                         [(TimeRange('2015/01/10 00:00:00', '2015/01/10 12:00:00'),
                           a.Wavelength(6563 * u.AA),
                           '2015/kanz_halph_fr_20150110_102629.fts.gz',
                           '2015/kanz_halph_fr_20150110_113524.fts.gz')])
def test_get_url_for_timerange(timerange, wavelength, url_start, url_end):
    urls = KClient._get_url_for_timerange(timerange, wavelength=wavelength)
    assert isinstance(urls, list)
    assert urls[0] == "http://cesar.kso.ac.at/halpha2k/recent/" + url_start
    assert urls[1] == "http://cesar.kso.ac.at/halpha2k/recent/" + url_end


TRANGE = a.Time('2015/12/30 00:00:00', '2015/12/31 00:05:00')


@pytest.mark.parametrize("time, instrument, wavelength, expected",
                         [(TRANGE, a.Instrument('kanzelhohe'), a.Wavelength(6563*u.AA), True),
                          (TRANGE, a.Instrument('swap'), None, False),
                          (TRANGE, None, None, False),
                          (TRANGE, a.Instrument('kanzelhohe'), a.Wavelength(32768*u.AA), True)])
def test_can_handle_query(time, instrument, wavelength, expected):
    assert KClient._can_handle_query(time, instrument, wavelength) is expected


@pytest.mark.online
def test_query():
    qr = KClient.search(a.Time('2015/01/10 00:00:00', '2015/01/10 12:00:00'),
                        a.Wavelength(6563 * u.AA))
    assert isinstance(qr, QueryResponse)
    assert len(qr) == 2
    assert qr.time_range().start.date() == datetime.date(2015, 1, 10)
    assert qr.time_range().end.date() == datetime.date(2015, 1, 10)


# This test downloads 3 files
# Each file is 4.5MB, total size
# is 13.4MB
@pytest.mark.online
@pytest.mark.parametrize("time, wavelength",
                         [(a.Time('2015/01/02 07:30:00', '2015/01/02 07:38:00'),
                           a.Wavelength(3276.8 * u.nm))])
def test_get(time, wavelength):
    qr = KClient.search(time, wavelength)
    res = KClient.get(qr)
    download_list = res.wait()
    assert len(download_list) == len(qr)


# This test downloads 3 files
# Each file is 4.5MB, total size
# is 13.4MB
@pytest.mark.online
def test_fido_query():
    qr = Fido.search(a.Time('2016/01/05 07:30:00', '2016/01/05 07:38:00'),
                     a.Instrument('kanzelhohe'), a.Wavelength(546.0 * u.nm))
    assert isinstance(qr, UnifiedResponse)
    response = Fido.fetch(qr)
    assert len(response) == qr._numfile