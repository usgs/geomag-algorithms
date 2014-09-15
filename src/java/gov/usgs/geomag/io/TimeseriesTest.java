package gov.usgs.geomag.io;

import gov.usgs.util.ISO8601;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;


public class TimeseriesTest {

	/** Object for instance tests. */
	private Timeseries instance;

	/**
	 * Create object for instance tests.
	 */
	@Before
	public void setup () {
		Date start = ISO8601.parse("2014-01-01T01:01:00Z");
		Date end = ISO8601.parse("2014-01-01T01:01:04Z");
		instance = new Timeseries(start, end,
				getList(new String[] {"1.0",  "1.1",  "1.2", "1.3", "1.4"}));
	}

	/**
	 * Test the getSampleTime method.
	 */
	@Test
	public void testInstanceGetSampleTime() {
		Assert.assertNull("returns null when index before series start",
				instance.getSampleTime(-1));
		Assert.assertNull("returns null when index after series end",
				instance.getSampleTime(instance.getSamples().size()));
		Date expected = ISO8601.parse("2014-01-01T01:01:01Z");
		Assert.assertEquals("second sample is one second after first",
				expected, instance.getSampleTime(1));
	}

	/**
	 * Test the getSampleIndex method.
	 */
	@Test
	public void testInstanceGetSampleIndex() {
		Assert.assertNull("returns null when time before series start",
				instance.getSampleIndex(ISO8601.parse("2014-01-01T01:00:59Z")));
		Assert.assertNull("returns null when time after series end",
				instance.getSampleIndex(ISO8601.parse("2014-01-01T01:01:05Z")));
		Assert.assertEquals("second sample is one second after first",
				new Integer(1),
				instance.getSampleIndex(ISO8601.parse("2014-01-01T01:01:01Z")));

		Assert.assertNull("returns null when time not exactly at sample",
				instance.getSampleIndex(ISO8601.parse("2014-01-01T01:01:01.001Z")));
		Assert.assertEquals("rounds to nearest sample when exact is false",
				new Integer(1),
				instance.getSampleIndex(ISO8601.parse("2014-01-01T01:01:01.001Z"),
						false));
		Assert.assertEquals("rounds to nearest sample when exact is false",
				new Integer(2),
				instance.getSampleIndex(ISO8601.parse("2014-01-01T01:01:01.5Z"),
						false));
	}

	/**
	 * Test the static computeSampleTime method.
	 */
	@Test
	public void testStaticComputeSampleTime () {
		Date start = ISO8601.parse("2014-01-01T01:01:00Z");
		Date end = ISO8601.parse("2014-01-01T01:02:00Z");
		// 61st second (one based)
		Assert.assertEquals("end date matches using seconds", end,
				Timeseries.computeSampleTime(60, start, Timeseries.RATE_SECOND));
		// 2nd minute (one based)
		Assert.assertEquals("end date matches using minutes", end,
				Timeseries.computeSampleTime(1, start, Timeseries.RATE_MINUTE));
	}

	/**
	 * Test the static computeSampleIndex method.
	 */
	@Test
	public void testStaticComputeSampleIndex () {
		Date start = ISO8601.parse("2014-01-01T01:01:00Z");
		Date end = ISO8601.parse("2014-01-01T01:02:00Z");
		// 61st second (one based)
		Assert.assertEquals("sample index matches using seconds", 60,
				Timeseries.computeSampleIndex(end, start, Timeseries.RATE_SECOND));
		// 2nd minute (one based)
		Assert.assertEquals("sample index matches using minutes", 1,
				Timeseries.computeSampleIndex(end, start, Timeseries.RATE_MINUTE));
	}

	/**
	 * Test the static computeSampleRate method.
	 */
	@Test
	public void testStaticComputeSampleRate () {
		Date start = ISO8601.parse("2014-01-01T01:01:00Z");
		Date end = ISO8601.parse("2014-01-01T01:02:00Z");
		// one sample for each second (end - start + 1)
		Assert.assertEquals("sample rate matches using seconds",
				Timeseries.RATE_SECOND,
				Timeseries.computeSampleRate(61, start, end));
		// one sample for each minute (end - start + 1)
		Assert.assertEquals("sample rate matches using minutes",
				Timeseries.RATE_MINUTE,
				Timeseries.computeSampleRate(2, start, end));
	}

	/**
	 * Test the static merge method.
	 */
	@Test
	public void testStaticMerge () {
		Date start = ISO8601.parse("2014-01-01T01:01:00Z");
		Date end = ISO8601.parse("2014-01-01T01:01:04Z");
		Timeseries primary = new Timeseries(start, end,
				getList(new String[] {null,  null,  null, "1.3", null}));
		Timeseries secondary = new Timeseries(start, end,
				getList(new String[] {null,  "2.1", null, "2.3", "2.4"}));
		Timeseries tertiary = new Timeseries(start, end,
				getList(new String[] {"3.0", null,  null, "3.3", null}));
		Timeseries merged = Timeseries.merge(
				new Timeseries[] {primary, secondary, tertiary});
		Assert.assertEquals("start time matches", start, merged.getStartTime());
		Assert.assertEquals("end time matches", end, merged.getEndTime());
		Assert.assertEquals("rate matches", Timeseries.RATE_SECOND,
				merged.getSampleRate());
		// data from tertiary
		// data from secondary
		// null in all
		// data from primary
		// data from secondary
		Assert.assertEquals("samples merge as expected",
				getList(new String[] {"3.0", "2.1", null, "1.3", "2.4"}),
				merged.getSamples());
	}

	/**
	 * Utility method for building testing data.
	 *
	 * @param data an array of null or string values to convert to BigDecimals.
	 * @return list containing BigDecimal objects, or nulls.
	 */
	private ArrayList<BigDecimal> getList(final String[] data) {
		ArrayList<BigDecimal> list = new ArrayList<BigDecimal>();
		for (String item : data) {
			list.add(item == null ? null : new BigDecimal(item));
		}
		return list;
	}

}
