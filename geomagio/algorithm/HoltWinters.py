"""Algorithm that produces Solar Quiet (SQ), Secular Variation (SV) and
   Magnetic Disturbance (DIST).

   Algorithm for producing SQ, SV and DIST.
       This module implements Holt-Winters exponential smoothing. It predicts
       an offset-from-zero plus a "seasonal" correction given observations
       up to time t-1. Each observation's influence on the current prediction
       decreases exponentially with time according to user-supplied runtime
       configuration parameters.
"""

import numpy as np
import datetime as dt
from scipy.optimize import fmin_l_bfgs_b


def RMSE(params, *args):
   """Wrapper function passed to scipy.optimize.fmin_l_bfgs_b in
      order to find optimal Holt-Winters prediction coefficients.

   Parameters
   ----------

   Returns
   -------
   """
   # extract parameters to fit
   alpha, beta, gamma = params

   # extract arguments
   yobs = args[0]
   method = args[1]
   m = args[2]
   s0 = args[3]
   l0 = args[4]
   b0 = args[5]
   hstep = args[6]
   zthresh = args[7]

   if method == "additive":
      # call Holt-Winters with additive seasonality
      yhat, _, _, _, _, _, _, _ = additive(yobs, m, alpha=alpha, beta=beta,
                 gamma=gamma, l0=l0, b0=b0, s0=s0, zthresh=zthresh, hstep=hstep)

   else:
      print 'Method must be additive or ...'
      raise Exception

   # calculate root-mean-squared-error of predictions
   rmse = np.sqrt( np.nanmean([(m - n) ** 2 for m, n in zip(yobs, yhat)]) )

   return rmse

