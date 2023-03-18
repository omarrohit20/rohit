import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p4")
    sb.option.add_argument('--headless=new')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_10_30):
        #if (sb.nw >= time_09_25 and sb.nw <= time_09_45):
            # ( {46553} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < 1 day ago close and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.5 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute low - 2 days ago open ) * 100 ) / 2 days ago open ) > -4 and [0] 5 minute low < [=3] 5 minute close and [0] 5 minute low < [=3] 5 minute open and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > -1.75 and 1 day ago close < 2 days ago open and 1 day ago close < 3 days ago close ) ) ) )
            #process_url('https://chartink.com/screener/sell-morning-volume-breakout-checknews-01', 'sell-morning-volume-breakout(Check-News)-01', time_09_25, time_09_45, True)

        if (sb.nw >= time_09_00 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 18  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close > 1 day ago close and ( ( ( [=2] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( {cash} ( [=2] 5 minute high < [=1] 5 minute high and [-1] 5 minute high < [=1] 5 minute open and [-1] 5 minute high < [=1] 5 minute close and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > 2 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 5 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" < 0.5 ) ) ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'sell-morning-up-volume-breakout(wait-till-9:45/10)', time_09_00, time_10_30)

        if(sb.nw>= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low <= [-3] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and [-1] 5 minute low < [=2] 15 minute low and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < -0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -4 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and [-1] 5 minute low > 1 day ago low and [-1] 5 minute low > 2 days ago low and ( ( 3 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -1 and ( ( 4 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -2.5 ) ) ) ) 
            process_url('https://chartink.com/screener/03-sellbreakdownintraday-01', 'sell-(==Reversal-lastDayLowNotReached==)03-BreakdownIntraday', time_09_40, time_10_15, True)


        # if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_11_30, True)
        
        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-sellBreakdownIntraday-10:15-to-11:15', time_10_15, time_11_15)
                        
            
        #time.sleep(30)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    