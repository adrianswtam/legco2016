# -*- coding: utf-8 -*-
# vim:set ts=4 sw=4 et:
#
# Copyright (c) 2016 Adrian Tam & Frontline Tech Workers
# All Rights Reserved.
#
# Released under 2-clause BSD license.
#
#
from bokeh.plotting import figure
from bokeh.io import output_notebook, show
from bokeh.models import CheckboxGroup, CustomJS, Panel, Tabs
from bokeh.layouts import row
from bokeh.palettes import brewer

from ipy_table import make_table, set_global_style, set_cell_style
from IPython.display import HTML, display

from datetime import datetime
import sqlite3
import sys
import urllib.request
import urllib.parse
import os.path
import csv
import itertools

import lxml.html
import yaml

assert(sys.version_info.major == 3) # Python3 only!

def webscraping():
    'A generator to fetch all CSVY files of 2016 LegCo rolling data from HKU POP'
    # XPath 2.0 is not supported, so use substring() instead of ends-with()
    main_url = 'http://data.hkupop.hku.hk/hkupop/lc_election/ch.html'
    xpath = "//a[text()='下載']/@href[substring(.,string-length(.)-string-length('.csvy')+1)='.csvy']"
    text = urllib.request.urlopen(main_url).read().decode('utf-8')
    dom = lxml.html.document_fromstring(text)
    csvyurls = [urllib.parse.urljoin(main_url,relurl) for relurl in dom.xpath(xpath)]
    for url in reversed(csvyurls):
        if 'lc2016_rolling' not in url: continue # prevent mistake
        yield url, urllib.request.urlopen(url).read().decode('utf-8')

def deduce_name(url):
    "Deduce filename from URL"
    return os.path.basename(urllib.parse.urlsplit(url).path).rsplit('.',1)[0]