def additive(yobs, m, alpha=None, beta=None, gamma=None, phi=1,
             yhat0=None, s0=None, l0=None, b0=None, sigma0=None,
             zthresh=6, fc=0, hstep=0):
   """Primary function for Holt-Winters smoothing/forecasting with
      damped linear trend and additive seasonal component.

   Parameters
   ----------
   yobs         : input series to be smoothed/forecast
   m            : number of "seasons"

   KEYWORDS:
   alpha        : the level smoothing parameter (0<=alpha<=1)
                  (if None, alpha will be estimated; default)
   beta         : the slope smoothing parameter (0<=beta<=1)
                  (if None, beta will be estimated; default)
   gamma        : the seasonal adjustment smoothing parameter (0<=gamma<=1)
                  (if None, gamma will be estimated; default)
   phi          : the dampening factor for slope (0<=phi<=1)
                  (if None, phi will be estimated; default is 1)
   yhat0        : initial yhats for hstep>0 (len(yhat0) == hstep)
                  (if None, yhat0 will be set to NaNs)
   s0           : initial set of seasonal adjustments
                  (if None, default is [yobs[i] - a[0] for i in range(m)])
   l0           : initial level (i.e., l(t-hstep))
                  (if None, default is mean(yobs[0:m]))
   b0           : initial slope (i.e., b(t-hstep))
                  (if None, default is (mean(yobs[m:2*m]) - mean(yobs[0:m]))/m )
   sigma0       : initial standard-deviation estimate (len(sigma0) == hstep+1)
                  (if None, default is [sqrt(var(yobs))] * (hstep+1) )
   zthresh      : z-score threshold to determine whether yhat is updated by
                  smoothing observations, or by simulation alone; if exceeded,
                  only sigma is updated to reflect latest observation
                  (default is 6)
   fc           : the number of steps beyond the end of yobs (the available
                  observations) to forecast
                  (default is 0)
   hstep        : the number of steps ahead to predict yhat[i]
                  which forces an hstep prediction at each time step
                  (default is 0)

   Returns
   -------
   yhat      : series of smoothed/forecast values (aligned with yobs(t))
   shat      : series of seasonal adjustments (aligned with yobs(t))
   sigmahat  : series of time-varying standard deviations (aligned with yobs(t))
   yhat0next : use as yhat0 when function called again with new observations
   s0next    : use as s0 when function called again with new observations
   l0next    : use as l0 when function called again with new observations
   b0next    : use as b0 when function called again with new observations
   sigma0next: use as sigma0 when function called again with new observations

   alpha     : optimized alpha (if input alpha is None)
   beta      : optimized beta (if input beta is None)
   gamma     : optimized gamma (if input gamma is None)
   phi       : optimized phi (if input phi is None)
   rmse      : root mean squared error metric from optimization
             (only if alpha or beta or gamma were optimized)

   NOTES:
   * The adaptive standard deviation (sigma), multiplied by zthresh to determine
     which observations should be smoothed or ignored, is always updated using
     the latest error if a valid observation is available. This way, if what
     seemed a spike in real-time was actually a more permanent baseline shift,
     the algorithm will adjust to the new baseline once sigma grows enough to
     accommodate the errors.

   * The standard deviation also updates when no obserations are present, but
     does so according to Hyndman et al (2005) prediction intervals. The result
     is a sigma that grows over gaps, and for forecasts beyond yobs[-1].

   """

   # set some default values
   if l0 is None:
      l = np.nanmean(yobs[0:int(m)])
   else:
      l = l0
      if not np.isscalar(l0):
         raise Exception, "l0 must be a scalar"

   if b0 is None:
      b = (np.nanmean(yobs[m:2 * m]) - np.nanmean(yobs[0:m])) / m
      b = 0 if np.isnan(b) else b # replace NaN with 0
   else:
      b = b0
      if not np.isscalar(b0):
         raise Exception, "b0 must be a scalar"

   if yhat0 is None:
      yhat = [np.nan for i in range(hstep)]
   else:
      yhat = list(yhat0)
      if len(yhat) != hstep:
         raise Exception, "yhat0 must have length %d"%hstep

   if s0 is None:
      s = [yobs[i] - l for i in range(m)]
      s = [i if ~np.isnan(i) else 0 for i in s] # replace NaNs with 0s
   else:
      s = list(s0)
      if len(s)!=m:
         raise Exception, "s0 must have length %d "%m

   if sigma0 is None:
      # NOTE: maybe default should be vector of zeros???
      sigma = [np.sqrt(np.nanvar(yobs))] * (hstep+1)
   else:
      sigma = list(sigma0)
      if len(sigma)!=(hstep+1):
         raise Exception, "sigma0 must have length %d"%(hstep+1)

   #
   # Optimal parameter estimation if requested
   # FIXME: this should probably be extracted to a separate module function.
   #

   retParams = False
   if (alpha == None or beta == None or gamma == None or phi == None):

      # estimate parameters
      retParams = True

      if fc > 0:
         print "WARNING: non-zero fc is not used in estimation mode"

      if alpha != None:
         # allows us to fix alpha
         boundaries = [(alpha,alpha)]
         initial_values = [alpha]
      else:
         boundaries = [(0,1)]
         initial_values = [0.3] # FIXME: should add alpha0 option

      if beta != None:
         # allows us to fix beta
         boundaries.append((beta,beta))
         initial_values.append(beta)
      else:
         boundaries.append((0,1))
         initial_values.append(0.1) # FIXME: should add beta0 option

      if gamma != None:
         # allows us to fix gamma
         boundaries.append((gamma,gamma))
         initial_values.append(gamma)
      else:
         boundaries.append((0,1))
         initial_values.append(0.1) # FIXME: should add gamma0 option

      if phi != None:
         # allows us to fix phi
         boundaries.append((phi,phi))
         initial_values.append(phi)
      else:
         boundaries.append((0,1))
         initial_values.append(0.9) # FIXME: should add phi0 option

      initial_values = np.array(initial_values)
      method = 'additive'

      parameters = fmin_l_bfgs_b(RMSE, x0 = initial_values,
                             args = (yobs, method, m, s, l, b, hstep, zthresh),
                             bounds = boundaries, approx_grad = True)
      alpha, beta, gamma = parameters[0]
      rmse = parameters[1]

   # endif (alpha == None or beta == None or gamma == None)


   #
   # Now begin the actual Holt-Winters algorithm
   #

   # ensure mean of seasonal adjustments is zero by setting first element of
   # r equal to mean(s)
   r = [np.nanmean(s)]


   # determine h-step vector of phis for damped trends
   # NOTE: Did away with phiVec altogether, and just use phiHminus1 now;
   #
   #phiVec = np.array([phi**i for i in range(1,hstep)])


   # determine sum(c^2) and phi_(j-1) for hstep "prediction interval" outside of
   # loop; initialize variables for jstep (beyond hstep) prediction intervals
   sumc2_H = 1
   phiHminus1 = 0
   for h in range(1, hstep):
      phiHminus1 = phiHminus1 + phi**(h-1)
      sumc2_H = sumc2_H + (alpha * (1 + phiHminus1 * beta) + \
                           gamma*(1 if (h%m == 0) else 0))**2
   phiJminus1 = phiHminus1
   sumc2 = sumc2_H
   jstep = hstep


   # convert to, and pre-allocate numpy arrays
   # FIXME: this should just be done when checking inputs above
   yobs = np.array(yobs)
   sigma = np.concatenate((sigma, np.zeros(yobs.size+fc)))
   yhat = np.concatenate((yhat, np.zeros(yobs.size+fc)))
   r = np.concatenate((r, np.zeros(yobs.size+fc)))
   s = np.concatenate((s, np.zeros(yobs.size+fc)))


   # smooth/simulate/forecast yobs
   for i in range(len(yobs) + fc):

      # update/append sigma for h steps ahead of i following Hyndman-et-al-2005
      # NOTE: this will be over-written if valid observations exist at step i
      if jstep == hstep:
         sigma2 = sigma[i] * sigma[i]
      sigma[i+hstep+1] = np.sqrt(sigma2 * sumc2 )


      # predict h steps ahead
      yhat[i+hstep] = l + phiHminus1*b + s[i + hstep%m]


      ## NOTE: this was a misguided attempt to smooth s that led to oscillatory
      ##       behavior; this makes perfect sense in hindsight, but I'm leaving
      ##       comments here as a reminder to NOT try this again. -EJR 6/2015
      #yhat[i+hstep] = l + (phiVec*b).sum() + np.nanmean(s[i+ssIdx])


      # determine discrepancy between observation and prediction at step i
      # FIXME: this if-block becomes unneccessary if we remove the fc option,
      #        and force the user to place NaNs at the end of yobs if/when
      #        they want forecasts beyond the last available observation
      if i < len(yobs):
         et = yobs[i] - yhat[i]
      else:
         et = np.nan


      # this if/else block is not strictly necessary, but it makes the logic
      # somewhat easier to follow (for me at least -EJR 5/2015)
      if (np.isnan(et) or np.abs(et) > zthresh * sigma[i]):
         #
         # forecast (i.e., update l, b, and s assuming et==0)
         #

         # no change in seasonal adjustments
         r[i+1] = 0
         s[i+m] = s[i]


         # update l before b
         l = l + phi * b
         b = phi * b

         if np.isnan(et):
            # when forecasting, grow sigma=sqrt(var) like a prediction interval;
            # sumc2 and jstep will be reset with the next valid observation
            phiJminus1 = phiJminus1 + phi**jstep
            sumc2 = sumc2 + (alpha * (1+phiJminus1*beta) +
                             gamma * (1 if (jstep%m == 0) else 0))**2
            jstep = jstep + 1

         else:
            # still update sigma using et when et > zthresh*sigma
            # (and is not NaN)
            # NOTE: Bodenham-et-Adams-2013 may have a more robust method
            sigma[i+1] = alpha*np.abs(et) + (1-alpha)*sigma[i]

      else:
         #
         # smooth (i.e., update l, b, and s by filtering et)
         #

         # renormalization could occur inside loop, but we choose to integrate
         # r, and adjust a and s outside the loop to improve performance.
         r[i+1] = gamma * (1 - alpha) * et/m

         # update and append to s using equation-error formulation
         s[i+m] = s[i] + gamma * (1 - alpha) * et

         # update l and b using equation-error formulation
         l = l + phi*b + alpha * et
         b = phi*b + alpha * beta * et

         # update sigma with et, then reset prediction interval variables
         # NOTE: Bodenham-et-Adams-2013 may have a more robust method
         sigma[i+1] = alpha*np.abs(et) + (1-alpha)*sigma[i]
         sumc2 = sumc2_H
         phiJminus1 = phiHminus1
         jstep = hstep

      # endif (np.isnan(et) or np.abs(et) > zthresh * sigma[i])

   # endfor i in range(len(yobs) + fc - hstep)


   # NOTE: Seasonal adjustments s[i+1:i+m] should be normalized so their mean is
   #       zero, at least until the next observation, or else the notion of a
   #       "seasonal" adjustment loses all meaning. In order to ensure that the
   #       predictions yhat[:] remain unchanged, the baseline a is shifted too.
   #         Archibald-et-Koehler-2003 recommend doing all this inside the loop,
   #       but this slows the algorithm significantly. A&K-2003 note, however,
   #       that r can be integrated, and used to adjust s[:] *outside* the loop,
   #       and Gardner-2006 recommends this approach. A&K-2003 provide valid
   #       reasons for their recommendation (online optimization of alpha will
   #       be impacted), but since ours is not currently such an estimator, we
   #       choose the more computationally efficient approach.
   r = np.cumsum(r)
   l = l + r[-1]
   s = list(np.array(s) - np.hstack((r,np.tile(r[-1],m-1))) )


   # return different outputs depending on retParams
   if retParams:
      return (yhat[:len(yobs)+fc], s[:len(yobs)+fc], sigma[1:len(yobs)+fc+1],
              yhat[len(yobs)+fc:], s[len(yobs)+fc:], l, b, sigma[len(yobs)+fc:],
              alpha, beta, gamma, rmse)
   else:
      return (yhat[:len(yobs)+fc], s[:len(yobs)+fc], sigma[1:len(yobs)+fc+1],
              yhat[len(yobs)+fc:], s[len(yobs)+fc:], l, b, sigma[len(yobs)+fc:])


if __name__ == '__main__':
   """
   This might be expanded to call HoltWinters.py as a script. More likely,
   HoltWinters.py will be incorporated into another module or class, which
   will have it's own command-line functionality.
   """

   print 'HELLO'
