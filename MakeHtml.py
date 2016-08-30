# -*- coding: utf-8 -*-

from FrontlineTechWorkerRollingHelper import *

conn, cur = buildsqlite("poll.db")
tabpanel1 = create_charts(cur, False)
tabpanel2 = create_charts(cur, True)
tabpanel = Tabs(tabs=[Panel(child=tabpanel1, title="不包游離票"),Panel(child=tabpanel2, title="包括游離票")])

from bokeh.embed import notebook_div, file_html
from bokeh.resources import CDN
html = file_html(tabpanel,CDN)
open("chart.html","w").write(html)

tabpanel1 = create_charts(cur, False, True)
tabpanel2 = create_charts(cur, True, True)
tabpanel = Tabs(tabs=[Panel(child=tabpanel1, title="不包游離票"),Panel(child=tabpanel2, title="包括游離票")])
html = file_html(tabpanel,CDN)
open("chart.raw.html","w").write(html)
