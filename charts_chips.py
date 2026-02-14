import json
import numpy as np


def generate_chips_chart(s_name, stock_id, dates, foreign, trust, dealer):
    """第三頁：法人籌碼圖 (三層結構)"""
    f_vals = [{"value": int(x), "itemStyle": {"color": '#ef232a' if x >= 0 else '#14b143'}} for x in foreign]
    t_vals = [{"value": int(x), "itemStyle": {"color": '#FF00FF' if x >= 0 else '#800080'}} for x in trust]
    d_vals = [{"value": int(x), "itemStyle": {"color": '#00BFFF' if x >= 0 else '#1E90FF'}} for x in dealer]

    template = """
    <div id="chips_main" style="width:100%; height:750px; background:black;"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        var chart = echarts.init(document.getElementById('chips_main'), 'dark');
        var dates = DATE_D; var f_d = F_D; var t_d = T_D; var d_d = D_D;
        var option = {
            backgroundColor: '#000',
            title: { text: TITLE_D, left: 'center', textStyle:{color:'#0F0'} },
            axisPointer: { link: [{ xAxisIndex: 'all' }], lineStyle: { color: 'rgba(255, 255, 255, 0.7)', width: 1.5, type: 'solid' } },
            tooltip: { 
                trigger: 'axis', axisPointer: { type: 'cross' },
                backgroundColor: 'rgba(0, 0, 0, 0.9)', borderColor: '#FF0000', borderWidth: 1, confine: true,
                formatter: function (pa) {
                    var i = pa[0].dataIndex;
                    return '<div style="line-height:1.6;font-size:12px;font-family:monospace;">' +
                           '<span style="color:#FFF">日期：' + dates[i] + '</span><br/>' +
                           '<hr style="border:0.1px solid #555;">' +
                           '<span style="color:#ef232a">外資買賣：' + f_d[i].value.toLocaleString() + ' 張</span><br/>' +
                           '<span style="color:#FF00FF">投信買賣：' + t_d[i].value.toLocaleString() + ' 張</span><br/>' +
                           '<span style="color:#00BFFF">自營買賣：' + d_d[i].value.toLocaleString() + ' 張</span>' +
                           '</div>';
                }
            },
            grid: [{top:'12%',height:'22%'}, {top:'40%',height:'22%'}, {top:'68%',height:'22%'}],
            xAxis: [{data:dates,axisLabel:{show:false},axisPointer:{show:true}},{gridIndex:1,data:dates,axisLabel:{show:false},axisPointer:{show:true}},{gridIndex:2,data:dates,axisLabel:{show:true,color:'#999'},axisPointer:{show:true}}],
            yAxis: [{name:'外資(張)',scale:true,splitLine:{show:false}},{gridIndex:1,name:'投信(張)',scale:true,splitLine:{show:false}},{gridIndex:2,name:'自營(張)',scale:true,splitLine:{show:false}}],
            series: [{name:'外資',type:'bar',data:f_d},{name:'投信',type:'bar',xAxisIndex:1,yAxisIndex:1,data:t_d},{name:'自營商',type:'bar',xAxisIndex:2,yAxisIndex:2,data:d_d}]
        };
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    </script>
    """
    return template.replace("DATE_D", json.dumps(dates)).replace("F_D", json.dumps(f_vals)).replace("T_D", json.dumps(
        t_vals)).replace("D_D", json.dumps(d_vals)).replace("TITLE_D",
                                                            json.dumps(f"{s_name} ({stock_id}) 法人籌碼動向"))
