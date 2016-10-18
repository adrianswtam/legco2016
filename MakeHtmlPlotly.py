# -*- coding: utf-8 -*-

from FrontlineTechWorkerRollingHelper import *
import plotly.plotly as py
import plotly.offline.offline as po
import plotly.graph_objs as go

conn, cur = buildsqlite("poll.db", True)

def to_rgba(colourstr,alpha):
    rr = int(colourstr[1:3],16)
    gg = int(colourstr[3:5],16)
    bb = int(colourstr[5:7],16)
    return "rgba(%d,%d,%d,%f)" % (rr,gg,bb,alpha)

# loop on six regions and produce div
divhtmls = []
for title, code, seats in regions:
    candids = [[n,candid,redness,trend] for n in range(1,30)
                                        for candid,redness,trend in [get_trend(cur,code,n)]
                                        if trend]
    top_candids = set(n for _,n in sorted([(trend[-1][1],n) for n,_,_,trend in candids], reverse=True)[:seats])
    earliest_date = min(trend[0][0] for _,_,_,trend in candids)
    latest_date = max(trend[-1][0] for _,_,_,trend in candids)
    components = []

    # for each candidate, find the trend line and error region
    for n, name, redness, trend in candids:
        colour = getcolour(redness)
        x_val = [d.strftime("%Y-%m-%d") for d,_,_ in trend]
        y_val = [p for _,p,_ in trend]
        y_upper = [p+e for _,p,e in trend]
        y_lower = [max(p-e,0.0) for _,p,e in trend]
        y_text = ["%.1f\u00B1%.1f%%" % (p,e) for _,p,e in trend]
        line = go.Scatter(
            legendgroup = name,
            showlegend = True,
            name = "%d %s" % (n, name),
            visible = True if n in top_candids else 'legendonly',
            x = x_val,
            y = y_val,
            text = y_text,
            hoverinfo = "x+text+name",
            mode = 'lines+markers',
            line = {'color':colour, 'width':2, 'shape':'spline'}
        )
        shade = go.Scatter(
            legendgroup = name,
            showlegend = False,
            hoverinfo = "none",
            visible = True if n in top_candids else 'legendonly',
            x = x_val + x_val[::-1],
            y = y_upper + y_lower[::-1],
            fill = 'tozerox',
            fillcolor = to_rgba(colour,0.3),
            line = go.Line(color='transparent')
        )
        components.extend([line,shade])

    # Plot the chart with all components found
    layout = dict(
        title = title,
        hovermode = 'compare',
        xaxis = dict(title = "滾動民調日期", tickangle=45, tickformat="%d %b", hoverformat='%d %b'),
        yaxis = dict(title = "支持度%", hoverformat='.2f')
    )
    # to display in Jupyter directly instead of generating HTML code:
    #    po.iplot(dict(data=components, layout=layout), filename='hkisland')
    divhtmls.append((title, po.plot(dict(data=components, layout=layout), output_type="div", include_plotlyjs=False)))

# Get plot.ly JS code
jscode = po.get_plotlyjs()

# Construct tabbed HTML
tabcss = '''
.chart-tab-wrap {
  -webkit-transition: 0.3s box-shadow ease;
          transition: 0.3s box-shadow ease;
  border-radius: 6px;
  max-width: 100%;
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-flex-wrap: wrap;
      -ms-flex-wrap: wrap;
          flex-wrap: wrap;
  position: relative;
  list-style: none;
  background-color: #fff;
  margin: 40px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
}
.chart-tab-wrap:hover {
  box-shadow: 0 12px 23px rgba(0, 0, 0, 0.23), 0 10px 10px rgba(0, 0, 0, 0.19);
}
.chart-tab {
  display: none;
}
''' + ''.join('''
.chart-tab:checked:nth-of-type(%d) ~ .chart-tab__content:nth-of-type(%d) {
  opacity: 1;
  -webkit-transition: 0.5s opacity ease-in, 0.8s transform ease;
          transition: 0.5s opacity ease-in, 0.8s transform ease;
  position: relative;
  top: 0;
  z-index: 100;
  -webkit-transform: translateY(0px);
          transform: translateY(0px);
  text-shadow: 0 0 0;
}''' % (n+1,n+1) for n in range(len(divhtmls))) + '''
.chart-tab:first-of-type:not(:last-of-type) + label {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.chart-tab:not(:first-of-type):not(:last-of-type) + label {
  border-radius: 0;
}
.chart-tab:last-of-type:not(:first-of-type) + label {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
.chart-tab:checked + label {
  background-color: #fff;
  box-shadow: 0 -1px 0 #fff inset;
  cursor: default;
}
.chart-tab:checked + label:hover {
  box-shadow: 0 -1px 0 #fff inset;
  background-color: #fff;
}
.chart-tab + label {
  box-shadow: 0 -1px 0 #eee inset;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  display: block;
  text-decoration: none;
  color: #333;
  -webkit-box-flex: 3;
  -webkit-flex-grow: 3;
      -ms-flex-positive: 3;
          flex-grow: 3;
  text-align: center;
  background-color: #f2f2f2;
  -webkit-user-select: none;
     -moz-user-select: none;
      -ms-user-select: none;
          user-select: none;
  text-align: center;
  -webkit-transition: 0.3s background-color ease, 0.3s box-shadow ease;
  transition: 0.3s background-color ease, 0.3s box-shadow ease;
  height: 50px;
  box-sizing: border-box;
  padding: 15px;
}
.chart-tab + label:hover {
  background-color: #f9f9f9;
  box-shadow: 0 1px 0 #f4f4f4 inset;
}
.chart-tab__content {
  padding: 10px 25px;
  background-color: transparent;
  position: absolute;
  width: 100%;
  z-index: -1;
  opacity: 0;
  left: 0;
  -webkit-transform: translateY(-3px);
          transform: translateY(-3px);
  border-radius: 6px;
}
.chart-container {
  margin: 0 auto;
  display: block;
  width: 100%;
}
'''

tabhtml = '''
<div class="chart-container">
  <div class="chart-tab-wrap">
''' + ''.join('''
    <input type="radio" id="tab%d" name="tabGroup" class="chart-tab" %s>
    <label for="tab%d">%s</label>
''' % (n+1,('' if n else 'checked'),n+1,divhtml[0]) for n,divhtml in enumerate(divhtmls)) + ''.join('''
    <div class="chart-tab__content">%s</div>
''' % divhtml[1] for divhtml in divhtmls) + '''
  </div>
</div>
'''

outputhtml = '<!DOCTYPE html>\n<html><head><meta charset="utf-8"><style>'+tabcss+'</style>' + \
             '<script type="text/javascript">'+jscode+'</script>' + \
             '</head><body>' + tabhtml + '</body></html>'

open("chart.plotly.html","w").write(outputhtml)
