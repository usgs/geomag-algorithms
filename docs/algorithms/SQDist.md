Solar Quiet and Disturbance Algorithm
=====================================

Algorithm Theoretical Basis for "Geomag Solar Quiet and Disturbance"

E. Joshua Rigler &lt;[erigler@usgs.gov](mailto:erigler@usgs.gov)&gt;


## Summary

Mathematical underpinnings and general algorithm considerations are presented
for estimating Solar Quiet (SQ), Secular Variation (SV) and Magnetic
Disturbance (DIST) data streams. SV describes the geomagnetic trend line
at a given moment, and is usually assumed to be a measure of the Earth’s
internal field. SQ is used to describe daily variations that result from the
Earth’s rotation beneath geospace electric currents that are mostly fixed
with respect to the sun. Finally, the value often of most interest in
space weather applications is DIST, or the remainder of the signal when SV
and SQ are removed. This is typically assumed to represent Earth’s magnetic
response to aperiodic solar storms.


## Background and Motivation



## Math and Theory

Exponential smoothing of time series has been employed in countless research,
engineering, economic, sociological, political and other applications. While
its utility has been empirically demonstrated time and again over the last
half century or more, it has only been in the last couple decades that it has
normalized in form, stood up to rigorous mathematical scrutiny, and been tied
directly to well-known statistical time series models. A major contributor to
this recent maturation of this subdiscipline of applied mathematics is R. J.
Hyndman. We largely follow notation used in his free Online textbook
(http://www.otexts.org/fpp), and related literature, to provide a very brief
overview of exponential smoothing that culminates in an algorithm that can be
used to decompose a time series into a trend, a repeating “seasonal” pattern,
and a residual.


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
