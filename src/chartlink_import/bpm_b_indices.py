import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p1")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30):
        if (sb.nw >= time_09_25 and sb.nw <= time_09_45):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close and ( ( ( [=2] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and [0] 5 minute high > [=3] 5 minute close and [0] 5 minute high > [=3] 5 minute open ) ) ) )
            process_url('https://chartink.com/screener/buy-morning-volume-breakout-checknews-01', 'buy-morning-volume-breakout(CheckNews)-01', time_09_25, time_09_45, True)

        #if(sb.nw >= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute open > 1 day ago low and [=1] 5 minute close > 1 day ago low and [-1] 5 minute high >= [-2] 15 minute high and [-1] 5 minute high >= [-3] 15 minute high and [-1] 5 minute high > [=1] 15 minute high and [-1] 5 minute high > [=2] 15 minute high and ( ( [-1] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > 0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close < 2.5 and ( ( [-1] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high < 1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open < 4 and ( ( 1 day ago high - 1 day ago open ) * 100 ) / 1 day ago high < 4 and ( ( 1 day ago high - 1 day ago low ) * 100 ) / 1 day ago low < 5 and [-1] 5 minute high < 1 day ago high and [-1] 5 minute high < 2 days ago high and ( ( 3 days ago high - [-1] 5 minute high ) * 100 ) / [-1] 5 minute high > 1 and ( ( 4 days ago high - [-1] 5 minute high ) * 100 ) / [-1] 5 minute high > 2.5 ) ) ) ) 
            #process_url('https://chartink.com/screener/03-buybreakupintraday-01', 'buy-(==Reversal-lastDayHighNotReached==)03-BreakupIntraday', time_09_40, time_10_15, True)
        
        #if(sb.nw >= time_09_40 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( [-1] 5 minute high > [=1] 15 minute high and [-1] 5 minute close > ( 1 day ago high - 1 day ago low ) / 2 + 1 day ago low and [-1] 5 minute close < 2 days ago high and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open < 0 and ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago open < -1 and 1 day ago high = [=-7] 1 hour high and [=-1] 1 hour high < [=-3] 1 hour high and ( {cash} ( [=2] 5 minute volume < greatest(  1 day ago volume / 18  ) and [=2] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 5 minute close > [=1] 5 minute open ) ) ) ) ) ) 
            #process_url('https://chartink.com/screener/03-buybreakupintraday-02', 'buy-(==Reversal-Crossedlast1DayMid==)03-buyBreakupIntraday', time_09_40, time_10_15, True)

        if(sb.nw >= time_09_45 and sb.nw <= time_10_30):
            #( {33489} ( ( {cash} ( ( {cash} ( ( ( [-2] 5 minute vwap - [-4] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap < 0.1 and ( ( [-2] 5 minute vwap - [-8] 5 minute vwap ) * 100 ) / [-8] 5 minute vwap < 0.1 and ( ( [-2] 5 minute vwap - [-4] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap > -0.1 ) ) and ( {cash} ( ( ( [-10] 1 minute vwap - [-15] 1 minute vwap ) * 100 ) / [-15] 1 minute vwap < .1 and ( ( [-10] 1 minute vwap - [-20] 1 minute vwap ) * 100 ) / [-20] 1 minute vwap < .1 and ( ( [-10] 1 minute vwap - [-15] 1 minute vwap ) * 100 ) / [-15] 1 minute vwap > -0.1 and ( ( [-10] 1 minute vwap - [-20] 1 minute vwap ) * 100 ) / [-20] 1 minute vwap > -0.1 ) ) and ( {cash} ( [=1] 5 minute close > [=1] 5 minute open and [0] 5 minute high > [=1] 5 minute high and [0] 5 minute high > [=2] 5 minute high and [0] 5 minute high > [=3] 5 minute high and [0] 5 minute high > [=4] 5 minute high and [=1] 30 minute low > [=-2] 15 minute low and ( ( ( [0] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < 3 and ( ( ( [=1] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < 3 and latest close > 100 ) ) ) ) ) )
            process_url('https://chartink.com/screener/morning-volume-breakout-buy-consolidation-02', 'buy-morning-volume-breakout-consolidation-02(checkfirstcandleupThendown)', time_09_45, time_10_30)
           
        # if(sb.nw >= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-04', 'buy-dayconsolidation-breakout-04(11:45-to-1:00)', time_10_00, time_11_30, True)
                        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/buy-breakup-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-buyBreakupIntraday-10:15-to-11:15', time_10_15, time_11_15)
        
        #time.sleep(30)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    