def redness(cur):
    "Add the redness table"
    data = [
       # region value redness who
         ['SuperDC',  801, -0.3, '民主黨 涂謹申']
        ,['SuperDC',  802,  1.0, '民建聯 李慧瓊']
        ,['SuperDC',  803, -0.3, '民主黨 鄺俊宇']
        ,['SuperDC',  804, -0.3, '民協 何啟明']
        ,['SuperDC',  805, -0.3, '公民黨 陳琬琛']
        ,['SuperDC',  806,  1.0, '工聯會 王國興']
        ,['SuperDC',  807, -0.5, '新同盟 關永業']
        ,['SuperDC',  808, -0.5, '街工 梁耀忠']
        ,['SuperDC',  809,  1.0, '民建聯 周浩鼎']
        ,['HKIsland',   1,  0.5, '民主思路 黃梓謙']
        ,['HKIsland',   2, -0.8, '人民力量 劉嘉鴻']
        ,['HKIsland',   3,  0.8, '新民黨 葉劉淑儀']
        ,['HKIsland',   4, -0.3, '工黨 何秀蘭']
        ,['HKIsland',   5,  1.0, '民建聯 張國鈞']
        ,['HKIsland',   6,  0.3, '女人係雞 詹培忠']
        ,['HKIsland',   7, -1.0, '熱普城 鄭錦滿']
        ,['HKIsland',   8, -0.3, '香港眾志 羅冠聰']
        ,['HKIsland',   9,  0.3, '基右 沈志超']
        ,['HKIsland',  10,  0.1, '香港電視 王維基']
        ,['HKIsland',  11, -0.5, '傘兵 徐子見']
        ,['HKIsland',  12, -0.5, '公專聯 司馬文']
        ,['HKIsland',  13, -0.3, '民主黨 許智峰']
        ,['HKIsland',  14, -0.3, '公民黨 陳淑莊']
        ,['HKIsland',  15,  1.0, '工聯會 郭偉強']
        ,['KlnWest',    1, -0.8, '社民連 吳文遠']
        ,['KlnWest',    2, -0.5, '本土力量 何志光']
        ,['KlnWest',    3, -0.3, '公民黨 毛孟靜']
        ,['KlnWest',    4,  1.0, '經民聯 梁美芬']
        ,['KlnWest',    5, -0.3, '民協 譚國橋']
        ,['KlnWest',    6, -0.8, '維園衝鋒 朱韶洪']
        ,['KlnWest',    7, -1.0, '熱普城 黃毓民']
        ,['KlnWest',    8, -0.3, '民主黨 黃碧雲']
        ,['KlnWest',    9,  0.1, '二奶可惡 林依麗']
        ,['KlnWest',   10,  1.0, '民建聯 蔣麗芸']
        ,['KlnWest',   11,  0.8, '政研會 關新偉']
        ,['KlnWest',   12, -0.7, '民主教室 劉小麗']
        ,['KlnWest',   13, -0.7, '青年新政 游蕙禎']
        ,['KlnWest',   14,  0.8, '乜水 李泳漢']
        ,['KlnWest',   15,  0.1, '新思維 狄志遠']
        ,['KlnEast',    1,  1.0, '工聯會 黃國健']
        ,['KlnEast',    2, -0.3, '工黨 胡穗珊']
        ,['KlnEast',    3,  1.0, '愛港之聲 高達斌']
        ,['KlnEast',    4, -0.5, '前綫 譚香文']
        ,['KlnEast',    5,  1.0, '中聯辦 謝偉俊']
        ,['KlnEast',    6,  1.0, '民建聯 柯創盛']
        ,['KlnEast',    7,  0.8, '乜水 呂永基']
        ,['KlnEast',    8, -0.3, '民主黨 胡志偉']
        ,['KlnEast',    9, -0.3, '公民黨 譚文豪']
        ,['KlnEast',   10, -1.0, '熱普城 黃洋達']
        ,['KlnEast',   11, -1.0, '東九社區 陳澤滔']
        ,['KlnEast',   12, -0.8, '人民力量 譚得志']
        ,['NTWest',     1, -0.5, '街工 黃潤達']
        ,['NTWest',     2, -0.3, '民主黨 尹兆堅']
        ,['NTWest',     3,  0.8, '政研會 高志輝']
        ,['NTWest',     4,  0.8, '自由黨 周永勤']
        ,['NTWest',     5, -1.0, '熱普城 鄭松泰']
        ,['NTWest',     6,  1.0, '經民聯 鄺官穩']
        ,['NTWest',     7,  0.8, '新民黨 田北辰']
        ,['NTWest',     8,  1.0, '中聯辦 何君堯']
        ,['NTWest',     9,  1.0, '民建聯 梁志祥']
        ,['NTWest',    10, -0.3, '公民黨 郭家麒']
        ,['NTWest',    11, -0.8, '社民連 黃浩銘']
        ,['NTWest',    12, -0.3, '工黨 李卓人']
        ,['NTWest',    13, -0.7, '青年新政 黃俊傑']
        ,['NTWest',    14,  1.0, '工聯會 麥美娟']
        ,['NTWest',    15, -0.3, '民協 馮檢基']
        ,['NTWest',    16,  1.0, '民建聯 陳恆鑌']
        ,['NTWest',    17,  0.8, '乜水 張慧晶']
        ,['NTWest',    18,  0.8, '乜水 呂智恆']
        ,['NTWest',    19, -0.7, '乜水 湯詠芝']
        ,['NTWest',    20, -0.7, '八鄉 朱凱迪']
        ,['NTEast',     1,  0.5, '保皇黨 方國珊']
        ,['NTEast',     2, -0.3, '民主黨 林卓廷']
        ,['NTEast',     3,  0.1, '新思維 廖添誠']
        ,['NTEast',     4, -1.0, '熱普城 陳云根']
        ,['NTEast',     5, -0.8, '社民連 梁國雄']
        ,['NTEast',     6, -0.3, '工黨 張超雄']
        ,['NTEast',     7, -0.3, '公民黨 楊岳橋']
        ,['NTEast',     8,  0.5, '民主思路 麥嘉晉']
        ,['NTEast',     9, -0.3, '退民主黨 鄭家富']
        ,['NTEast',    10,  1.0, '民建聯 葛珮帆']
        ,['NTEast',    11,  0.8, '新界人 侯志強']
        ,['NTEast',    12,  0.8, '自由黨 李梓敬']
        ,['NTEast',    13,  1.0, '工聯會 鄧家彪']
        ,['NTEast',    14, -0.5, '新同盟 范國威']
        ,['NTEast',    15,  0.8, '乜水 陳玉娥']
        ,['NTEast',    16, -0.5, '乜水 黃琛瑜']
        ,['NTEast',    17,  0.8, '正義聯盟 李偲嫣']
        ,['NTEast',    18, -0.8, '人民力量 陳志全']
        ,['NTEast',    19, -0.7, '青年新政 梁頌恆']
        ,['NTEast',    20, -0.5, '乜水 梁金成']
        ,['NTEast',    21,  0.8, '新民黨 容海恩']
        ,['NTEast',    22,  1.0, '民建聯 陳克勤']
    ]
    cur.execute("CREATE TABLE redness(region,num,redness,who)")
    cur.executemany("INSERT INTO redness(region,num,redness,who) VALUES(?,?,?,?)", data)

