Geomagnetic Secular Variation, Solar Quiet, and Disturbance
===========================================================

E. Joshua Rigler &lt;[erigler@usgs.gov](mailto:erigler@usgs.gov)&gt;


## Background and Motivation

The magnetic field measured at a given point on Earth’s surface is often
assumed to be static, but in reality it is constantly changing, and on a
variety of time scales associated with distinct physical phenomena. These are:

- `SV` - Secular variation, slow variations in the geomagnetic field associated
  with changes in Earth's interior.
- `SQ` - Solar quiet variation, shorter-term periodic variations in the
  geomagnetic field associated with Earth's rotation beneath quasi-static
  geospace electric currents that are phase-locked with the sun.
- `DIST` - Disturbance, shorter-term non-periodic variations in the geomagnetic
  field, typically associated with episodic events like geomagnetic storms and
  substorms.

SV is fairly easily separated from higher frequency variations using low-order
polynomials to *detrend* the data. SQ and DIST have similar time scales, and
are therefore more difficult to separate. Fourier series can be fit to data to
estimate SQ, which works well in non-real time situations. This approach
suffers in real time situations for both practical and theoretical reasons
that we won't discuss in detail here.


## Exponential Smoothing

Real time decomposition of geomagnetic time series into SV, SQ, and DIST should
explicitly acknowledge and address the time-causal nature of real time
observations. To this end, we employ a form of exponential smoothing, with
"seasonal" adjustments, that updates estimates of SV and SQ based only on past
observations, weighting older observations less and less as time passes. In
effect, SV and SQ adapt to changing conditions at a predictable rate that can
be specified by the user.

In addition, this approach is significantly less computationally expensive than
traditional Fourier techniques. No Fourier transform of months-to-years-long
data series is required, and memory requirements are comparably reduced, since
a description of the state of the system at any given moment is only 1+m, where
m is the number of data points in an SQ cycle, nominally 1 day.

Finally, exponential smoothing is generally more robust to common issues with
real time data series; it easily extrapolates SV and SQ across gaps in the
data; it provides a running estimate of the variance of DIST, which can be used
to set a threshold for spike detection; and it adjusts SV to accommodate DC
offsets at rate specified by the user.


## Example

Detailed usage examples and expected output for this algorithm is shown in this
[Solar Quiet and Disturbance (Holt Winters)](SqDistValidate.ipynb) IPython Notebook
example.


## References

 - Archibald, B.C., and A.B. Koehler (2003), [Normalization of seasonal
   factors in Winters'
   methods](http://www.sciencedirect.com/science/article/pii/S0169207001001170),
   Int. J. of Forecasting, 19(1), 143-148.

 - Bodenham, D., and N. Adams (2013), [Technical Report: Continuous changepoint
   monitoring of data streams using
   adaptive estimation](http://wwwf.imperial.ac.uk/~dab10/techreport.pdf), ...
   (Submitted to Elsevier; also a longer thesis is available from Imperial
   College London)

 - Byrd, R. H., P. Lu, and J. Nocedal (1995), [A limited memory algorithm for
   bound constrained
   optimization](http://epubs.siam.org/doi/abs/10.1137/0916069), SIAM J.
   Scientific and Stat. Computing, 16(5), 1190-1208.

 - Gardner, E. S. (2006), [Exonential smoothing: The state of the art --
   Part II](http://www.sciencedirect.com/science/article/pii/S0169207006000392),
   Int. J. of Forecasting, 22(4), 637-666.

 - Hyndman, R. J., A.B. Koehler, J.K. Ord, and R.D. Snyder (2005), [Prediction
   intervals for exponential smoothing using two new classes of state space
   models](http://onlinelibrary.wiley.com/doi/10.1002/for.938/abstract), J.
   Forecast., 24(1), 17-37.

 - Hyndman, Rob J., and George Athana­sopou­los. "Forecasting: Principles and
   Practice." Forecasting: Principles and Practice. OTexts: Online,
   Open-Access Textbooks, May 2012. Web. <https://www.otexts.org/fpp>.

 - Hyndman, R. J., and G. Athanasopoulos (2013), [Forecasting: principles and
   practice](https://www.otexts.org/fpp), OTexts.
