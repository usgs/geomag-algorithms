Average Algorithm
-----------------

Algorithm Theoretical Basis for "Average Algorithm"

## Summary
Averages multiple observatory data for the same channel.
Used mainly to average disturbance data in order to find
the general disturbance in the magnetic field. The algorithm
takes data from multiple observatories with the same channel
and returns a stream of the averaged data.

## Background and Motivation
The averaging function is used to smooth out the plots and
find a combined disturbance of the magnetic field that
encompasses the Earth. This can be used to determine the 
overall effect of magnetic storms over a large area. The 
algorithm is also used to average the Solar Quiet response 
to find the daily change in the magnetic field. The algorithm
can be used to find the average of any channel over multiple
observation stations.

## Math and Theory
Multiple data streams are averaged using a numpy function
(numpy.mean) that takes multiple ndarrays as an argument
and averages them into one array. A latitude correction
can be applied based on the different observation locations.
The correction is really just a weighting value based on a
0-1 scale in order to put more validity in some stations.

## Practical Considerations
The averaging function can be called from geomag.py and stating 
the '--algorithm average' option or by calling the average.py 
script which automatically chooses the averaging option to the 
algorithm. Only one channel at a time can be run through the 
algorithm. Any input that geomag.py can handle can be used
such as the edge server or a file url input this is also true
for any output.