def buildsqlite():
    " Produce cursor to SQLite holding all latest data from HKUPOP "
    columns = ['sourcefile']
    data = []
    answer = []
    # work on each URL, gather all data
    for url, csvy in webscraping():
        print(url)
        data_name = deduce_name(url)
        lines = csvy.split("\n")
        # Extract and parse the CSVY metadata part
        fields_def_yaml = [ln[1:] for ln in itertools.takewhile(lambda s:s[0]=='#', lines)]
        if not fields_def_yaml:
            # the metadata is not in comment, look for limiters instead
            fields_def_yaml = [ln for ln in itertools.takewhile(lambda s:not s.startswith('---'), lines[1:])]
        else:
            fields_def_yaml = fields_def_yaml[1:-1]
        if not answer: # assume all are the same, so parse only the first one
            fields_def = yaml.load("\n".join(fields_def_yaml))
            assert('fields' in fields_def)
            assert(all('name' in f for f in fields_def['fields']))
            for f in fields_def['fields']:
                if 'labels' not in f: continue
                for answertext, code in f['labels'].items():
                    answer.append([f['name'], int(code), answertext])
        # Extract and parse the CSVY data part
        csvdata = list(csv.reader([ln+'\n' for ln in lines[len(fields_def_yaml)+2:]]))
        # parse header, and gather data
        header = csvdata[0]
        if len(header) < len(csvdata[1]):
            # in case header row is shorter, align to right
            header = ['_'+str(int(n+1)) for n in range(len(csvdata[1])-len(header))] + header
        data += [
            dict(zip(header, row), sourcefile=data_name) for row in csvdata[1:] if row
        ]
        # remember all column names
        for h in header:
            if h not in columns:
                columns.append(h)
    # Review data, make sure all keys exist
    for row in data:
        for h in columns:
            if h not in row or not row[h] or row[h] == 'NA':
                row[h] = None
            elif h == 'date':
                row[h] = datetime.strptime(row[h], "%Y%m%d").strftime("%Y-%m-%d")
            elif row[h].isdigit():
                row[h] = int(row[h])
            else:
                try:
                    row[h] = float(row[h])
                except:
                    pass
    # Write to SQLite
    try:
        os.unlink(file_dest)
    except:
        pass
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute("CREATE TABLE answers(region,value,answer)")
    cur.executemany("INSERT INTO answers(region,value,answer) VALUES(?,?,?)", answer)
    columnlist = ",".join(columns)
    paramlist = ",".join(':'+c for c in columns)
    redness(cur)
    cur.execute("CREATE TABLE poll(%s)" % columnlist)
    cur.executemany("INSERT INTO poll(%s) VALUES(%s)" % (columnlist, paramlist), data)
    sql = ['CREATE TABLE overall AS']
    for region,col in [("HKIsland","R2"),("KlnWest","R3"),("KlnEast","R4"),("NTWest","R5"),("NTEast","R6"),("SuperDC","R8")]:
        sql += [
            "SELECT"
                ,"'%s' AS region," % region
                ,"SUBSTR(X.sourcefile,14,13) AS daterange,"
                ,"COUNT(*) AS votes,"
                ,"COUNT(*)*100.0/(SELECT COUNT(*) FROM poll WHERE",col,"IS NOT NULL AND sourcefile=X.sourcefile) AS vote_pct,"
                ,"SUM(X.weight)*100.0/(SELECT SUM(weight) FROM poll WHERE",col,"IS NOT NULL AND sourcefile=X.sourcefile) AS adj_pct,"
                ,"SUM(X.weight)*100.0/(SELECT SUM(weight) FROM poll WHERE",col,">0 AND",col,"<30 AND sourcefile=X.sourcefile) AS valid_pct,"
                ,col, "AS num,"
                ,"Y.redness AS redness,"
                ,"Y.who AS candid"
            ,("FROM poll X LEFT JOIN redness Y ON Y.region='%s' AND Y.num=X.%s" if region!='SuperDC' else
              "FROM poll X LEFT JOIN redness Y ON Y.region='%s' AND Y.num=800+X.%s"
              )% (region,col)
            ,"WHERE X."+col, "IS NOT NULL GROUP BY X.sourcefile, X."+col
            ,"UNION ALL"
        ]
    cur.execute(' '.join(sql[:-1]))
    return conn,cur

