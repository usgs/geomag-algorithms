<a name="h.dnpv2n3m3rfc"></a><span>Algorithm Theoretical Basis for &ldquo;Geomag XYZ&rdquo;</span>

<a name="h.x8hn56la31oj"></a><span>E. Joshua Rigler &lt;</span><span class="c15">[erigler@usgs.gov](mailto:erigler@usgs.gov)</span><span>&gt;</span>

# <a name="h.rdpf78gaqv72"></a><span>Summary</span>

<span>Mathematical underpinnings and general algorithm considerations are presented for converting geomagnetic observations from so-called HEZ coordinates, used by the USGS geomagnetism program, into XYZ coordinates, used by a growing number of international geomagnetism programs, as well as various academic and commercial entities. Inverse transformations are also provided.</span>

# <a name="h.l0w23nqidiq1"></a><span>Background and Motivation</span>

<span>Historically, the most common coordinate system used to specify measured geomagnetic fields has been HDZ, where: </span>

<span></span>

1.  <span>H is the magnitude of the geomagnetic field vector tangential to the Earth&rsquo;s surface;</span>
2.  <span>D is the declination, or clockwise angle from the vector pointing to the geographic north pole to the H vector;</span>
3.  <span>Z is the downward component of the geomagnetic field.</span>

<span></span>

<span>This coordinate system is useful for navigation (it is the natural coordinate system for a magnetic compass), and any scientific analysis conducted in a geomagnetic field-aligned reference frame, but is somewhat awkward for most other applications. A more generally useful set of coordinates for scientific analysis and engineering applications is the XYZ system:</span>

<span></span>

1.  <span>X points to the geographic north pole;</span>
2.  <span>Y points eastward;</span>
3.  <span>Z, as before, points downward.</span>

<span></span>

<span>Conversion between these two coordinate systems involves relatively straight-forward trigonometry (see Eqs. 1, 2, and 3). However, in practice, a 3-axis magnetometer necessarily takes on a fixed orientation upon installation. For USGS observatories, this is aligned with the average magnetic north vector and downward, with the final axis completes a right-handed 3-dimensional coordinate system (roughly eastward). &nbsp;This is often referred to as HEZ coordinates, but for the remainder of this document we will refer to it as </span><span>heZ</span><span>, to avoid confusion with more traditional definitions of H and E(==Y).</span>

<span></span>

<span>The purpose of this document then is to provide a mathematical and algorithmic description of how one converts data measured in heZ coordinates to true HDZ, and finally to XYZ.</span>

<span></span>

# <a name="h.fukk0zanj6jd"></a><span>Math and Theory</span>

<span>First, following definitions in the previous section, the conversion from cylindrical HDZ to Cartesian XYZ is very straight-forward trigonometry:</span>

