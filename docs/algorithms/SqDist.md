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
polynomials to *detrend* the data. `SQ` and `DIST` have similar time scales, and
are therefore more difficult to separate. Fourier series can be fit to data to
estimate `SQ`, which works reasonably well in non-real time situations.

However, Fourier decomposition suffers in real time processing because there is
a large computational burden associated with the long time series required to
properly reproduce seasonal and yearly variations, plus their associated
harmonics. Even if the computational burden were not an issue, such long time
series become a numerical problem when extreme artificial spikes, and even
moderate baseline shifts, are not corrected for, since the algorithm must
accommodate these non-periodic artifacts in the data fit for the entire duration
of the long time series (e.g., a year or more).


## Exponential Smoothing

Real time decomposition of geomagnetic time series into `SV`, `SQ`, and `DIST`
should explicitly acknowledge and address the time-causal nature of real time
observations. To this end, we employ a discrete form of exponential smoothing,
with "seasonal" adjustments, to update estimates of `SV` and `SQ` based only on
past observations. A detailed theoretical basis and demonstration of our
algorithm can be found in [SqDistValidate.ipynb (a Jupyter/IPython
Notebook)](SqDistValidate.ipynb), while a usage guide is in
[SqDist_usage.md](SqDist_usage.md). Below, we summarize the basics.

Exponential smoothing is a weighted running average of the most recent
observation and the previous average - a recursive process. If between 0 and 1,
the weight associated with the observation is referred to as a "forgetting
factor", whose inverse defines the average age (in terms of regular sample
intervals) of the observations contributing to the current average. A weight of
0 means new observations do not affect the average at all, while 1 means new
observations become the average.

Exponential smoothing can be used to estimate a running mean, a linear trend,
even a periodic sequence of `m` discrete "seasonal corrections" (there's more,
but we focus on these three here). We define separate forgetting factors for
each:

- `alpha` - sensitivity of running average to new observations
- `beta` - sensitivity of linear trend to new observations
- `gamma` - sensitivity of seasonal correction to new observations
- `m` - length of cycle for which seasonal corrections are estimated

Now, suppose we have a typical time series of 1-minute resolution geomagnetic
data, and want to remove secular variations with a time scale longer than 30
days (SV is traditionally fit to the monthly averages of "quiet days", leading
to ~30 day time scale). 30 days is 43200 minutes, so we specify `alpha=1/43200`.
If we want to allow the slope to vary with a similar time scale, we specify
`beta=1/43200`. However, if we want seasonal corrections to vary with a 30 day
time scale, it is necessary to account for the fact that they are only updated
once per cycle. If that cycle is 1 day, or `m=1440` minutes, that means
`gamma=1/43200*1440`.

So, `alpha`, `beta`, and `gamma`, combined with observations, provide a running average of geomagnetic time series (`SV+SQ`). This is then subtracted from the actual observations to produce `DIST`.

## Why Exponential Smoothing?

In addition to addressing the computational and operational shortcomings of
traditional Fourier decomposition methods in real time processing mentioned
above, our exponential smoothing with seasonal corrections has other advantages:
`SV` and `SQ` are not constrained to arbitrary functional forms, and so more
truly reflect actual observation; `SV` and `SQ` are easily extrapolated across
gaps in data; and a running estimate of the standard deviation of `DIST` is
provided (which can be used as a performance metric, to set noise thresholds,
etc.). Finally, the simplicity of exponential smoothing makes it more intuitive,
and thus easier to adapt to evolving operational requirements.

There are disadvantages too, most notable perhaps being that `SQ` becomes quite
noisy if the general level of magnetic disturbance is large, as is the case at
high latitude observatories. The user can certainly apply ad hoc corrections to
`SQ` to smooth it. We are currently considering one such correction that still
retains all the best characteristic of exponential smoothing. A future version
of this algorithm may contain a configuration parameter that allows the user to
specify a local `SQ` smoothing window, in addition to the once-per-cycle
exponential smoothing currently allowed.


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