def get_trend(cur, region, num):
    "Read from database the rolling poll trend"
    sql = "SELECT daterange, candid, redness, valid_pct FROM overall WHERE region=? AND num=? ORDER BY daterange"
    rows = list(cur.execute(sql, (region, num)))
    if not rows:
        return None, None, []
    ret = []
    candid = rows[0][1]
    redness = rows[0][2]
    for row in rows:
        date = datetime.strptime('2016'+row[0][-4:], "%Y%m%d")
        ret.append([date, row[3]])
    return candid, redness, ret

def get_rank(cur, region, date):
    "Read from database the latest ranking"
    if isinstance(date, datetime):
        datestr = date.strftime("%m%d")
    elif isinstance(date, str):
        datestr = date
        assert(len(datestr)==4)
    elif isinstance(date, int):
        datestr = "08%02d" % date
    else:
        raise TypeError
    assert(len(datestr)==4)
    sql = "SELECT daterange, num, candid, redness, valid_pct " \
          "FROM overall " \
          "WHERE region=? AND daterange LIKE '%%%s' AND num<30 ORDER BY valid_pct DESC" % datestr
    rows = list(cur.execute(sql, (region,)))
    if not rows:
        return None, []
    ret = []
    daterange = rows[0][0]
    for row in rows:
        ret.append(row[1:])
    return daterange, ret

# colours
bluecode = brewer['Blues'][9]
redcode = brewer["PuRd"][9]

def getcolour(redness, for_table=False):
    " Return color to use in chart and in table, based on redness "
    if   redness == -1.0:  offset = 0
    elif redness == -0.8:  offset = 1
    elif redness == -0.7:  offset = 1
    elif redness == -0.5:  offset = 2
    elif redness == -0.3:  offset = 2
    elif redness == -0.1:  offset = 2
    elif redness ==  0.1:  offset = 2
    elif redness ==  0.3:  offset = 2
    elif redness ==  0.5:  offset = 1
    elif redness ==  0.8:  offset = 0
    elif redness ==  1.0:  offset = 0
    else: offset = -1
    if for_table:
        offset = offset+4 if offset>=0 else 0
    return redcode[offset] if redness > 0 else bluecode[offset]

regions = [["香港島","HKIsland",6],
           ["九龍西","KlnWest",6],["九龍東","KlnEast",5],
           ["新界西","NTWest",9],["新界東","NTEast",9],
           ["超區","SuperDC",5]]

