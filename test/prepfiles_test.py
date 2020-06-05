from geomagio.pcdcp.PCDCPParser import PCDCPParser
from geomagio.edge import EdgeFactory
from numpy.testing import assert_almost_equal


def test_prepfiles_raw():
    # gather raw example file from magproc
    pcdcp = PCDCPParser()
    pcdcp.parse(open("etc/prepfiles/CMO2020061.raw").read())
    h_data = pcdcp.data["H"]
    e_data = pcdcp.data["E"]
    z_data = pcdcp.data["Z"]
    f_data = pcdcp.data["F"]
    times = pcdcp.times

    pcdcp.parse(open("etc/prepfiles/CMO202061_cmd.raw").read())
    result_h_data = pcdcp.data["H"]
    result_e_data = pcdcp.data["E"]
    result_z_data = pcdcp.data["Z"]
    result_f_data = pcdcp.data["F"]
    result_times = pcdcp.times

    assert_almost_equal(result_h_dat], h_data, decimal=3)
    assert_almost_equal(result_e_data, e_data, decimal=3)
    assert_almost_equal(result_z_data], z_data, decimal=3)
    assert_almost_equal(result_f_data, f_data, decimal=3)
