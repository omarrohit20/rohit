import pathlib
import sbase as sb
from config import *

if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p7")
    sb.option.add_argument('--headless=new')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    regression_ta_data_buy()
    print('Started')
    sb.nw = datetime.now()

    while (sb.nw <= time_10_30):
        if (sb.nw >= time_09_15 and sb.nw <= time_09_25):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > [=-1] 5 minute high and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.5 and ( ( ( [=1] 5 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.75 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_00, time_09_30)

        if(sb.nw>= time_09_20 and sb.nw <= time_09_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.7 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 2 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 ) ) and ( {cash} ( [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > [=-1] 5 minute high and [=1] 5 minute high > [=1] 5 minute vwap and [=1] 5 minute high > [=1] 5 minute ema ( [0] 5 minute close , 20 ) and [=1] 5 minute high > [=-1] 15 minute low and [=1] 5 minute close > [=-1] 15 minute close ) ) and ( 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" ) < 1.5 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'morning-volume-breakout-buy(LT2)', time_09_00, time_09_30, True)

        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            #( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open > -0.1 and ( ( [=1] 5 minute high - [=1] 5 minute close ) * 100 ) / [=1] 5 minute close < 1 and [=1] 10 minute close > [=1] 5 minute open and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-3', 'breakout-morning-volume', time_09_00, time_09_30, 'breakout-morning-volume-buy')

        if (sb.nw >= time_09_25 and sb.nw <= time_09_45):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( [=1] 5 minute high - [=1] 5 minute close ) * 100 ) / [=1] 5 minute close < 1 and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close ) ) and ( {cash} ( [=1] 5 minute close > [=-1] 5 minute high and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( [=-1] 1 hour high - [=-3] 1 hour low ) * 100 ) / [=-3] 1 hour low < 2 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'breakout2-morning-volume', time_09_25, time_09_45, 'breakout2-morning-volume-buy')

        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close > [=1] 5 minute open and [=2] 5 minute close > [=2] 5 minute open and ( ( ( [=2] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-buy*2')

        if(sb.nw>= time_09_30 and sb.nw <= time_11_30):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.75 and [=1] 30 minute low < 1 day ago close and [=1] 30 minute low = [=1] 20 minute low and [-1] 5 minute vwap > [-3] 5 minute vwap and ( ( [-1] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > 0 and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) ) ) and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute open < [=1] 5 minute open and [=2] 5 minute close < [=1] 5 minute open and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) < 0 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-0', 'LastDayLT-1:checkChartBuy-morningDown', time_09_15, time_11_30)

        if(sb.nw>= time_09_30 and sb.nw <= time_11_30):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.75 and [=1] 30 minute low < 1 day ago close and [=1] 30 minute low = [=1] 20 minute low and [-1] 5 minute vwap > [-3] 5 minute vwap and ( ( [-1] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > 0 and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 18  ) ) ) and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute open < [=1] 5 minute open and [=2] 5 minute close < [=1] 5 minute open and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) > 0 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 2 days ago open ) < 6 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'LastDayGT1:checkChartBuy-morningDown((LastDayPostLunchDownSell))', time_09_15, time_11_30)


        #if(sb.nw>= time_11_30 and sb.nw <= time_13_30):
            #process_url_volBreakout('https://chartink.com/screener/buy-morning-down-3', 'buy-morning-down-breakout-VWAP-3-11:30', time_11_30, time_13_30)



        time.sleep(10)
        sb.nw = datetime.now()

    sb.driver.quit()
    