<span></span>
[](#)[](#)<table cellpadding="0" cellspacing="0" class="c14"><tbody><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image00.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(1)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image01.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(2)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image02.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(3)</span>
</td></tr></tbody></table>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 243.38px; height: 418.50px;">![](images/image11.png)</span>

<span></span>

<span>However, as noted previously, the USGS aligns its magnetometers with the magnetic north upon installation at an observatory, meaning raw data is generated in heZ coordinates, where &ldquo;h&rdquo; is is the primary axis in a fixed reference frame, &ldquo;e&rdquo; is the secondary axis in this reference frame, and &ldquo;Z&rdquo; is the tertiary axis, which remains common for all reference frames discussed in this document.</span>

<span></span>

<span>The figure to the right illustrates how the same full magnetic field vector </span><span class="c18">F</span><span>, can be represented in heZ, HDZ, and XYZ coordinates. Red objects are specific to the magnetometer&rsquo;s reference frame, while blue objects are specific to the geographic reference frame. Black is common to all frames considered here, and dashed lines help define Cartesian grids.</span>

<span></span>

<span>One thing that is not labeled in this figure is the angle d (see Eq. 4), which is the difference between declination D, and a declination baseline (D</span><span class="c11">0</span><span>, or DECBAS)</span><span>.</span>

<span></span>

<span>Equations 4, 5, and 6 describe how to convert the horizontal components of a USGS magnetometer&rsquo;s raw data element into more standard H and D components.</span>

<span></span>
[](#)[](#)<table cellpadding="0" cellspacing="0" class="c14"><tbody><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image03.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(4)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image04.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(5)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image05.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(6)</span>
</td></tr></tbody></table>

<span></span>

<span>To inverse transform from XY to HD:</span>

<span></span>
[](#)[](#)<table cellpadding="0" cellspacing="0" class="c14"><tbody><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image06.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(7)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image07.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(8)</span>
</td></tr></tbody></table>

<span></span>

<span>...and from HD to he:</span>

<span></span>
[](#)[](#)<table cellpadding="0" cellspacing="0" class="c14"><tbody><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image08.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(9)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image09.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(10)</span>
</td></tr><tr class="c5"><td class="c10" colspan="1" rowspan="1">

![](images/image10.png)
</td><td class="c12" colspan="1" rowspan="1">

<span class="c3">(11)</span>
</td></tr></tbody></table>

<span></span>

<span>It is worth noting that there is potential for mathematically undefined results in several of the preceding equations, where infinite ratios are a possible argument to the arctan() function. However, Python&rsquo;s Numpy package, and indeed most modern math libraries, will return reasonable answers in such situations (hint: arctan(Inf)==pi/2).</span>

<span></span>

# <a name="h.rsxcajyqdnvk"></a><span>Algorithm</span><span>&nbsp;Considerations</span>

## <a name="h.e7fn5x4g0vlc"></a><span>Magnetic Intensity Units</span>

<span>It is understood that all raw data inputs are provided in units of nanoTesla (nT). Of course this is not required for the equations to be valid, but it is incumbent on the programmer to make sure all input data units are the same, and that output units are defined accurately.</span>

## <a name="h.c3gsqbgrcf59"></a><span>Declination Angular Units</span>

<span>The equations in the preceding section are relatively simple to code up, with the standard caveat that angles must be appropriate for the trigonometric functions (e.g., if sin/cos/tan expect radians, be sure to provide parameters in radians). One thing that can potentially complicate this is that IAGA standards require declination angles to be in minutes of arc. Furthermore, </span><span>D</span><span class="c11">0</span><span>&nbsp;(DECBAS)</span><sup>[[a]](#cmnt1)</sup><sup>[[b]](#cmnt2)</sup><span>&nbsp;is not very well-defined by IAGA standards, but is typically reported in tenths of minutes of arc. None of these are difficult to convert, but it is incumbent on the programmer to make sure they know what units are being used for the inputs.</span>

## <a name="h.tzmta19ugqn"></a><span>Declination Baseline</span>

<span>Declination baseline is not well-defined by IAGA standards. The typical method used to publish it with actual data is to include it in the metadata. For older IMF formatted files, it is part of the periodic block header. For IAGA2002 formatted file, it </span><span class="c8">may</span><span>&nbsp;be in the file header, but is not required. To the best of my knowledge, if it is not included, one should assume it is zero, but no corroborating documentation could be found to justify this statement.</span>

## <a name="h.t3w4ufsf9h6w"></a><span>Declination in USGS Variations Data</span>

<span>The</span><span>&nbsp;USGS variations data is actually published in hdZ coordinates. If one wishes to apply equations in the preceding section to USGS variations data, they must first convert &ldquo;d&rdquo; back into &ldquo;e&rdquo; via Eq. 11.</span>

## <a name="h.efk3flra8ap3"></a><span>Data Flags</span>

<span>It should go without saying that bad data in one coordinate system is bad data in another. However, on occasion, operational USGS Geomagnetism Program code has been discovered where coordinate transformations were applied </span><span class="c8">before</span><span>&nbsp;checking data flags. </span><span>This is not an issue if data flags are NaN (not-a-number values), but more typical for Geomag data, these are values like 99999, which can lead to seemingly valid, but erroneous values at times when the raw data were known to be bad.</span><sup>[[c]](#cmnt3)</sup><sup>[[d]](#cmnt4)</sup><sup>[[e]](#cmnt5)</sup><sup>[[f]](#cmnt6)</sup>
<div class="c1">

[[a]](#cmnt_ref1)<span class="c3">How is this value computed? &nbsp;Is it something that would be configured in advance, or best computed dynamically?</span>
</div><div class="c1">

[[b]](#cmnt_ref2)<span class="c3">Good question.</span>

<span class="c3"></span>

<span class="c3">To date, I have simply extracted it from the header of the text files we publish Online. But Hal tells me it is not actually stored in any database currently, but hard-coded or included in a config file somewhere. He or Duff Stewart are probably needed to answer this question more confidently.</span>

<span class="c3"></span>

<span class="c3">For this XYZ algorithm it is more-or-less assumed that DECBAS is a quasi-static value, but in the future this may change.</span>
</div><div class="c1">

[[c]](#cmnt_ref3)<span class="c3">Is the preferred algorithm output NaN, which can (when needed) be replaced with a placeholder value such as 99999?</span>
</div><div class="c1">

[[d]](#cmnt_ref4)<span class="c3">Another good question. The official data products are required to use 99999 (or in some cases 88888), but if output is some kind of intermediate product, it might make more sense to use NaNs, and simply replace these with 9s when the text files are generated.</span>
</div><div class="c1">

[[e]](#cmnt_ref5)<span class="c3">That makes the most sense to me. It should be the job of the module creating the text file to replace the NaNs with the accepted value for that type of file.</span>
</div><div class="c1">

[[f]](#cmnt_ref6)<span class="c3">that&#39;s the route we&#39;re planning to go</span>
</div></body></html>
