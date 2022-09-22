import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p4")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_12_30):
        if (sb.nw >= time_09_25 and sb.nw <= time_09_45):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < 1 day ago close and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and [0] 5 minute low < [=3] 5 minute close and [0] 5 minute low < [=3] 5 minute open ) ) ) )
            process_url('https://chartink.com/screener/sell-morning-volume-breakout-checknews-01', 'sell-morning-volume-breakout(CheckNews)-01', time_09_25, time_09_45, True)

        #if(sb.nw>= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low <= [-3] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and [-1] 5 minute low < [=2] 15 minute low and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < -0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -4 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and [-1] 5 minute low > 1 day ago low and [-1] 5 minute low > 2 days ago low and ( ( 3 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -1 and ( ( 4 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -2.5 ) ) ) ) 
            #process_url('https://chartink.com/screener/03-sellbreakdownintraday-01', 'sell-(==Reversal-lastDayLowNotReached==)03-BreakdownIntraday', time_09_40, time_10_15, True)
            
        # if(sb.nw>= time_09_30 and sb.nw <= time_10_30): 
        #     process_url('https://chartink.com/screener/03-sellbreakdownintraday-02', '(==Reversal-Crossedlast2DayLow==)03-sellBreakdownIntraday', time_09_30, time_10_15, True)
            
        #if(sb.nw >= time_11_00 and sb.nw <= time_12_30):
            #( {33489} ( ( {cash} ( ( {cash} ( [=1] 10 minute close < [=1] 10 minute open and [=1] 5 minute close < [=1] 5 minute open and [-1] 5 minute low > [=1] 1 hour low and [-2] 5 minute low > [=1] 1 hour low and [-1] 15 minute high < [=1] 20 minute low and ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close < -1 and ( ( [=1] 1 hour low - 1 day ago close ) * 100 ) / 1 day ago close > -5 and ( ( [=1] 1 hour low - [=1] 1 hour high ) * 100 ) / 1 day ago close > -4 and ( ( 1 day ago close - 3 days ago close ) * 100 ) / 3 days ago close > -3 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open < -0.75 and ( ( [=1] 2 hour low - [-1] 5 minute close ) * 100 ) / [-1] 5 minute close > -1 and ( ( [=1] 2 hour low - [0] 15 minute high ) * 100 ) / [0] 15 minute high > -1 and ( ( [=1] 2 hour low - [-1] 15 minute high ) * 100 ) / [-1] 15 minute high > -1 and ( ( [=1] 2 hour low - [-2] 15 minute high ) * 100 ) / [-2] 15 minute high > -1 ) ) and ( {cash} ( ( ( [-1] 15 minute vwap - [-6] 15 minute vwap ) * 100 ) / [-6] 15 minute vwap < 0.2 and ( ( [-1] 15 minute vwap - [-9] 15 minute vwap ) * 100 ) / [-9] 15 minute vwap < 0.2 and ( ( [-1] 15 minute vwap - [-12] 15 minute vwap ) * 100 ) / [-12] 15 minute vwap < 0.2 and ( ( [-1] 15 minute vwap - [-6] 15 minute vwap ) * 100 ) / [-6] 15 minute vwap > -0.2 and ( ( [-1] 15 minute vwap - [-9] 15 minute vwap ) * 100 ) / [-9] 15 minute vwap > -0.2 and ( ( [-1] 15 minute vwap - [-12] 15 minute vwap ) * 100 ) / [-12] 15 minute vwap > -0.2 and abs ( ( [-1] 5 minute close - [-2] 15 minute close ) * 100 ) / [-2] 15 minute close < 0.2 and abs ( ( [-1] 5 minute close - [-2] 15 minute close ) * 100 ) / [-2] 15 minute close > -0.2 and abs ( ( [-4] 5 minute close - [-3] 15 minute close ) * 100 ) / [-3] 15 minute close < 0.2 and abs ( ( [-4] 5 minute close - [-3] 15 minute close ) * 100 ) / [-3] 15 minute close > -0.2 and abs ( ( [-7] 5 minute close - [-4] 15 minute close ) * 100 ) / [-4] 15 minute close < 0.2 and abs ( ( [-7] 5 minute close - [-4] 15 minute close ) * 100 ) / [-4] 15 minute close > -0.2 and abs ( ( [-1] 5 minute close - [-4] 15 minute close ) * 100 ) / [-4] 15 minute close < 0.3 and abs ( ( [-1] 5 minute close - [-4] 15 minute close ) * 100 ) / [-4] 15 minute close > -0.3 and ( ( [-1] 5 minute high - [-1] 15 minute high ) * 100 ) / [-1] 15 minute high < 0.3 and ( ( [-1] 5 minute high - [-2] 15 minute high ) * 100 ) / [-2] 15 minute high < 0.5 and ( ( [-1] 5 minute high - [-3] 15 minute high ) * 100 ) / [-3] 15 minute high < 0.5 and ( ( [-1] 5 minute high - [-1] 15 minute high ) * 100 ) / [-1] 15 minute high > -0.3 and ( ( [-1] 5 minute high - [-2] 15 minute high ) * 100 ) / [-2] 15 minute high > -0.5 and ( ( [-1] 5 minute high - [-3] 15 minute high ) * 100 ) / [-3] 15 minute high > -0.5 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open < -1 ) ) ) ) ) ) 
            #process_url('https://chartink.com/screener/morning-volume-breakout-sell-consolidation-01', 'sell-morning-volume-breakout-consolidation-01', time_11_00, time_12_30, True)
        
        if(sb.nw >= time_09_45 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( ( {cash} ( ( ( [-2] 5 minute vwap - [-4] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap < 0.1 and ( ( [-2] 5 minute vwap - [-4] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap > -0.1 and ( ( [-2] 5 minute vwap - [-8] 5 minute vwap ) * 100 ) / [-8] 5 minute vwap > -0.1 ) ) and ( {cash} ( ( ( [-10] 1 minute vwap - [-15] 1 minute vwap ) * 100 ) / [-15] 1 minute vwap < .1 and ( ( [-10] 1 minute vwap - [-20] 1 minute vwap ) * 100 ) / [-20] 1 minute vwap < .1 and ( ( [-10] 1 minute vwap - [-15] 1 minute vwap ) * 100 ) / [-15] 1 minute vwap > -0.1 and ( ( [-10] 1 minute vwap - [-20] 1 minute vwap ) * 100 ) / [-20] 1 minute vwap > -0.1 ) ) and ( {cash} ( [=1] 5 minute close < [=1] 5 minute open and [0] 5 minute low < [=1] 5 minute low and [0] 5 minute low < [=2] 5 minute low and [0] 5 minute low < [=3] 5 minute low and [0] 5 minute low < [=4] 5 minute low and [=1] 30 minute high < [=-2] 15 minute high and ( ( ( [0] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -3 and ( ( ( [=1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -3 and latest close > 100 ) ) ) ) ) ) 
            process_url('https://chartink.com/screener/morning-volume-breakout-sell-consolidation-02', 'sell-morning-volume-breakout-consolidation-02(checkfirstcandledownThenup)', time_09_45, time_10_30)
            
        
        # if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_11_30, True)
        
        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-sellBreakdownIntraday-10:15-to-11:15', time_10_15, time_11_15)
                        
            
        #time.sleep(30)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    