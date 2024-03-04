import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p8")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    regression_ta_data_sell()
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_11_00):
        if(sb.nw>= time_09_15 and sb.nw <= time_09_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 10 minute close < [=-1] 5 minute low and abs ( ( ( [=1] 10 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( [=1] 10 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [=1] 10 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.75 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" > -1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_00, time_09_30)

        if (sb.nw >= time_09_50 and sb.nw <= time_11_00):
            # ( {46553} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.75 and [-1] 5 minute low < [=2] 5 minute low and [-1] 5 minute close < [=2] 5 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-checknews-01', 'sell-morning-volume-breakout(Check-News)-01', time_09_50, time_11_00)

        if(sb.nw>= time_09_30 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( [=1] 2 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 2 minute volume > greatest(  2 days ago volume / 24  ) and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1.5 and ( ( ( [=1] 1 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and [0] 5 minute high > [=1] 5 minute open ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-3', 'SSSsell-downtrend-breakout-morning-volume', time_09_30, time_10_30, 'breakout-morning-volume-sell')

        #if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute close < [=2] 5 minute open and ( ( ( [=2] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1 ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-sell*2')

        #if(sb.nw>= time_09_45 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 30 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 2.5 and [=1] 30 minute high > 1 day ago close and [=1] 30 minute high = [=1] 20 minute high and [-1] 5 minute vwap < [-3] 5 minute vwap and [-1] 5 minute low < [=3] 1 minute low and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 18  ) ) ) and [=1] 5 minute close > [=1] 5 minute open and [=2] 5 minute close > [=1] 5 minute open and [=2] 5 minute open > [=1] 5 minute open and [-1] 5 minute close > [=-1] 30 minute low and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0 and ( ( ( [=1] 30 minute high - [-1] 5 minute low ) * 100 ) / 1 day ago low ) > 1.5 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 2 ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', '9_30:checkChartSell-morningup(LastDaybeforeLT0)', time_09_30, time_09_45)
            #process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', '10_00:checkChartSell-morningup(LastDaybeforeLT0)', time_10_00, time_11_00)

        if (sb.nw >= time_09_45 and sb.nw <= time_11_00):
            # ( {46553} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -2 and [=1] 30 minute low < 1 day ago close and [=1] 30 minute low = [=1] 20 minute low and [-1] 5 minute vwap > [-3] 5 minute vwap and ( ( [-1] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > 0 and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute open < [=1] 5 minute open and [=2] 5 minute close < [=1] 5 minute open and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1.5 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) < 4 and ( {cash} ( ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.75 and [-1] 5 minute high > [=2] 5 minute high and [-1] 5 minute low > [=2] 5 minute low and [-1] 5 minute close > [=2] 5 minute low and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute close ) ) ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'checkChartSell-morningDown', time_09_45, time_11_00)


        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
