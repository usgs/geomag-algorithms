"""Factory that loads html for Web Service Usage Documentation"""
from datetime import datetime
from geomagio.ObservatoryMetadata import ObservatoryMetadata


class WebServiceUsage(object):
    def __init__(self, metadata=None, mount_path=None, host_prefix=None):
        metadata = metadata or list(ObservatoryMetadata().metadata.keys())
        self.date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.metadata = ', '.join(sorted(metadata))
        self.mount_path = mount_path
        self.host_prefix = host_prefix

    def __call__(self, environ, start_response):
        """Implement documentation page"""
        start_response('200 OK',
                [
                    ("Content-Type", "text/html")
                ])
        if self.mount_path is None:
            self.mount_path = '/ws/edge'
        if self.host_prefix is None:
            self.host_prefix = environ['HTTP_HOST']
        usage_page = self.set_usage_page()
        return [usage_page]

    def set_usage_page(self):
        """Set body of Web Service Usage Documentation Page"""
        stylesheet = "https://geomag.usgs.gov/theme/site/geomag/index.css"
        ids = ""
        observatories = self.metadata.split(", ")
        for idx, obs_id in enumerate(observatories):
            ids += "<code>" + obs_id + "</code>"
            if idx != len(observatories) - 1:
                ids += ", "
            if idx % 9 == 0 and idx != 0:
                ids += "<br/>"
        usage_body = """
            <!doctype html>
            <html>
            <head>
              <title>Geomag Web Service Usage</title>
              <base href={host_prefix}>
              <meta charset="utf-8"/>
              <meta name="viewport" content="width=device-width,
                    initial-scale=1"/>
              <link rel="stylesheet" href={stylesheet} type="text/css">
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

            <body style="font-size:135%">
                <main role="main" class="page" aria-labelledby="page-header">
                <header class="page-header" id="page-header">
                    <h1>Geomag Web Service Usage</h1>
                </header>


                <h2>Example Requests</h3>
                 <dl>
                    <dt>BOU observatory data for current UTC day in IAGA2002
                            format</dt>
                    <dd>
                    <a href="{link1}">
                            {link1}</a>
                    </dd>
                    <dt>BOU observatory data for current UTC day in JSON
                            format</dt>
                    <dd>
                    <a href="{link2}">
                            {link2}</a>
                    </dd>
                    <dt>BOU electric field data for current UTC day in
                            IAGA2002 format</dt>
                    <dd>
                    <a href="{link3}">
                            {link3}</a>
                    </dd>

                <h2>Parameters</h2>
                <dl>
                    <dt>id</dt>
                    <dd>
                        Observatory code.
                        Required.<br/>
                        Valid values:<br/>
                                {metadata}
                    </dd>

                    <dt>starttime</dt>
                    <dd>
                        Time of first requested data.<br/>
                        Default: start of current UTC day<br/>
                        Format: ISO8601
                                (<code>YYYY-MM-DDTHH:MM:SSZ</code>)<br/>
                        Example: <code>{date}</code>
                    </dd>

                    <dt>endtime</dt>
                    <dd>
                        Time of last requested data.<br/>
                        Default: starttime + 24 hours<br/>
                        Format: ISO8601
                                (<code>YYYY-MM-DDTHH:MM:SSZ</code>)<br/>
                        Example: <code>{date}</code>
                    </dd>

                    <dt>elements</dt>
                    <dd>
                        Comma separated list of requested elements.<br/>
                        Default: <code>X</code>,<code>Y</code>,<code>Z</code>,
                                <code>F</code><br/>
                        Valid values: <code>D</code>, <code>DIST</code>,
                                <code>DST</code>, <code>E</code>,
                                <code>E-E</code>, <code>E-N</code>,
                                <code>F</code>, <code>G</code>,
                                <code>H</code>, <code>SQ</code>,
                                <code>SV</code>, <code>UK1</code>,
                                <code>UK2</code>, <code>UK3</code>,
                                <code>UK4</code>, <code>X</code>,
                                <code>Y</code>, <code>Z</code>
                                <br/>
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
                        Default: <code>variation</code><br/>
                        Valid values:
                          <code>variation</code>,
                           <code>adjusted</code>,
                           <code>quasi-definitive</code>,
                           <code>definitive</code><br/>
                        <small>
                          NOTE: the USGS web service also supports specific
                          EDGE location codes.
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
            </html>
        """.format(metadata=ids, date=self.date,
                host_prefix=self.host_prefix,
                stylesheet=stylesheet,
                link1=self.host_prefix + self.mount_path + "/?id=BOU",
                link2=self.host_prefix + self.mount_path +
                "/?id=BOU&format=json",
                link3=self.host_prefix + self.mount_path +
                "/?id=BOU&elements=E-N,E-E",)
        return usage_body
