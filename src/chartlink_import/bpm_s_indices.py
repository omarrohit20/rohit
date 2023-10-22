import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p4")
    sb.option.add_argument('--headless=new')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_00):
        #if (sb.nw >= time_09_45 and sb.nw <= time_12_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.7 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [-1] 5 minute close - [-6] 5 minute close ) * 100 ) / [-6] 5 minute close ) < 0 and latest "close - 1 candle ago close / 1 candle ago close * 100" < -0.7 ) ) ) )
            #process_url('https://chartink.com/screener/supertrend-morning-sell', 'supertrend-morning-sell', time_09_45, time_12_00)


        if (sb.nw >= time_09_30 and sb.nw <= time_10_00):
            # ( {46553} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.75 and [-1] 5 minute low < [=2] 5 minute low and [-1] 5 minute close < [=2] 5 minute low ) ) ) )
            process_url('https://chartink.com/screener/sell-morning-volume-breakout-checknews-01', 'sell-morning-volume-breakout(Check-News)-01', time_09_25, time_10_00)

        if (sb.nw >= time_09_30 and sb.nw <= time_14_00):
            # ( {33489} ( ( {cash} ( [0] 5 minute volume > greatest(  1 day ago volume / 10  ) and [0] 5 minute volume > greatest(  2 days ago volume / 10  ) and [=1] 5 minute close < [=1] 5 minute open and [-1] 5 minute high > [-1] 30 minute low and abs ( [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) > -0.5 and abs ( [-2] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) > -0.5 and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" < ( -0.2 ) and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" < ( [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" ) and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" < ( [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" < ( [-2] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) and ( ( ( [-1] 5 minute high - [=1] 5 minute low ) * 100 ) / 1 day ago close ) > -0.5 and ( ( ( [-1] 5 minute high - [=1] 5 minute high ) * 100 ) / 1 day ago close ) > -1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-2', 'BBreakout-Sell-BuyDayTrend-volume-5minutes', time_09_40, time_14_00)

        #if (sb.nw >= time_09_00 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 18  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close > 1 day ago close and ( ( ( [=2] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( {cash} ( [=2] 5 minute high < [=1] 5 minute high and [-1] 5 minute high < [=1] 5 minute open and [-1] 5 minute high < [=1] 5 minute close and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > 2 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 5 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" < 0.5 ) ) ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'sell-morning-up-volume-breakout(wait-till-9:45/10)', time_09_00, time_10_30)

        #if(sb.nw>= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low <= [-3] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and [-1] 5 minute low < [=2] 15 minute low and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < -0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -4 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and [-1] 5 minute low > 1 day ago low and [-1] 5 minute low > 2 days ago low and ( ( 3 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -1 and ( ( 4 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -2.5 ) ) ) ) 
            #process_url('https://chartink.com/screener/03-sellbreakdownintraday-01', 'sell-(==Reversal-lastDayLowNotReached==)03-BreakdownIntraday', time_09_40, time_10_15, True)
            #https://chartink.com/screener/03-sellbreakdownintraday-02

        # if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_11_30, True)
        
        

            
        #time.sleep(30)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    