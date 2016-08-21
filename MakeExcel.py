#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:set ts=4 sw=4 et:
#
# HKU POP Rolling Poll convert to Excel format
#

import sys
assert(sys.version_info.major == 3) # Python3 only!

import urllib.request
import urllib.parse
import os.path
import csv
import itertools
import datetime
import math

import lxml.html
import yaml
import xlsxwriter

import arial10

def webscraping():
    'A generator to fetch all CSVY files of 2016 LegCo rolling data from HKU POP'
    # XPath 2.0 is not supported, so use substring() instead of ends-with()
    main_url = 'http://data.hkupop.hku.hk/hkupop/lc_election/ch.html'
    xpath = "//a[text()='下載']/@href[substring(.,string-length(.)-string-length('.csvy')+1)='.csvy']"
    text = urllib.request.urlopen(main_url).read().decode('utf-8')
    dom = lxml.html.document_fromstring(text)
    csvyurls = [urllib.parse.urljoin(main_url,relurl) for relurl in dom.xpath(xpath)]
    for url in reversed(csvyurls):
        yield url, urllib.request.urlopen(url).read().decode('utf-8')

def localscraping():
    'Simulate webscraping() by using local dir'
    import os
    files = [f for f in os.listdir() if f.endswith('.csvy')]
    for f in files:
        yield f, open(f,encoding='utf-8').read()

def deduce_name(url):
    "Deduce worksheet name from URL"
    filename = os.path.basename(urllib.parse.urlsplit(url).path).rsplit('.',1)[0]
    if filename.startswith('LC2016_final_'):
        # 滾動調查
        numfrags = [f for f in filename.split('_') if f.isdigit()]
        namefrags = []
        for f in numfrags:
            if len(f) == 8:
                namefrags.append(datetime.datetime.strptime(f, "%Y%m%d").strftime("%m-%d"))
            elif len(f) == 4:
                namefrags.append(datetime.datetime.strptime(f, "%m%d").strftime("%m-%d"))
            else:
                namefrags.append(f)
        if len(namefrags) == 2:
            return namefrags[0]+'至'+namefrags[1]+'滾動調查'
        else:
            return " ".join(namefrags)+'滾動調查'
    elif filename.startswith('LC2016PRE_dataset_'):
        return "提名期前民意調查"
    else:
        namefrags = []
        if '2008' in filename:
            namefrags.append('2008年')
        elif '2012' in filename:
            namefrags.append('2012年')
        if filename.startswith("RP"):
            namefrags.append("滾動調查")
        elif filename.startswith("XP"):
            namefrags.append("票站調查")
        if len(namefrags) == 2:
            return "".join(namefrags)
    return filename

def breaklabel(label):
    if not label or label[0] != '[':
        return label
    else:
        return label.replace(']',']\n',1)

def buildexcel(file_dest):
    # prepare an empty workbook
    workbook = xlsxwriter.Workbook(file_dest, {'default_date_format':'YYYY-mm-dd'})
    header_row_format = workbook.add_format({'bg_color':'#C2C2D6',
                                             'bottom':3, 'top':3,
                                             'text_wrap':True,
                                             'font_name':'Arial', 'font_size':10})
    data_row_format = workbook.add_format({'font_name':'Arial', 'font_size':10})
    # work on each URL, as one new worksheet
    for url, csvy in webscraping():
        print(url)
        lines = csvy.split("\n")
        # Extract and parse the CSVY metadata part
        fields_def_yaml = [ln[1:] for ln in itertools.takewhile(lambda s:s[0]=='#', lines)]
        if not fields_def_yaml:
            # the metadata is not in comment, look for limiters instead
            fields_def_yaml = [ln for ln in itertools.takewhile(lambda s:not s.startswith('---'), lines[1:])]
        else:
            fields_def_yaml = fields_def_yaml[1:-1]
        fields_def = yaml.load("\n".join(fields_def_yaml))
        assert('fields' in fields_def)
        assert(all('name' in f for f in fields_def['fields']))
        fields = {f['name']:f for f in fields_def['fields']}
        for name in fields:
            if 'labels' in fields[name]:
                labeltext = "\n".join(
                    [str(int(x2))+" : "+str(x1)
                     for x1,x2 in sorted(fields[name]['labels'].items(), key=lambda x:x[1])]
                )
                fields[name]['labels'] = labeltext
        # Extract and parse the CSVY data part
        csvdata = list(csv.reader([ln+'\n' for ln in lines[len(fields_def_yaml)+2:]]))
        # Create worksheet and set title
        worksheet = workbook.add_worksheet(deduce_name(url)) # new sheet at end
        # Header rows: label, labels, name
        header = csvdata[0]
        if len(header) < len(csvdata[1]):
            # in case header row is shorter, align to right
            header = [None] * (len(csvdata[1]) - len(header)) + header
        option = [fields.get(h,{}).get('labels',' ') for h in header]
        label = [breaklabel(fields.get(h,{}).get('label',' ')) for h in header]
        worksheet.write_row(0, 0, header, header_row_format)
        worksheet.write_row(1, 0, option, header_row_format)
        worksheet.write_row(2, 0, label, header_row_format)
        # Data rows
        for j, row in enumerate(csvdata[1:]):
            for i, col in enumerate(row):
                if header[i] == 'date':
                    row[i] = datetime.datetime.strptime(col, "%Y%m%d").date()
                elif col.isdigit():
                    row[i] = int(col)
                else:
                    try:
                        row[i] = float(col)
                    except:
                        row[i] = None if col == 'NA' else col
            worksheet.write_row(3+j, 0, row, data_row_format)
        # Add autofilter
        ignore_col = ['weight','caseid',None]
        maxrow = len(csvdata)+2
        minrow = 2
        mincol = min(i for i,c in enumerate(header) if c not in ignore_col)
        maxcol = max(i for i,c in enumerate(header) if c not in ignore_col)
        worksheet.autofilter(minrow, mincol, maxrow, maxcol)
        # Adjust column width: usually to fit the option text
        colwidths = []
        for c in range(len(header)):
            columndata = ["00000",header[c],option[c]]+[str(row[c]) for row in csvdata[1:] if len(row)>c]
            width = max(arial10.fitwidth(x) for x in columndata if x)
            worksheet.set_column(c, c, width/256.0)
            colwidths.append(width)
        # Adjust row height for option text row
        height = max(arial10.fitheight(x) for x in option if x)
        worksheet.set_row(1, height/18.0)
        # Adjust row height for option text row
        height = max(arial10.fitheight(x) for x in label if x)
        wrapped_add_height = max(
            arial10.fitheight("\n" * math.ceil(arial10.fitwidth(l)/w-1))
            for l,w in zip(label,colwidths)
        )
        worksheet.set_row(2, (height+wrapped_add_height)/18.0)
        # Freeze the 3 header rows
        worksheet.freeze_panes(3,0)
    # save to disk
    workbook.close()

if __name__ == '__main__':
    import argparse, textwrap
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
            HKU POP 2016 LegCo rolling poll raw data to Excel conversion

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
    parser.add_argument("filename", nargs='?', default="RollingPoll.xlsx", help="Output Excel filename")
    args = parser.parse_args()
    buildexcel(args.filename)
