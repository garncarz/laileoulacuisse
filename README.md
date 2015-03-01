# L'aile ou la cuisse

This app creates a tray icon for an easy access to information about this week's menus of user's favourite restaurants.

It is written in Python 3, GUI is powered by GTK+ 3.

Fetching algorithms are written as plugins in the `fetcher` directory.
  They make use of `urllib.request`, so fetching online data is easy, cookie-aware connection is used by default.
Fetchers parse HTML, XML and even Word (using external program Antiword) documents using `lxml.etree`,
mainly by the means of XPath.
New/modified XPath queries can be easily tested online at http://videlibri.sourceforge.net/cgi-bin/xidelcgi.
