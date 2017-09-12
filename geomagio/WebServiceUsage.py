from datetime import datetime
from geomagio.ObservatoryMetadata import ObservatoryMetadata

class WebServiceUsage(object):
    def __init__(self, metadata=None):
        metadata = metadata or ObservatoryMetadata().metadata
        self.date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.metadata = ', '.join(metadata)

    def usage_page(self, start_response):
        start_response('200 OK',
                [
                    ("Content-Type", "text/html")
                ])
        usage_body = '''
        <h2>Example Requests</h3>
        <dl>
          <dt>BOU observatory data for current UTC day in IAGA2002 format</dt>
          <dd>
          <a href="http://geomag.usgs.gov/ws/edge/?id=BOU">http://geomag.usgs.gov/ws/edge/?id=BOU</a>
          </dd>
          <dt>BOU observatory data for current UTC day in JSON format</dt>
          <dd>
          <a href="http://geomag.usgs.gov/ws/edge/?id=BOU&format=json">http://geomag.usgs.gov/ws/edge/?id=BOU&format=json</a>
          </dd>
        </dl>


        <h2>Request Limits</h2>
        <p>
          To ensure availablility for users, the web service restricts the amount of
          data that can be retrieved in one request.  The amount of data requested
          is computed as follows, where interval is the number of seconds between
          starttime and endtime:
        </p>

        <pre>
          samples = count(elements) * interval / sampling_period
        </pre>
        <h3>Limits by output format</h3>
        <dl>
          <dt>json</dt>
          <dd>
            <code>172800 samples</code> = 4 elements * 12 hours * 3600 samples/hour.
          </dd>

          <dt>iaga2002</dt>
          <dd>
            <code>345600 samples</code> = 4 elements * 24 hours * 3600 samples/hour.
          </dd>
        </dl>

        <p>
          NOTE: while the <code>json</code> format supports fewer total samples per
          request, users may request fewer elements to retrieve longer intervals.
        </p>


        <h2>Parameters</h2>
        <dl>
          <dt>id</dt>
          <dd>
            Observatory code.
            Required.<br/>
            Valid values: {metadata}
          </dd>

          <dt>starttime</dt>
          <dd>
            Time of first requested data.<br/>
            Default: start of current UTC day<br/>
            Format: ISO8601 (<code>YYYY-MM-DDTHH:MM:SSZ</code>)<br/>
            Example: <code>{date}</code>
          </dd>

          <dt>endtime</dt>
          <dd>
            Time of last requested data.<br/>
            Default: starttime + 24 hours<br/>
            Format: ISO8601 (<code>YYYY-MM-DDTHH:MM:SSZ</code>)<br/>
            Example: <code>{date}</code>
          </dd>

          <dt>elements</dt>
          <dd>
            Comma separated list of requested elements.<br/>
            Default: <code>X,Y,Z,F</code><br/>
          </dd>

          <dt>sampling_period</dt>
          <dd>
            Interval in seconds between values.<br/>
            Default: <code>60</code><br/>
            Valid values:
              <code>1</code>,
              <code>60</code>
          </dd>

          <dt>type</dt>
          <dd>
            Type of data.<br/>
            Default: <code>variation</code>
            Valid values:
              <code>variation</code>,
               <code>adjusted</code>,
               <code>quasi-definitive</code>,
               <code>definitive</code><br/>
            <small>
              NOTE: the USGS web service also supports specific EDGE location codes.
              For example:
                  <code>R0</code> is "internet variation",
                  <code>R1</code> is "satellite variation".
            </small>
          </dd>

          <dt>format</dt>
          <dd>
            Output format.<br/>
            Default: <code>iaga2002</code><br/>
            Valid values:
              <code>iaga2002</code>.
          </dd>
        </dl>
        '''.format(metadata=self.metadata, date=self.date)
        return usage_body
