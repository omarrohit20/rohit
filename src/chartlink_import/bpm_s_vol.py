import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p8")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30):             
        if(sb.nw>= time_09_15 and sb.nw <= time_09_25):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < [=-1] 5 minute low and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [=1] 5 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.75 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_00, time_09_30)

        if (sb.nw >= time_09_25 and sb.nw <= time_09_30):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < [=-1] 5 minute low and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [=1] 5 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.75 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-2', 'morning-volume-breakout-sell-2(lastDayMid-or-2daylow)', time_09_00, time_09_30)

        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-3', 'breakout-morning-volume', time_09_00, time_09_30, 'brakout-morning-volume-sell')
        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-sell*2')
        
        
        if(sb.nw>= time_09_30 and sb.nw <= time_11_30):
            # ( {33489} ( ( {cash} ( ( ( ( [=2] 5 minute high - [=1] 5 minute open ) * 100 ) / [=1] 5 minute low ) > 0.75 and ( ( ( [=1] 20 minute high - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low ) > 2 and ( ( ( [=2] 5 minute high - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low ) > 0.75 and [=1] 5 minute close > [=1] 5 minute open and [=1] 30 minute high > 1 day ago close and [-1] 5 minute close < [=1] 5 minute open and [0] 5 minute vwap < [-2] 5 minute vwap and ( ( [0] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap < 0.3 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', 'checkChartSell-morningup(marketUp,lastDayDown-sell))', time_09_15, time_11_30)

        if(sb.nw>= time_09_30 and sb.nw <= time_10_15):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 2 and [=1] 30 minute high > 1 day ago close and [-1] 5 minute close > 1 day ago close and [-1] 5 minute close < [=1] 5 minute close and [0] 5 minute vwap < [-2] 5 minute vwap and ( ( [0] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap < -0.5 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-1', 'marketDownSell-(marketUp,lastDayUp-buyCheckBase,lastDayDown-sell)', time_09_15, time_10_15)

        if(sb.nw>= time_09_30 and sb.nw <= time_11_30):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and latest high > 1 day ago close and latest high = [=1] 10 minute high and [=1] 30 minute high = [=1] 10 minute high and [0] 5 minute vwap < [-2] 5 minute vwap and ( ( [-1] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap < 0 and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) ) ) and [=1] 5 minute close > [=1] 5 minute open and [=2] 5 minute close > [=1] 5 minute open and [=2] 5 minute open > [=1] 5 minute open and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0.5 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-after10', 'checkChartSell-morningup', time_09_15, time_11_30)

        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
