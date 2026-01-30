import json
import numpy as np


def clean_series(series):
    return [None if np.isnan(x) else round(float(x), 2) for x in series]


def generate_market_chart(df):
    dates = df.index.strftime('%Y/%m/%d').tolist()
    values = clean_series(df['Close'])
    html = f"""
    <div id="m_chart" style="width:100%; height:450px; background:black;"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        var chart = echarts.init(document.getElementById('m_chart'), 'dark');
        chart.setOption({{
            backgroundColor:'#000', grid:{{left:'50', right:'20', top:'30', bottom:'40'}},
            tooltip:{{trigger:'axis'}},
            xAxis:{{type:'category', data:{json.dumps(dates)}, axisLabel:{{fontSize:10}}}},
            yAxis:{{type:'value', scale:true, splitLine:{{lineStyle:{{color:'#222'}}}}}},
            series:[{{name:'加權指數', type:'line', data:{json.dumps(values)}, smooth:true, lineStyle:{{color:'#FFFF00', width:3}}, areaStyle:{{color:'rgba(255,255,0,0.1)'}}, showSymbol:false}}]
        }});
        window.addEventListener('resize', function() {{ chart.resize(); }});
    </script>
    """
    return html


def generate_stock_chart(s_name, stock_id, df, trend_line_values):
    dates = df.index.strftime('%Y/%m/%d').tolist()
    k_vals = [[round(r.Open, 2), round(r.Close, 2), round(r.Low, 2), round(r.High, 2)] for r in df.itertuples()]
    volumes = [{"value": int(r.Volume), "itemStyle": {"color": '#ef232a' if r.Close >= r.Open else '#14b143'}} for r in
               df.itertuples()]

    sma5 = clean_series(df['SMA5']);
    sma10 = clean_series(df['SMA10'])
    sma20 = clean_series(df['SMA20']);
    sma60 = clean_series(df['SMA60'])
    lsLine = clean_series(df['LongShortLine'])  # 多空線 (MA25)

    rsiData = clean_series(df['RSI']);
    kVal = clean_series(df['K']);
    dVal = clean_series(df['D'])
    dif = clean_series(df['DIF']);
    dea = clean_series(df['DEA'])
    macdHist = [{"value": round(v, 2), "itemStyle": {"color": '#ef232a' if v >= 0 else '#14b143'}} for v in
                df['MACD_HIST']]

    chg = clean_series(df['Change']);
    pct = clean_series(df['PctChange']);
    trendData = [round(float(x), 2) for x in trend_line_values]
    full_title = f"{s_name} ({stock_id})"

    html = f"""
    <div id="main" style="width: 100%; height: 1100px; background: black;" tabindex="0"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        var chartDom = document.getElementById('main');
        var chart = echarts.init(chartDom, 'dark');
        var dates = {json.dumps(dates)}; var kData = {json.dumps(k_vals)}; var volumes = {json.dumps(volumes)};
        var sma5 = {json.dumps(sma5)}; var sma10 = {json.dumps(sma10)}; var sma20 = {json.dumps(sma20)}; var sma60 = {json.dumps(sma60)};
        var lsLine = {json.dumps(lsLine)};
        var rsi = {json.dumps(rsiData)}; var kv = {json.dumps(kVal)}; var dv = {json.dumps(dVal)};
        var dif = {json.dumps(dif)}; var dea = {json.dumps(dea)}; var mh = {json.dumps(macdHist)};
        var chg = {json.dumps(chg)}; var pct = {json.dumps(pct)}; var trend = {json.dumps(trendData)};

        var option = {{
            backgroundColor: '#000',
            axisPointer: {{ link: [{{ xAxisIndex: 'all' }}], lineStyle: {{ color: 'rgba(255, 255, 255, 0.7)', width: 1.5, type: 'solid' }} }},
            tooltip: {{
                trigger: 'axis', axisPointer: {{ type: 'cross' }},
                backgroundColor: 'rgba(0, 0, 0, 0.9)', borderColor: '#FF0000', borderWidth: 1, confine: true,
                position: function (p, params, dom, rect, size) {{
                    var x = p[0] + 20; if (x + size.contentSize[0] > size.viewSize[0]) x = p[0] - size.contentSize[0] - 20;
                    return [x, p[1] - 20];
                }},
                formatter: function (params) {{
                    var i = params[0].dataIndex; var k = kData[i]; var c = chg[i] >= 0 ? '#ef232a' : '#14b143'; var s = chg[i] >= 0 ? '+' : '';
                    return '<div style="line-height:1.6;font-size:12px;font-family:monospace;">' +
                           '<span style="color:#FFF">日期：' + dates[i] + '</span><br/>' +
                           '<span style="color:#FFF">開：' + k[0] + ' / 收：' + k[1] + '</span><br/>' +
                           '<span style="color:#FFF">高：' + k[3] + ' / 低：' + k[2] + '</span><br/>' +
                           '漲跌：<span style="color:'+c+'">' + s + chg[i] + ' (' + s + pct[i] + '%)</span><br/>' +
                           '<hr style="border:0.1px solid #555;margin:4px 0;">' +
                           '<span style="color:#FFF">MA5：' + (sma5[i]||'--') + '</span> <span style="color:#FFFF00">MA10：' + (sma10[i]||'--') + '</span><br/>' +
                           '<span style="color:#FF00FF">MA20：' + (sma20[i]||'--') + '</span> <span style="color:#00FFFF">MA60：' + (sma60[i]||'--') + '</span><br/>' +
                           '<span style="color:#87CEFA">多空線：' + (lsLine[i]||'--') + '</span><br/>' +
                           '<span style="color:#FF00FF">AI趨勢：' + trend[i] + '</span><br/>' +
                           '<hr style="border:0.1px solid #555;margin:4px 0;">' +
                           '<span style="color:#FFFF00">RSI(14)：' + (rsi[i]||'--') + '</span><br/>' +
                           '<span style="color:#FFF">K值：' + (kv[i]||'--') + '</span> <span style="color:#FFFF00">D值：' + (dv[i]||'--') + '</span><br/>' +
                           '<span style="color:#00BFFF">DIF：' + (dif[i]||'--') + '</span> <span style="color:#FFF">MACD：' + (dea[i]||'--') + '</span>' +
                           '</div>';
                }}
            }},
            grid: [
                {{ left: '60', right: '40', top: '3%', height: '28%' }},  // K線
                {{ left: '60', right: '40', top: '40%', height: '10%' }}, // 量
                {{ left: '60', right: '40', top: '54%', height: '10%' }}, // RSI
                {{ left: '60', right: '40', top: '68%', height: '10%' }}, // KD
                {{ left: '60', right: '40', top: '82%', height: '10%' }}  // MACD
            ],
            xAxis: [
                {{ type: 'category', data: dates, axisLabel: {{show: false}}, axisPointer: {{show: true}} }},
                {{ type: 'category', gridIndex: 1, data: dates, axisLabel: {{show: false}}, axisPointer: {{show: true}} }},
                {{ type: 'category', gridIndex: 2, data: dates, axisLabel: {{show: false}}, axisPointer: {{show: true}} }},
                {{ type: 'category', gridIndex: 3, data: dates, axisLabel: {{show: false}}, axisPointer: {{show: true}} }},
                {{ type: 'category', gridIndex: 4, data: dates, axisLabel: {{show: true, color: '#999'}}, axisPointer: {{show: true}} }}
            ],
            yAxis: [
                {{ scale: true, splitLine: {{lineStyle: {{color: '#222'}}}} }},
                {{ gridIndex: 1, axisLabel: {{show: false}}, splitLine: {{show: false}} }},
                {{ gridIndex: 2, min: 0, max: 100, interval: 10, axisLabel: {{show: true, color: '#FFF', fontSize: 10, formatter: v => [30, 50, 70].includes(v) ? v : ''}}, splitLine: {{show: false}} }},
                {{ gridIndex: 3, min: 0, max: 100, interval: 10, axisLabel: {{show: true, color: '#FFF', fontSize: 10, formatter: v => [20, 50, 80].includes(v) ? v : ''}}, splitLine: {{show: false}} }},
                {{ gridIndex: 4, scale: true, splitLine: {{show: false}}, axisLabel: {{color: '#FFF', fontSize: 10}} }}
            ],
            series: [
                {{ name: '日K', type: 'candlestick', data: kData, itemStyle: {{color: '#ef232a', color0: '#14b143', borderColor: '#ef232a', borderColor0: '#14b143'}} }},
                {{ name: 'MA5', type: 'line', data: sma5, lineStyle: {{color: '#FFF', width: 1.5}}, showSymbol: false }},
                {{ name: 'MA10', type: 'line', data: sma10, lineStyle: {{color: '#FFFF00', width: 1.5}}, showSymbol: false }},
                {{ name: 'MA20', type: 'line', data: sma20, lineStyle: {{color: '#FF00FF', width: 1.5}}, showSymbol: false }},
                {{ name: 'MA60', type: 'line', data: sma60, lineStyle: {{color: '#00FFFF', width: 1.5}}, showSymbol: false }},
                {{ name: '多空線', type: 'line', data: lsLine, lineStyle: {{color: '#87CEFA', width: 2, type: 'dotted'}}, showSymbol: false }},
                {{ name: 'AI趨勢', type: 'line', data: trend, lineStyle: {{color: '#FF00FF', width: 2, type: 'dashed'}}, showSymbol: false }},
                {{ name: 'Vol', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volumes }},
                {{ name: 'RSI', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: rsi, lineStyle: {{color: '#FFFF00', width: 1.5}}, showSymbol: false,
                   markLine: {{ symbol: 'none', label: {{show: false}}, data: [{{yAxis: 30}}, {{yAxis: 50}}, {{yAxis: 70}}], lineStyle: {{type:'dashed', color:'#555'}} }} }},
                {{ name: 'K', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kv, lineStyle: {{color: '#FFF', width: 1.5}}, showSymbol: false,
                   markLine: {{ symbol: 'none', label: {{show: false}}, data: [{{yAxis: 20}}, {{yAxis: 50}}, {{yAxis: 80}}], lineStyle: {{type:'dashed', color:'#555'}} }} }},
                {{ name: 'D', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: dv, lineStyle: {{color: '#FFFF00', width: 1.5}}, showSymbol: false }},
                {{ name: 'MACD_H', type: 'bar', xAxisIndex: 4, yAxisIndex: 4, data: mh }},
                {{ name: 'DIF', type: 'line', xAxisIndex: 4, yAxisIndex: 4, data: dif, lineStyle: {{color: '#00BFFF', width: 1.5}}, showSymbol: false }}, 
                {{ name: 'MACD', type: 'line', xAxisIndex: 4, yAxisIndex: 4, data: dea, lineStyle: {{color: '#FFFFFF', width: 1.5}}, showSymbol: false }}
            ],
            title: [
                {{ text: {json.dumps(full_title)}, left: '60', top: '0%', textStyle: {{color: '#00FF00', fontSize: 24}} }},
                {{ text: '成交量', left: '60', top: '38%', textStyle: {{fontSize: 12, color: '#FFFF00'}} }},
                {{ id: 'rsi_t', text: 'RSI', left: '60', top: '52%', textStyle: {{fontSize: 12, color: '#FFFF00'}} }},
                {{ id: 'kd_t', text: 'KD', left: '60', top: '66%', textStyle: {{fontSize: 12, color: '#FFF'}} }},
                {{ id: 'macd_t', text: 'MACD', left: '60', top: '80%', textStyle: {{fontSize: 12, rich: {{b:{{color:'#00BFFF'}}, w:{{color:'#FFF'}}}} }} }}
            ]
        }};
        chart.setOption(option);
        function update(idx) {{
            var rVal = rsi[idx]||'--'; var kVal = kv[idx]||'--'; var dVal = dv[idx]||'--';
            var difVal = dif[idx]||'--'; var deaVal = dea[idx]||'--';
            chart.setOption({{ title: [{{}}, {{}}, {{id:'rsi_t', text:'RSI(14): '+rVal}}, {{id:'kd_t', text:'K: '+kVal+' D: '+dVal}}, {{id:'macd_t', text:'{{b|DIF: '+difVal+'}}  {{w|MACD: '+deaVal+'}}'}}] }});
        }}
        chart.on('showTip', (p) => {{ if(p.dataIndex !== undefined) update(p.dataIndex); }});
        var checkResize = setInterval(function() {{ if (chartDom.clientWidth > 100) {{ chart.resize(); chart.dispatchAction({{type:'showTip', seriesIndex:0, dataIndex:dates.length-1}}); clearInterval(checkResize); }} }}, 200);
        window.addEventListener('resize', function() {{ chart.resize(); }});
    </script>
    """
    return html
