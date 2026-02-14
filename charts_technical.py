import json
import numpy as np


def clean_series(series):
    return [None if np.isnan(x) else round(float(x), 2) for x in series]


def generate_stock_chart(s_name, stock_id, df, trend_line_values):
    dates = df.index.strftime('%Y/%m/%d').tolist()
    k_vals = [[round(r.Open, 2), round(r.Close, 2), round(r.Low, 2), round(r.High, 2)] for r in df.itertuples()]
    v_data = [{"value": int(r.Volume), "itemStyle": {"color": '#ef232a' if r.Close >= r.Open else '#14b143'}} for r in
              df.itertuples()]

    s5 = clean_series(df['SMA5']);
    s10 = clean_series(df['SMA10'])
    s20 = clean_series(df['SMA20']);
    s60 = clean_series(df['SMA60'])
    ls_l = clean_series(df['LongShortLine']);
    rs_d = clean_series(df['RSI'])
    kv_d = clean_series(df['K']);
    dv_d = clean_series(df['D'])
    dif_v = clean_series(df['DIF']);
    dea_v = clean_series(df['DEA'])
    mh_list = [{"value": round(x, 2), "itemStyle": {"color": '#ef232a' if x >= 0 else '#14b143'}} for x in
               df['MACD_HIST']]

    tr_d = [round(float(x), 2) for x in trend_line_values]
    chg = clean_series(df['Change']);
    pct = clean_series(df['PctChange'])
    title_str = f"{s_name} ({stock_id})"

    # 核心：使用模板替換法，保證 JavaScript 大括號不被 Python 誤解析
    template = """
    <div id="main" style="width:100%; height:1100px; background:black;" tabindex="0"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        var cd = document.getElementById('main');
        var c = echarts.init(cd, 'dark');
        var dt = DATE_D; var kD = K_D; var s5 = S5_D; var s10 = S10_D; var s20 = S20_D; var s60 = S60_D;
        var ls = LS_D; var tr = TR_D; var rs = RS_D; var kv = KV_D; var dv = DV_D;
        var df = DF_D; var de = DE_D; var mh = MH_D; var cg = CHG_D; var pc = PCT_D;

        var option = {
            backgroundColor: '#000',
            axisPointer: { link: [{ xAxisIndex: 'all' }], lineStyle: { color: 'rgba(255, 255, 255, 0.7)', width: 1.5, type: 'solid' } },
            tooltip: {
                trigger: 'axis', axisPointer: { type: 'cross' },
                backgroundColor: 'rgba(0, 0, 0, 0.9)', borderColor: '#FF0000', borderWidth: 1, confine: true,
                position: function (p, params, dom, rect, size) {
                    var x = p[0] + 20; if (x + size.contentSize[0] > size.viewSize[0]) x = p[0] - size.contentSize[0] - 20;
                    return [x, p[1] - 20];
                },
                formatter: function (pa) {
                    var i = pa[0].dataIndex; var co = cg[i] >= 0 ? '#ef232a' : '#14b143'; var sn = cg[i] >= 0 ? '+' : '';
                    return '<div style="line-height:1.6;font-size:12px;font-family:monospace;">' +
                           '<span style="color:#FFF">日期：' + dt[i] + '</span><br/>' +
                           '<span style="color:#FFF">開:' + kD[i][0] + ' 收:' + kD[i][1] + ' 高:' + kD[i][3] + ' 低:' + kD[i][2] + '</span><br/>' +
                           '漲跌：<span style="color:'+co+'">' + sn + cg[i] + ' (' + sn + pc[i] + '%)</span><br/>' +
                           '<hr style="border:0.1px solid #555;">' +
                           '<span style="color:#FFF">MA5:' + s5[i] + '</span> <span style="color:#FFFF00">MA10:' + s10[i] + '</span><br/>' +
                           '<span style="color:#FF00FF">MA20:' + s20[i] + '</span> <span style="color:#00FFFF">MA60:' + s60[i] + '</span><br/>' +
                           '<span style="color:#87CEFA">多空線:' + ls[i] + '</span><br/>' +
                           '<span style="color:#FF00FF">AI趨勢:' + tr[i] + '</span><br/>' +
                           '<hr style="border:0.1px solid #555;">' +
                           '<span style="color:#FFFF00">RSI:' + rs[i] + '</span><br/>' +
                           '<span style="color:#FFF">K值:' + kv[i] + '</span> <span style="color:#FFFF00">D值:' + dv[i] + '</span><br/>' +
                           '<span style="color:#00BFFF">DIF:' + df[i] + '</span> <span style="color:#FFF">MACD:' + de[i] + '</span></div>';
                }
            },
            grid: [{top:'5%',height:'30%'}, {top:'40%',height:'10%'}, {top:'54%',height:'10%'}, {top:'68%',height:'10%'}, {top:'82%',height:'10%'}],
            xAxis: [{data:dt,axisLabel:{show:false},axisPointer:{show:true}},{gridIndex:1,data:dt,axisLabel:{show:false}},{gridIndex:2,data:dt,axisLabel:{show:false}},{gridIndex:3,data:dt,axisLabel:{show:false}},{gridIndex:4,data:dt,axisLabel:{show:true,color:'#999'}}],
            yAxis: [
                {scale:true, splitLine:{lineStyle:{color:'#222'}}},
                {gridIndex:1,axisLabel:{show:false},splitLine:{show:false}},
                {gridIndex:2,min:0,max:100,interval:10,axisLabel:{show:true,color:'#FFF',fontSize:10,formatter:function(v){return [20,50,80].includes(v)?v:'';}},splitLine:{show:false}},
                {gridIndex:3,min:0,max:100,interval:10,axisLabel:{show:true,color:'#FFF',fontSize:10,formatter:function(v){return [20,50,80].includes(v)?v:'';}},splitLine:{show:false}},
                {gridIndex:4,scale:true,splitLine:{show:false}}
            ],
            series: [
                {name:'日K',type:'candlestick',data:kD,itemStyle:{color:'#ef232a',color0:'#14b143',borderColor:'#ef232a',borderColor0:'#14b143'}},
                {name:'MA5',type:'line',data:s5,lineStyle:{color:'#FFF',width:1.5},showSymbol:false},
                {name:'MA10',type:'line',data:s10,lineStyle:{color:'#FF0',width:1.5},showSymbol:false},
                {name:'MA20',type:'line',data:s20,lineStyle:{color:'#F0F',width:1.5},showSymbol:false},
                {name:'MA60',type:'line',data:s60,lineStyle:{color:'#0FF',width:1.5},showSymbol:false},
                {name:'多空線',type:'line',data:ls,lineStyle:{color:'#87CEFA',width:2,type:'dotted'},showSymbol:false},
                {name:'AI趨勢',type:'line',data:tr,lineStyle:{color:'#F0F',width:2,type:'dashed'},showSymbol:false},
                {name:'Vol',type:'bar',xAxisIndex:1,yAxisIndex:1,data:V_DATA},
                {type:'line',xAxisIndex:2,yAxisIndex:2,data:rs,lineStyle:{color:'#FF0',width:1.5},showSymbol:false,markLine:{symbol:'none',label:{show:false},data:[{yAxis:20},{yAxis:50},{yAxis:80}],lineStyle:{type:'dashed',color:'#555'}}},
                {type:'line',xAxisIndex:3,yAxisIndex:3,data:kv,lineStyle:{color:'#FFF',width:1.5},showSymbol:false,markLine:{symbol:'none',label:{show:false},data:[{yAxis:20},{yAxis:50},{yAxis:80}],lineStyle:{type:'dashed',color:'#555'}}},
                {type:'line',xAxisIndex:3,yAxisIndex:3,data:dv,lineStyle:{color:'#FF0',width:1.5},showSymbol:false},
                {type:'bar',xAxisIndex:4,yAxisIndex:4,data:mh},
                {type:'line',xAxisIndex:4,yAxisIndex:4,data:df,lineStyle:{color:'#00BFFF',width:1.5},showSymbol:false},
                {type:'line',xAxisIndex:4,yAxisIndex:4,data:de,lineStyle:{color:'#FFF',width:1.5},showSymbol:false}
            ],
            title: [
                {text:TITLE_D,left:'60',top:'0%',textStyle:{color:'#00FF00',fontSize:24}},
                {text:'成交量',left:'60',top:'38%',textStyle:{fontSize:11,color:'#FF0'}},
                {id:'rsi_t',text:'RSI',left:'60',top:'52%',textStyle:{fontSize:11,color:'#FF0'}},
                {id:'kd_t',text:'KD',left:'60',top:'66%',textStyle:{fontSize:11,rich:{w:{color:'#FFF'},y:{color:'#FF0'}}}},
                {id:'macd_t',text:'MACD',left:'60',top:'80%',textStyle:{fontSize:11,rich:{b:{color:'#00BFFF'},w:{color:'#FFF'}}}} 
            ]
        };
        c.setOption(option);
        function updS(idx) {
            var r = rs[idx]||'--'; var k = kv[idx]||'--'; var d = dv[idx]||'--';
            var dfV = df[idx]||'--'; var deV = de[idx]||'--'; var mhV = mh[idx] ? mh[idx].value : '--';
            c.setOption({ title: [ {}, {}, {id:'rsi_t', text:'RSI(14): '+r}, {id:'kd_t', text:'{w|K: '+k+'}  {y|D: '+d+'}'}, {id:'macd_t', text:'{b|DIF: '+dfV+'} {w|MACD: '+deV+'} OSC: '+mhV}] });
        }
        c.on('showTip', (pa)=> { if(pa.dataIndex!==undefined) updS(pa.dataIndex); });
        var rsz = setInterval(() => { if(cd.clientWidth > 100) { c.resize(); c.dispatchAction({type:'showTip',seriesIndex:0,dataIndex:dt.length-1}); updS(dt.length-1); clearInterval(rsz); } }, 200);
        window.addEventListener('resize', () => c.resize());
    </script>
    """

    return template.replace("DATE_D", json.dumps(dates)) \
        .replace("K_D", json.dumps(k_vals)) \
        .replace("V_DATA", json.dumps(v_data)) \
        .replace("S5_D", json.dumps(s5)) \
        .replace("S10_D", json.dumps(s10)) \
        .replace("S20_D", json.dumps(s20)) \
        .replace("S60_D", json.dumps(s60)) \
        .replace("LS_D", json.dumps(ls_l)) \
        .replace("RS_D", json.dumps(rs_d)) \
        .replace("KV_D", json.dumps(kv_d)) \
        .replace("DV_D", json.dumps(dv_d)) \
        .replace("DF_D", json.dumps(dif_v)) \
        .replace("DE_D", json.dumps(dea_v)) \
        .replace("MH_D", json.dumps(mh_list)) \
        .replace("TITLE_D", json.dumps(title_str)) \
        .replace("CHG_D", json.dumps(chg)) \
        .replace("PCT_D", json.dumps(pct)) \
        .replace("TR_D", json.dumps(tr_d))
