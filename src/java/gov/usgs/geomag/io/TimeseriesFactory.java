package gov.usgs.geomag.io;

import java.io.IOException;
import java.util.Date;

public interface TimeseriesFactory {

	/**
	 * Retrieve timeseries data for a specified observatory and component.
	 *
	 * @param observatory the observatory to fetch.
	 * @param component the component to fetch.
	 * @param starttime the time of the first sample.
	 * @param endtime the time of the last sample.
	 */
	public Timeseries getTimeseries(String observatory, String component,
			Date starttime, Date endtime) throws IOException;

}
