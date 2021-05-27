import pandas as pd
import numpy as np
import plotly.graph_objects as go
pd.options.plotting.backend="plotly"

def p2f(value):
    try:
        return float(value.rstrip('%'))
    except:
        return

class stats:
    average_return = 0
    standard_deviation = 0
    def __init__(self, AS_df, stock):
        self.standard_deviation=AS_df[stock].std()
        self.average_return = AS_df[stock].mean()

def get_dataframe(path):
    cols = {'RJR','Hasbro','S&P 500','3 month T-Bill'}
    converters_dict = {col:p2f for col in cols}
    AS_df = pd.read_csv(r'C:\Users\npk50\Desktop\Alex_Sharpe.csv', sep=",", converters=converters_dict, header=0)
    AS_df.drop(AS_df.iloc[:, 5:17], inplace=True, axis=1)
    AS_df = AS_df[:-3]
    return AS_df

def get_market_premiums(AS_df):
    AS_df['RJR_Premium'] = AS_df['RJR'] - AS_df['3 month T-Bill']
    AS_df['HAS_Premium'] = AS_df['Hasbro'] - AS_df['3 month T-Bill']
    AS_df['S&P500_Premium'] = AS_df['S&P 500'] - AS_df['3 month T-Bill']

if __name__ =="__main__":
    path = r'C:\Users\npk50\Desktop\Alex_Sharpe.csv'
    AS_df = get_dataframe(path)
    get_market_premiums(AS_df)

    config = {'staticPlot': True}

    # Populating stats objects for each stock
    RJR = stats(AS_df,'RJR')
    HAS = stats(AS_df, 'Hasbro')
    SP = stats(AS_df, 'S&P 500')
    RiskFree = stats(AS_df,'3 month T-Bill')

    # Creating dataframe for storing weighted portfolio data
    SP_weights=list(np.arange(150,-0,-0.5))
    Port_df=pd.DataFrame(SP_weights, columns=['S&P500 weight'])

    # Computing average returns for weighted portfolio
    Port_df['ER_S&P500_RJR'] = (Port_df['S&P500 weight'] * SP.average_return+(100-Port_df['S&P500 weight']) * RJR.average_return)/100
    Port_df['ER_S&P500_HAS'] = (Port_df['S&P500 weight'] * SP.average_return + (100 - Port_df['S&P500 weight']) * HAS.average_return)/100

    # Computing standard deviations for weighted portfolio
    correl_SP_RJR = np.corrcoef(AS_df['S&P 500'],AS_df['RJR'])[0,1]
    correl_SP_HAS = np.corrcoef(AS_df['S&P 500'], AS_df['Hasbro'])[0, 1]
    Port_df['SD_S&P500_RJR'] = np.sqrt(np.power(Port_df['S&P500 weight'] * SP.standard_deviation,2) + np.power((100 - Port_df['S&P500 weight']) * RJR.standard_deviation,2) + 2 * Port_df['S&P500 weight'] * SP.standard_deviation * (100 - Port_df['S&P500 weight']) * RJR.standard_deviation * correl_SP_RJR)/100
    Port_df['SD_S&P500_HAS'] = np.sqrt(np.power(Port_df['S&P500 weight'] * SP.standard_deviation, 2) + np.power((100 - Port_df['S&P500 weight']) * HAS.standard_deviation, 2) + 2 * Port_df['S&P500 weight'] * SP.standard_deviation * (100 - Port_df['S&P500 weight']) * HAS.standard_deviation * correl_SP_HAS)/100

    # Computing Sharpe Ratios
    Port_df['Sharpe_S&P500_RJR'] = (Port_df['ER_S&P500_RJR']-RiskFree.average_return) / Port_df['SD_S&P500_RJR']
    Port_df['Sharpe_S&P500_HAS'] = (Port_df['ER_S&P500_HAS'] - RiskFree.average_return) / Port_df['SD_S&P500_HAS']

    # 99% S&P500 and 1% RJR portfolios
    Portf_SP_RJR_ER = Port_df.loc[Port_df['S&P500 weight'] == 99, 'ER_S&P500_RJR'].values[0]
    Portf_SP_RJR_SD = Port_df.loc[Port_df['S&P500 weight'] == 99, 'SD_S&P500_RJR'].values[0]
    Portf_SP_RJR_Sharpe = Port_df.loc[Port_df['S&P500 weight'] == 99, 'Sharpe_S&P500_RJR'].values[0]

    # 99% S&P500 and 1% HAS portfolios
    Portf_SP_HAS_ER = Port_df.loc[Port_df['S&P500 weight'] == 99, 'ER_S&P500_HAS'].values[0]
    Portf_SP_HAS_SD = Port_df.loc[Port_df['S&P500 weight'] == 99, 'SD_S&P500_HAS'].values[0]
    Portf_SP_HAS_Sharpe = Port_df.loc[Port_df['S&P500 weight'] == 99, 'Sharpe_S&P500_HAS'].values[0]

    # Peak Sharpe Ratio for S&P500 + RJR
    SP_RJR_Peak_Sharpe = np.max(Port_df['Sharpe_S&P500_RJR'])
    # Computing Tangent Portfolio mix for S&P500 and RJR
    Tangent_RJR_ER = Port_df.loc[Port_df['Sharpe_S&P500_RJR'] == SP_RJR_Peak_Sharpe,'ER_S&P500_RJR'].values[0]
    Tangent_RJR_SD = Port_df.loc[Port_df['Sharpe_S&P500_RJR'] == SP_RJR_Peak_Sharpe,'SD_S&P500_RJR'].values[0]
    Tangent_RJR_weight = Port_df.loc[Port_df['Sharpe_S&P500_RJR'] == SP_RJR_Peak_Sharpe,'S&P500 weight'].values[0]

    # Peak Sharpe Ratio for S&P500 + HAS
    SP_HAS_Peak_Sharpe = np.max(Port_df['Sharpe_S&P500_HAS'])
    # Computing Tangent Portfolio mix for S&P500 and HAS
    Tangent_HAS_ER = Port_df.loc[Port_df['Sharpe_S&P500_HAS'] == SP_HAS_Peak_Sharpe,'ER_S&P500_HAS'].values[0]
    Tangent_HAS_SD = Port_df.loc[Port_df['Sharpe_S&P500_HAS'] == SP_HAS_Peak_Sharpe,'SD_S&P500_HAS'].values[0]
    Tangent_HAS_weight = Port_df.loc[Port_df['Sharpe_S&P500_HAS'] == SP_HAS_Peak_Sharpe, 'S&P500 weight'].values[0]

    # Generating scatter plot
    trace1 = go.Scatter(x=Port_df['SD_S&P500_RJR'], y=Port_df['ER_S&P500_RJR'],name='S&P500 & RJR',mode='markers')
                        # ,hovertext=list(Port_df['S&P500 weight']))
    trace2 = go.Scatter(x=Port_df['SD_S&P500_HAS'], y=Port_df['ER_S&P500_HAS'],name='S&P500 & HAS',mode='markers')
                        # ,hovertext=list(Port_df['S&P500 weight']))

    trace3 = go.Scatter(x=[0,Tangent_RJR_SD,10],y=[RiskFree.average_return,Tangent_RJR_ER,10*np.max(Port_df['Sharpe_S&P500_RJR'])+RiskFree.average_return],
                        mode='markers+lines',name='CML S&P500 & RJR')
    # ,text=["Risk-Free Investment","Tangent Portfolio"])

    trace4 = go.Scatter(x=[0, Tangent_HAS_SD,10], y=[RiskFree.average_return, Tangent_HAS_ER,10*np.max(Port_df['Sharpe_S&P500_HAS'])+RiskFree.average_return],
                        mode='markers+lines', name='CML S&P500 & HAS')
    # ,text=["","Tangent Portfolio"])

    trace5 = go.Table(
        header=dict(values=['<b>Reference</b>','<b>Name</b>','<b>Expected Revenue [%]</b>','<b>Standard Deviation [%]</b>','<b>Sharpe Ratio</b>']),
        cells=dict(values=[['A','B','C','D','E'],
                           ['Risk-Free Investment',
                            '       Efficient Portfolio<br>' + str(Tangent_RJR_weight) + '% S&P500 +' + str(100-Tangent_RJR_weight) + '% RJR',
                            '       Efficient Portfolio<br>' + str(Tangent_HAS_weight) + '% S&P500 +' + str(100-Tangent_HAS_weight) + '% HAS',
                            '99% S&P500 + 1% RJR','99% S&P500 + 1% HAS'],
                           [np.round(RiskFree.average_return*100,3), np.round(Tangent_RJR_ER,3), np.round(Tangent_HAS_ER,3),
                            np.round(Portf_SP_RJR_ER,3),np.round(Portf_SP_HAS_ER,3)],
                           [0, np.round(Tangent_RJR_SD,3), np.round(Tangent_HAS_SD,3), np.round(Portf_SP_RJR_SD,3), np.round(Portf_SP_HAS_SD,3)],
                           [0, np.round(SP_RJR_Peak_Sharpe,3), np.round(SP_HAS_Peak_Sharpe,3), np.round(Portf_SP_RJR_Sharpe,3), np.round(Portf_SP_HAS_Sharpe,3)]],
                            align=['center','center','center','center','center']),
        domain=dict(x=[0.01, 0.51],
                    y=[0.5, 0.99]),
        columnwidth = [2,5])

    data=[trace1,trace2,trace3,trace4,trace5]

    layout = go.Layout(title={'text': "<b>Portfolio Efficiency Comparison</b>", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, xaxis = dict(title='Volatility (Standard Deviation) %'), yaxis=dict(title='Expected Return %'))
                       # ,hovermode="x")

    fig = go.Figure(data=data,layout=layout)

    # TEXT CALLOUTS

    text_list=['A','B','C','D','E']
    x_list=[0, Tangent_RJR_SD, Tangent_HAS_SD,Portf_SP_RJR_SD,Portf_SP_HAS_SD]
    y_list=[RiskFree.average_return,Tangent_RJR_ER, Tangent_HAS_ER,Portf_SP_RJR_ER,Portf_SP_HAS_ER]
    x_shifts=[0,0,0,0,0]
    x_anchors=['center','center','center','right','right']
    y_anchors=["auto","auto","auto","top","bottom"]

    for aIndex in range(len(text_list)):
        fig.add_annotation(text=text_list[aIndex], xanchor=x_anchors[aIndex], x=x_list[aIndex], y=y_list[aIndex], arrowhead=2, arrowsize=2,
                           font=dict(family="Courier New, monospace", size=16, color="black"), showarrow=True,xshift=x_shifts[aIndex],
                           yanchor=y_anchors[aIndex])

    fig.show()

    # For static image, add
    # config=config)

    # Export dataframe to Excel
    # export_file=r'C:\Users\npk50\Desktop\Alex_Sharpe.xlsx'
    # Port_df.to_excel(export_file)


