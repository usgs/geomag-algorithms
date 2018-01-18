"""Factory that loads html for Web Service Usage Documentation"""
from datetime import datetime
from geomagio.ObservatoryMetadata import ObservatoryMetadata


class WebServiceUsage(object):
    def __init__(self, metadata=None):
        metadata = metadata or ObservatoryMetadata().metadata.keys()
        self.date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.metadata = ', '.join(sorted(metadata))

    def set_usage_page(self, start_response):
        """Set body of Web Service Usage Documentation Page"""
        start_response('200 OK',
                [
                    ("Content-Type", "text/html")
                ])
        usage_body = """
            <head>
              <title>Geomag Web Service Usage</title>
              <meta charset="utf-8"/>
              <meta name="viewport" content="width=device-width,
                    initial-scale=1"/>
              <link href="/theme/site/geomag/index.scss" type="text/css">
              <style>
                  code,
                  pre {{
                    background: #f8f8f8;
                    border-radius: 3px;
                    color: #555;
                    font-family: monospace;
                  }}
              </style>
            </head>

            <body>
                <main role="main" class="page" aria-labelledby="page-header">
                <header class="page-header" id="page-header">
                    <h1>Geomag Web Service Usage</h1>
                </header>


                <h2>Example Requests</h3>
                 <dl>
                    <b>BOU observatory data for current UTC day in IAGA2002
                            format</b>
                    <dd>
                    <a href="http://geomag.usgs.gov/ws/edge/?id=BOU">
                            http://geomag.usgs.gov/ws/edge/?id=BOU</a>
                    </dd>


                <h2>Parameters</h2>
                <dl>
                    <b>id</b>
                    <dd>
                        Observatory code.
                        Required.<br/>
                        Valid values: <code>{metadata}</code>
                    </dd>

                    <b>starttime</b>
                    <dd>
                        Time of first requested data.<br/>
                        Default: start of current UTC day<br/>
                        Format: ISO8601
                                (<code>YYYY-MM-DDTHH:MM:SSZ</code>)<br/>
                        Example: <code>{date}</code>
                    </dd>

                    <b>endtime</b>
                    <dd>
                        Time of last requested data.<br/>
                        Default: starttime + 24 hours<br/>
                        Format: ISO8601
                                (<code>YYYY-MM-DDTHH:MM:SSZ</code>)<br/>
                        Example: <code>{date}</code>
                    </dd>

                    <b>elements</b>
                    <dd>
                        Comma separated list of requested elements.<br/>
                        Default: <code>X,Y,Z,F</code><br/>
                        Valid values: <code>D, DIST, DST, E, E-E, E-N, F, G,
                                H, SQ, SV, UK1, UK2, UK3, UK4, X, Y, Z</code>
                                <br/>
                    </dd>
                    <b>sampling_period</b>
                    <dd>
                        Interval in seconds between values.<br/>
                        Default: <code>60</code><br/>
                        Valid values:
                          <code>1</code>,
                          <code>60</code>
                    </dd>

                    <b>type</b>
                    <dd>
                        Type of data.<br/>
                        Default: <code>variation</code><br/>
                        Valid values:
                          <code>variation</code>,
                           <code>adjusted</code>,
                           <code>quasi-definitive</code>,
                           <code>definitive</code><br/>
                    </dd>

                    <b>format</b>
                    <dd>
                        Output format.<br/>
                        Default: <code>iaga2002</code><br/>
                        Valid values:
                          <code>iaga2002</code>.
                    </dd>
                </dl>
              </main>


              <nav class="site-footer">
              <p> Not what you were looking for?<br/>
                  Search usa.gov: </p>
                <form class="site-search" role="search"
                        action="//search.usa.gov/search" method="get"
                        accept-charset="UTF-8">
                  <input name="utf8" type="hidden" value="x"/>
                  <input name="affiliate" type="hidden" value="usgs"/>
                  <input name="sitelimit" type="hidden" />
                  <input id="query" name="query" type="search"
                        placeholder="Search usa.gov..." title="Search"/>
                  <button type="submit">Search</button>
                </form>
              </nav>
            </body>
        """.format(metadata=self.metadata, date=self.date)
        return usage_body