def create_charts(cur):
    " Create chart on each tab for 5 regions + super DC "
    tabs = []
    for title,code,seats in regions:
        # chart components
        p = figure(x_axis_label='滾動日期', y_axis_label='有效支持%', x_axis_type="datetime")
        candids = []
        earliest_date, latest_date = None, None
        for n in range(1,30):
            candid, redness, trend = get_trend(cur, code, n)
            if not trend: continue
            earliest_date, latest_date = trend[0][0], trend[-1][0]
            colour = getcolour(redness)
            line = p.line([d for d,_ in trend], [p for _,p in trend], color=colour, line_width=2, line_alpha=0.9)
            label = p.text([trend[-1][0]], [trend[-1][1]], text=[candid.rsplit(None,1)[-1]],
                           text_align='right', text_alpha=0.9, text_baseline='bottom', text_color=colour,
                           text_font_size="9pt", y_offset=0.25)
            candids.append([n, candid, colour, trend[-1][1], line, label])
        p.line([earliest_date, latest_date],[100.0/seats, 100.0/seats],
               line_dash=[6,3], color="black", line_width=2, line_alpha=0.5)
        # control
        all_lines = [n for n,_ in enumerate(candids)]
        top_5 = [n for _,n in sorted([(c[3],n) for n,c in enumerate(candids)], reverse=True)[:5]]
        for n in all_lines:
            if n not in top_5:
                candids[n][-1].visible = candids[n][-2].visible = False
        customjs_params = [("line%d"%n, candid[-2]) for n,candid in enumerate(candids)] + \
                          [("label%d"%n, candid[-1]) for n,candid in enumerate(candids)]
        jscode = '''
            var lines = [%s];
            var labels = [%s];
            for (var n=0; n<lines.length; n++) {
                 lines[n].visible = (cb_obj.active.indexOf(n) >= 0);
                labels[n].visible = (cb_obj.active.indexOf(n) >= 0);
            };''' % (",".join("line%d" % n for n in all_lines), ",".join("label%d" % n for n in all_lines))
        checkbox = CheckboxGroup(labels=[str(800+c[0] if code=='SuperDC' else c[0])+' '+c[1] for c in candids],
                                 active=top_5)
        checkbox.callback = CustomJS(args=dict(customjs_params), code=jscode)
        # layout and show
        layout = row(checkbox, p)
        tab = Panel(child=layout, title=title+"民調")
        tabs.append(tab)
    # build and return 
    return Tabs(tabs=tabs)

def create_tables(cur):
    " Produce ranking table "
    tabs = []
    lastdate = list(cur.execute("SELECT MAX(daterange) FROM overall"))[0][0]
    rangetext = lastdate[6:8]+'/'+lastdate[4:6]+'至'+lastdate[11:13]+'/'+lastdate[9:11]
    for title,code,_ in regions:
        daterange, rankdata = get_rank(cur, code, lastdate[-4:])
        if code == 'SuperDC':
            for n,row in enumerate(rankdata):
                row = list(row)
                row[0] += 800
                rankdata[n] = row
        tabletitle = rangetext+title+'民調排名'
        human, beast = [r for r in rankdata if r[2]<0], [r for r in rankdata if r[2]>0]
        header = ["編號","政黨","候選人","有效%",""]
        tabledata = [[tabletitle]+([""]*10),["非建制"]+([""]*5)+["建制"]+([""]*4),header + [""] + header]
        for n in range(max(len(human), len(beast))):
            tabledata.append([])
            if len(human)>n:
                tabledata[-1].extend([human[n][0]]+human[n][1].split()+["%.2f"%human[n][3],n+1])
            else:
                tabledata[-1].extend(['']*5)
            if len(beast)>n:
                tabledata[-1].extend(['',beast[n][0]]+beast[n][1].split()+["%.2f"%beast[n][3],n+1])
            else:
                tabledata[-1].extend(['']*6)
        table = make_table(tabledata)
        set_global_style(no_border='all',align="center")
        set_cell_style(0,0, column_span=11, bold=True, color=brewer['Greens'][8][4])
        set_cell_style(1,0, column_span=5, bold=True, color=getcolour(-2,True), font_color="white")
        set_cell_style(1,6, column_span=5, bold=True, color=getcolour(2,True), font_color="white")
        for n in range(11):
            if n < 5:
                set_cell_style(2,n, bold=True, color=getcolour(-2,True), font_color="white")
            elif n > 5:
                set_cell_style(2,n, bold=True, color=getcolour(2,True), font_color="white")
        for m in range(max(len(human), len(beast))):
            hcolor = getcolour(human[m][2] if len(human)>m else -0.1, True)
            bcolor = getcolour(beast[m][2] if len(beast)>m else  0.1, True)
            for n in range(11):
                if n < 5:
                    set_cell_style(3+m,n, color=hcolor)
                elif n > 5:
                    set_cell_style(3+m,n, color=bcolor)
        display(HTML(table._repr_html_()))
