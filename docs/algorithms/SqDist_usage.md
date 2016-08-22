Solar Quiet and Disturbance Algorithm Usage
===========================================

The Solar Quiet and Disturbance Algorithm calculates secular variation `SV`,
solar quiet `SQ`, and disturbance `DIST` from Geomagnetic data.

# Command Line

`geomag.py --algorithm sqdist`


### Examples
(a)

    bin/geomag.py \
      --input edge \
      --observatory BOU \
      --inchannels X \
      --starttime 2016-01-03T00:00:00 \
      --endtime 2016-01-03T23:59:00 \
      --interval minute \
      --algorithm sqdist \
      --sqdist-alpha 2.315e-5 \
      --sqdist-beta 0 \
      --sqdist-m 1440 \
      --sqdist-gamma 3.333e-2 \
      --sqdist-statefile /tmp/sqdist_x_state.json \
      --rename-output-channel X_Dist MXT \
      --rename-output-channel X_SQ MXQ \
      --rename-output-channel X_SV MXV \
      --outchannels MXT MXQ MXV \
      --output iaga2002 \
      --output-stdout


This example processes one `Edge` channel (`X`) for the `BOU` observatory,
for one day of `minute` data. The memory of SV is 30 days, or 43200 samples,
so --sqdist-alpha is `2.315e-5` (i.e., ~1/43200). The SQ signal repeats once
per day, so --sqdist-m is `1440`. SQ also has a memory of 30 days, but because
each element of SQ is updated only once per day, --sqdist-gamma must be 1440
times larger than --sqdist-alpha, or `3.333e-2`. Finally, outputs is renamed to
valid Edge channels, and written to standard output using `IAGA2002` format.
The default initial slope is 0, so the --sqdist-beta option used here ensures
the slope stays 0. In general, if default initial conditions are not adequate,
the user must include them in `/tmp/sqdist_x_state.json`, and use
--sqdist-statefile.

(b)

    bin/geomag.py \
      --input edge \
      --observatory BOU \
      --inchannels H E Z F \
      --starttime 2016-01-03T00:00:00 \
      --endtime 2016-01-03T23:59:00 \
      --algorithm sqdist \
      --sqdist-mag \
      --sqdist-alpha 2.315e-5 \
      --sqdist-statefile /tmp/sqdist_h_state.json \
      --rename-output-channel H_SQ MSQ \
      --rename-output-channel H_SV MSV \
      --rename-output-channel H_Dist MDT \
      --outchannels MDT MSQ MSV \
      --output iaga2002 \
      --output-stdout

This example calculates the total horizontal field (`--sqdist-mag`) before
decomposing it into SQ, SV, and Dist. Minute data is assumed by default, so
again SV has a memory of 43200 samples, or forgets `2.315e-5` with each new
observation processed (--sqdist-alpha). By neglecting to specify --sqdist-beta,
--sqdist-m, and --sqdist-gamma, default values mean that no SQ correction is
estimated (or more precisely, SQ is zero). In other words, this is "simple
exponential smoothing".

### Application Programming Interface

***Class***  

```
geomagio.Algorithm.SqDistAlgorithm(alpha=None, beta=None, gamma=None,
    phi=1, m=1, yhat0=None, b0=None, s0=None, l0=None, sigma0=None,
    zthresh=6, fc=0, hstep=0, statefile=None, mag=False)
```

***Attributes***

<u>configuration parameters</u>
```
alpha            forgetting factor for SV (i.e., baseline level)
beta             forgetting factor for forecast slope
gamma            forgetting factor for SQ
phi              dampening factor for slope
m                length of SQ vector (i.e., "seasonal" corrections)

zthresh          z-score threshold that determines if observation
                 should be ignored while updating the state
fc               number of steps beyond last observation to forecast
hstep            number of steps to predict ahead of each observation
statefile        file in which to store state variables at end of run;
                 used to pick up processing where it left off if
                 Python kernel is restarted
mag              if True, and two horizontal vector components are in
                 the ObsPy stream, calculate total horizontal field,
                 then only process this field
```
<u>state variables</u>
```
yhat0            initial vector of hstep yhats
s0               initial vector of SQ "seasonal" corrections
l0               initial SV baseline
b0               initial forecast slope
sigma0           initial disturbance standard deviation
last_observatory remember observatory ID
last_channel     remember channel ID
next_starttime   remember the next expected time step
```

***Methods***

```
get_input_interval(start, end, observatory=None, channels=None)
  check requested start/end datetimes, observatory string, and
  channels string to see if they are consistent with the current
  state, thus allowing it to be extended into the future without
  re-initializing; if not, the state will be re-initialized by
  reading in ~3 months of data from the input factory.

load_state()
  load/initialize state from statefile

save_state()
  save state to statefile to be re-loaded later

process(stream)
  process ObsPy Stream, potentially with multiple traces

process_one(trace)
  process ObsPy Trace using additive(); construct SV, SQ, and DIST,
  and place these in a single Stream

add_arguments(parser)
  add command line arguments to argparse parser. See code for more
  information.

configure(arguments)
  configure algorithm using command line arguments. See code for more
  information
```

***Class Methods***

```
additive(yobs, m, alpha, beta, gamma, phi=1,
         yhat0=None, s0=None, l0=None, b0=None, sigma0=None,
         zthresh=6, fc=0, hstep=0)
  low-level implementation of the Holt-Winters algorithm where inputs
  are NOT ObsPy Streams or Traces, but NumPy arrays or scalars; this
  is a class method, allowing it to be used without instantiating a
  SqDistAlgorithm object. See code for more information.

estimate_parameters(yobs, m, alpha=None, beta=None, gamma=None, phi=1,
                    yhat0=None, s0=None, l0=None, b0=None, sigma0=None,
                    zthresh=6, fc=0, hstep=0,
                    alpha0=0.3, beta0=0.1, gamma0=0.1)
  utility to estimate optimal prediction paramters alpha, beta, gamma;
  this is a class method, allowing it to be used without instantiating
  a SqDistAlgorithm object. See code for more information.
```


see [SqDistValidate.ipynb](SqDistValidate.ipynb) for a detailed algorithm theoretical basis and demonstration.
