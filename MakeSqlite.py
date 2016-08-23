#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:set ts=4 sw=4 et:
#
# HKU POP Rolling Poll convert to SQLite format
#

import sys
assert(sys.version_info.major == 3) # Python3 only!

import urllib.request
import urllib.parse
import os.path
import csv
import itertools
import datetime

import lxml.html
import yaml
import sqlite3

def webscraping():
    'A generator to fetch all CSVY files of 2016 LegCo rolling data from HKU POP'
    # XPath 2.0 is not supported, so use substring() instead of ends-with()
    main_url = 'http://data.hkupop.hku.hk/v2/hkupop/lc_election/ch.html'
    xpath = "//a[text()='下載']/@href[substring(.,string-length(.)-string-length('.csvy')+1)='.csvy']"
    text = urllib.request.urlopen(main_url).read().decode('utf-8')
    dom = lxml.html.document_fromstring(text)
    csvyurls = [urllib.parse.urljoin(main_url,relurl) for relurl in dom.xpath(xpath)]
    for url in reversed(csvyurls):
        if 'lc2016_rolling' not in url: continue # prevent mistake
        yield url, urllib.request.urlopen(url).read().decode('utf-8')

def localscraping():
    'Simulate webscraping() by using local dir'
    import os
    files = [f for f in os.listdir() if f.endswith('.csvy')]
    for f in files:
        if 'LC2016_final_' not in f: continue # prevent mistake
        yield f, open(f,encoding='utf-8').read()

def deduce_name(url):
    "Deduce worksheet name from URL"
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

def buildsqlite(file_dest):
    columns = ['sourcefile']
    data = []
    answer = []
    # work on each URL, gather all data
    for url, csvy in localscraping():
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
                row[h] = datetime.datetime.strptime(row[h], "%Y%m%d").strftime("%Y-%m-%d")
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
    conn = sqlite3.connect(file_dest)
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    import argparse, textwrap
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
            HKU POP 2016 LegCo rolling poll raw data to SQLite conversion

            Copyright (c) 2016, Frontline Tech Workers.
            All rights reserved.

            Redistribution and use in source and binary forms, with or without
            modification, are permitted provided that the following conditions are met:

            1. Redistributions of source code must retain the above copyright notice, this
               list of conditions and the following disclaimer.
            2. Redistributions in binary form must reproduce the above copyright notice,
               this list of conditions and the following disclaimer in the documentation
               and/or other materials provided with the distribution.

            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
            ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
            WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
            DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
            ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
            (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
            LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
            ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
            (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
            SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
            """)
    )
    parser.add_argument("filename", nargs='?', default="RollingPoll.db", help="Output SQLite filename")
    args = parser.parse_args()
    buildsqlite(args.filename)
