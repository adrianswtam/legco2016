# 2016立法會選舉滾動民調一頁過
# HKU POP 2016 LegCo Rolling Poll One-Pager

Copyright (c) 2016, Adrian Tam & Frontline Tech Workers.

All rights reserved. Proudly made by Hongkongers.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

呢度有個Jupyter notebook，如果你run佢一次，佢會將港大民研最新嘅滾動民調畫成圖表畀你睇。為咗方便無裝Jupyter嘅朋友，我地都準備咗兩個分頁，分別係﹕

https://rawgit.com/fltw/legco2016/master/chart.html

同埋

https://rawgit.com/fltw/legco2016/master/chart8888.html

前者係統計有效支持度，即係除去未決定或者不打算投票嘅被訪者，而後者就包括游離嘅選民。睇圖嘅朋友可以係左邊剔選相應嘅候選人，佢支持度嘅變化就會係右邊出現。前線科技人員會每日更新資料。

系統需求: python3, Jupyter, bokeh 0.12, lxml, pyYAML

## 原始資料

是咁的，我都知唔係個個鍾意睇圖，所以我地都整咗MakeExcel.py，可以將港大民研嘅原始數據化成Excel，但係你就要裝Python3+xlsxwriter啦。

## 頭盔

呢度所有程式由前線科技人員制作，資料由香港大學民意研究計劃及選舉事務處取得，無人會保証任何嘢嘅準確性或客觀性。使用者應用自己個腦諗下先好再作任何解讀。呢個唔係投資產品，支持度將來亦可升可跌。

## 延伸閱讀

* 港大民研 https://www.hkupop.hku.hk/chinese/resources/lc2016/rolling/index.html
* 立法會選舉 http://www.elections.gov.hk/legco2016/chi/index.html
* 雷動計劃 https://www.facebook.com/ThunderGoHK/
* 前線科技人員 https://www.facebook.com/FrontlineTechWorkersConcernGroup/
