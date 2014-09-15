package gov.usgs.util;

import java.util.Date;
import org.junit.Test;
import org.junit.Assert;

/**
 * Test cases for the ISO8601 utility.
 */
public class ISO8601Test {

	@Test
	public void construct() {
		new ISO8601();
	}

	/**
	 * Date should parse correctly, and when parsed from normalized format
	 * serialize identically.
	 */
	@Test
	public void testRoundtrip() {
		String str = "2001-01-01T01:23:45.678Z";

		Date time = ISO8601.parse(str);
		Assert.assertEquals("time parses correctly", 978312225678L, time.getTime());

		String roundtrip = ISO8601.format(time);
		Assert.assertEquals("time matches after roundtrip", str, roundtrip);
	}

	/**
	 * Invalid date formats should return null.
	 */
	@Test
	public void testInvalid() {
		String str = "January, 1, 2001 at 1:23:45.678 am";
		Assert.assertNull("Invalid formats return null", ISO8601.parse(str));
	}

	/**
	 * Null dates should return null.
	 */
	@Test
	public void testNull() {
		Assert.assertNull("Null date returns null", ISO8601.format(null));
	}

}