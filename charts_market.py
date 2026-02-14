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
            backgroundColor:'#000', grid:{{left:'50', right:'20'}},
            tooltip:{{trigger:'axis'}},
            xAxis:{{data:{json.dumps(dates)}}},
            yAxis:{{scale:true, splitLine:{{lineStyle:{{color:'#222'}}}}}},
            series:[{{name:'加權指數', type:'line', data:{json.dumps(values)}, lineStyle:{{color:'#FFFF00', width:3}}, smooth:true, showSymbol:false}}]
        }});
        window.addEventListener('resize', function() {{ chart.resize(); }});
    </script>
    """
    return html
