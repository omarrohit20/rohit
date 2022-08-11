import sbase as sb
from config import *

if __name__ == "__main__":
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p7")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()

    while (sb.nw <= time_13_30):
        if (sb.nw >= time_09_15 and sb.nw <= time_09_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > [=-1] 5 minute high and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.5 and ( ( ( [=1] 5 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.75 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_00, time_09_30)

        if(sb.nw>= time_09_20 and sb.nw <= time_09_30):
            #( {33489} ( ( {cash} ( [=2] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=2] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=2] 5 minute close > [=2] 5 minute open and [=2] 5 minute close > [=-1] 5 minute high and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.5 and ( ( ( [=1] 5 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.75 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'morning-volume-breakout-buy', time_09_00, time_09_30)
            
        if(sb.nw>= time_09_20 and sb.nw <= time_09_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( [=1] 5 minute high - [=1] 5 minute close ) * 100 ) / [=1] 5 minute close < 1 and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close ) ) and ( {cash} ( [=1] 5 minute close > [=-1] 5 minute high and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 ) ) ) ) 
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-3', 'breakout-morning-volume', time_09_00, time_09_30, 'breakout-morning-volume-buy')
        
        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-buy*2')
        
        
        #if(sb.nw>= time_09_50 and sb.nw <= time_11_30):
            #process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'morning-volume-breakout-after10(BuyInUptrend)', time_10_00, time_11_30)

        if(sb.nw>= time_09_30 and sb.nw <= time_11_30):
            #( {cash} ( ( ( ( [=2] 5 minute low - [=1] 5 minute open ) * 100 ) / [=1] 5 minute high ) < -0.75 and ( ( ( [=2] 5 minute low - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high ) < -2 and ( ( ( [=2] 5 minute low - [-1] 5 minute high ) * 100 ) / [-1] 5 minute high ) < -0.75 and [=1] 5 minute close < [=1] 5 minute open and latest low < 1 day ago close and [-1] 5 minute close > [=1] 5 minute close and [0] 5 minute vwap > [-2] 5 minute vwap and ( ( [0] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > -0.3 ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-0', 'checkChartBuy-morningDown(marketDown,lastDayUp-buy)', time_09_15, time_11_30)

        if(sb.nw>= time_09_30 and sb.nw <= time_10_15):
            #( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -2 and latest low < 1 day ago close and [-1] 5 minute close < 1 day ago close and [-1] 5 minute close > [=1] 5 minute close and [0] 5 minute vwap > [-2] 5 minute vwap and ( ( [0] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > 0.5 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-1', 'marketUpBuy-(marketDown,lastDayDown-sellCheckBase,lastDayUp-buy)', time_09_15, time_10_15)

        #if(sb.nw>= time_10_15 and sb.nw <= time_11_15):
            #( {33489} ( ( {cash} ( [=2] 5 minute low > [=2] 5 minute ema ( [=2] 5 minute close , 50 ) and [=1] 5 minute high > [=1] 5 minute ema ( [=1] 5 minute close , 50 ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 50 ) and [-1] 5 minute high > [-1] 5 minute vwap and [-1] 5 minute close > [-1] 5 minute vwap and [-2] 5 minute close > [-1] 5 minute vwap and [-4] 5 minute close < [-1] 5 minute vwap and [-5] 5 minute close < [-1] 5 minute vwap and [-6] 5 minute close < [-1] 5 minute vwap and [-7] 5 minute close < [-1] 5 minute vwap and [-8] 5 minute close < [-1] 5 minute vwap and [=1] 30 minute high = [=1] 1 hour high and [=2] 30 minute high < [=1] 30 minute high and [=1] 30 minute low < [=-2] 30 minute high and ( ( ( [-1] 5 minute high - [-4] 5 minute low ) * 100 ) / [-4] 5 minute low ) < 0.75 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > 0.5 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) > 0.5 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) < 3 and ( [0] 5 minute vwap - [0] 5 minute ema ( [0] 5 minute close , 50 ) ) < ( [-12] 5 minute vwap - [-12] 5 minute ema ( [-12] 5 minute close , 50 ) ) / 2 and ( [0] 5 minute vwap - [0] 5 minute ema ( [0] 5 minute close , 50 ) ) > 0 and [0] 5 minute high < [=1] 5 minute open and [=-2] 1 hour high > [=-6] 1 hour high and [=-3] 1 hour high > [=-6] 1 hour high ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'buy-morning-down-breakout-VWAP-2-10:15', time_10_15, time_11_15)

        #if(sb.nw>= time_11_30 and sb.nw <= time_13_30):
            #process_url_volBreakout('https://chartink.com/screener/buy-morning-down-3', 'buy-morning-down-breakout-VWAP-3-11:30', time_11_30, time_13_30)
        
        
            
        time.sleep(10)
        sb.nw = datetime.now()

    sb.driver.quit()
    