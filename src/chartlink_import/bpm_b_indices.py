import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p1")
    sb.option.add_argument('--headless=new')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_00):
        #if (sb.nw >= time_09_45 and sb.nw <= time_12_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.7 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [-1] 5 minute close - [-6] 5 minute close ) * 100 ) / [-6] 5 minute close ) < 0 and latest "close - 1 candle ago close / 1 candle ago close * 100" < -0.7 ) ) ) )
            #process_url('https://chartink.com/screener/supertrend-morning-buy', 'supertrend-morning-buy', time_09_45, time_12_00)


        if (sb.nw >= time_09_30 and sb.nw <= time_10_00):
            # ( {46553} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1.75 and [-1] 5 minute high > [=2] 5 minute high and [-1] 5 minute close > [=2] 5 minute high ) ) ) )
            process_url('https://chartink.com/screener/buy-morning-volume-breakout-checknews-01', 'buy-morning-volume-breakout(Check-News)-01', time_09_25, time_10_00)

        if (sb.nw >= time_09_30 and sb.nw <= time_14_00):
            # ( {33489} ( ( {cash} ( [0] 5 minute volume > greatest(  1 day ago volume / 10  ) and [0] 5 minute volume > greatest(  2 days ago volume / 10  ) and [=1] 5 minute close > [=1] 5 minute open and [-1] 5 minute low < [-1] 30 minute high and abs ( [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < 0.5 and abs ( [-2] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < 0.5 and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > abs ( 0.2 ) and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > abs ( [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" ) and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > abs ( [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) and [0] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > abs ( [-2] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) and ( ( ( [-1] 5 minute low - [=1] 5 minute high ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / 1 day ago close ) < 1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'BBreakout-Buy-SellDayTrend-volume-5minutes', time_09_40, time_14_00)

        if(sb.nw >= time_09_30 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > 1 and abs ( [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" / 4 and abs ( [-1] 10 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" / 4 and abs ( [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" / 4 and abs ( [-1] 20 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" / 4 and abs ( [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" ) < [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" / 4 and [-1] 5 minute high < [=1] 15 minute high and [-1] 30 minute low > [=1] 5 minute high ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-dayconsolidation-breakout-04', 'BBreakout-Buy-SellDayTrendbuy-dayconsolidation', time_10_00, time_11_30)


        #if (sb.nw >= time_09_40 and sb.nw <= time_11_30):
            # ( {cash} ( ( {cash} ( abs ( [-1] 5 minute close - [-1] 5 minute sma ( [-1] 5 minute close , 200 ) * 100 ) / [-1] 5 minute close > 3.5 and abs ( [=-1] 5 minute close - [=-1] 5 minute sma ( [=-1] 5 minute close , 200 ) * 100 ) / [-1] 5 minute close < 2 and [=-5] 2 hour high >= 2 days ago "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" and abs ( [-1] 5 minute close - [0] 5 minute open * 100 ) / [-1] 5 minute close < 2 and abs ( [-1] 5 minute close - [-2] 5 minute open * 100 ) / [-1] 5 minute close < 2 and abs ( [-1] 5 minute close - [-1] 5 minute open * 100 ) / [-1] 5 minute close < 1 and [-1] 5 minute volume > [=1] 5 minute volume and [-1] 5 minute volume > [=2] 5 minute volume and [-1] 5 minute volume > [=3] 5 minute volume and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 2 and [0] 5 minute close > 50 and [0] 5 minute close < 3000 and market cap > 1000 ) ) ) )
            #process_url('https://chartink.com/screener/buy-ema-up0', 'buy-sma200-up', time_09_40, time_11_30)




        #if (sb.nw >= time_09_00 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < 1 day ago close and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.5 and ( {cash} ( [=2] 5 minute low < [=1] 5 minute low and [-1] 5 minute low < [=1] 5 minute open and [-1] 5 minute low < [=1] 5 minute close and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < -2 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > -5 ) ) ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/buy-check-morning-down-breakup-01', 'buy-morning-down-volume-breakout(wait-till-9:45/10)', time_09_00, time_10_30)

        #if(sb.nw >= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute open > 1 day ago low and [=1] 5 minute close > 1 day ago low and [-1] 5 minute high >= [-2] 15 minute high and [-1] 5 minute high >= [-3] 15 minute high and [-1] 5 minute high > [=1] 15 minute high and [-1] 5 minute high > [=2] 15 minute high and ( ( [-1] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > 0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close < 2.5 and ( ( [-1] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high < 1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open < 4 and ( ( 1 day ago high - 1 day ago open ) * 100 ) / 1 day ago high < 4 and ( ( 1 day ago high - 1 day ago low ) * 100 ) / 1 day ago low < 5 and [-1] 5 minute high < 1 day ago high and [-1] 5 minute high < 2 days ago high and ( ( 3 days ago high - [-1] 5 minute high ) * 100 ) / [-1] 5 minute high > 1 and ( ( 4 days ago high - [-1] 5 minute high ) * 100 ) / [-1] 5 minute high > 2.5 ) ) ) ) 
            #process_url('https://chartink.com/screener/03-buybreakupintraday-01', 'buy-(==Reversal-lastDayHighNotReached==)03-BreakupIntraday', time_09_40, time_10_15, True)
        
        #if(sb.nw >= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [-1] 5 minute high > [=1] 15 minute high and [-1] 5 minute close > ( 1 day ago high - 1 day ago low ) / 2 + 1 day ago low and [-1] 5 minute close < 2 days ago high and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open < 0 and ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago open < -1 and 1 day ago high = [=-7] 1 hour high and [=-1] 1 hour high < [=-3] 1 hour high and ( {cash} ( [=2] 5 minute volume < greatest(  1 day ago volume / 18  ) and [=2] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 5 minute close > [=1] 5 minute open ) ) ) ) ) ) 
            #process_url('https://chartink.com/screener/03-buybreakupintraday-02', 'buy-(==Reversal-Crossedlast1DayMid==)03-buyBreakupIntraday', time_09_40, time_10_15, True)


        # if(sb.nw >= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-04', 'buy-dayconsolidation-breakout-04(11:45-to-1:00)', time_10_00, time_11_30, True)
                        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/buy-breakup-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-buyBreakupIntraday-10:15-to-11:15', time_10_15, time_11_15)
        
        #time.sleep(30)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    
