package gov.usgs.geomag.io;

import java.math.BigDecimal;
import java.math.MathContext;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;

/**
 * Base class for Timeseries.
 *
 * A timeseries represents a sequence of samples collected at
 * regular intervals.
 */
public class Timeseries {

	public static final BigDecimal RATE_SECOND = BigDecimal.ONE;
	public static final BigDecimal RATE_MINUTE = BigDecimal.ONE.divide(
			new BigDecimal("60"), MathContext.DECIMAL128);

	/** The time of the first sample. */
	private final Date starttime;
	/** The time of the last sample. */
	private final Date endtime;
	/** The samples. */
	private final ArrayList<BigDecimal> samples;
	/** The sample interval. */
	private final BigDecimal sampleRate;

	/**
	 * Construct a timeseries object.
	 *
	 * @param channel the channel.
	 * @param starttime the starttime.
	 * @param endtime the endtime.
	 */
	public Timeseries (final Date starttime, final Date endtime,
			final ArrayList<BigDecimal> samples) {
		this(starttime, endtime, samples,
				computeSampleRate(samples.size(), starttime, endtime));
	}

	/**
	 * Construct a timeseries object.
	 *
	 * @param starttime time of the first sample.
	 * @param endtime time of the last sample.
	 * @param samples the samples.
	 * @param sampleRate the sample rate in hertz.
	 */
	public Timeseries (final Date starttime, final Date endtime,
			final ArrayList<BigDecimal> samples, final BigDecimal sampleRate) {
		this.starttime = starttime;
		this.endtime = endtime;
		this.samples = samples;
		this.sampleRate = sampleRate;
	}

	/**
	 * @return the time of the first sample.
	 */
	public Date getStartTime () {
		return this.starttime;
	}

	/**
	 * @return the time of the last sample.
	 */
	public Date getEndTime () {
		return this.endtime;
	}

	/**
	 * @return the samples.
	 */
	public ArrayList<BigDecimal> getSamples () {
		return this.samples;
	}

	/**
	 * @return the sample rate in Hertz.
	 */
	public BigDecimal getSampleRate () {
		return this.sampleRate;
	}


	/**
	 * Get the time for a given sample index.
	 */
	public Date getSampleTime (final int index) {
		if (index < 0 || index >= getSamples().size()) {
			// out of range
			return null;
		}
		return computeSampleTime(index, getStartTime(), getSampleRate());
	}

	/**
	 * Compute the index for a given time.
	 *
	 * @param time the sample time.
	 * @return getSampleIndex(time, true).
	 */
	public Integer getSampleIndex (final Date time) {
		return getSampleIndex(time, true);
	}

	/**
	 * Get the index of a given time.
	 *
	 * @param time the sample time.
	 * @param exact whether to (true) return null if no sample exists for time,
	 *        or (false) to return the nearest index for time.
	 * @return index for given time, null if out of timeseries range.
	 */
	public Integer getSampleIndex (final Date time, final boolean exact) {
		if (time.before(getStartTime()) || time.after(getEndTime())) {
			// out of range
			return null;
		}
		int index = computeSampleIndex(time, getStartTime(), getSampleRate());
		if (exact) {
			Date expected = getSampleTime(index);
			if (!time.equals(expected)) {
				// no sample at exactly time
				return null;
			}
		}
		return index;
	}

	/**
	 * Compute the time of an index.
	 *
	 * @param index the sample index (zero based).
	 * @param starttime the time of the first sample.
	 * @param sampleRate the sample rate in hertz.
	 * @return the time of the sample.
	 */
	public static final Date computeSampleTime (final int index,
			final Date starttime, final BigDecimal rate) {
		long offset = (long) (index * 1000.0 / rate.doubleValue());
		return new Date(starttime.getTime() + offset);
	}

	/**
	 * Compute the index of a time.
	 *
	 * @param time the time to compute index of.
	 * @param starttime the time of the first sample.
	 * @param rate the sample rate in hertz.
	 * @return the index of the sample nearest to time.
	 */
	public static final int computeSampleIndex (final Date time,
			final Date starttime, final BigDecimal rate) {
		long offset = time.getTime() - starttime.getTime();
		return (int) Math.round(offset * rate.doubleValue() / 1000.0);
	}

	/**
	 * Compute the sample rate.
	 *
	 * @param count the number of samples (one based).
	 * @param starttime the time of the first sample.
	 * @param endtime the time of the last sample.
	 * @return the sample rate in Hertz.
	 */
	public static final BigDecimal computeSampleRate (final int count,
			final Date starttime, final Date endtime) {
		long milliseconds = endtime.getTime() - starttime.getTime();
		BigDecimal seconds = new BigDecimal(milliseconds).movePointLeft(3);
		return new BigDecimal(count - 1).divide(seconds, MathContext.DECIMAL128);
	}

	/**
	 * Merge values from multiple timeseries.
	 *
	 * The first non-null value found for each sample is the merged value.
	 *
	 * @param sources sources to merge in most-preferred-first order.
	 * @return merged timeseries
	 */
	public static final Timeseries merge (final Timeseries[] sources) {
		int numSources = sources.length;
		int numSamples = sources[0].getSamples().size();
		ArrayList<BigDecimal> merged = new ArrayList<BigDecimal>(numSamples);
		BigDecimal value;
		for (int index = 0; index < numSamples; index++) {
			value = null;
			for (int source = 0; source < numSources; source++) {
				value = sources[source].getSamples().get(index);
				if (value != null) {
					// first non-null value for this index
					break;
				}
			}
			merged.add(value);
		}
		return new Timeseries(sources[0].getStartTime(), sources[0].getEndTime(),
				merged, sources[0].getSampleRate());
	}

}
