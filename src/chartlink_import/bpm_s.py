import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 17070})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p6")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_00):
        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            #( {33489} ( ( {cash} ( [=1] 3 minute volume > greatest(  1 day ago volume / 24  ) and [=5] 1 minute low < [=5] 1 minute vwap and [=6] 1 minute low < [=6] 1 minute vwap and [=7] 1 minute low < [=7] 1 minute vwap and [=8] 1 minute open < [=8] 1 minute vwap and [=8] 1 minute close < [=8] 1 minute vwap and [=8] 1 minute low < [=5] 1 minute low and [=1] 5 minute high < [=-2] 15 minute high ) ) ) ) 
            process_url('https://chartink.com/screener/sell-morning-volume-breakout-after10', 'sell-morning-volume-breakout(CheckNews)', time_09_25, time_09_45, True)
            #( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < 1 day ago close and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 ) ) ) ) 
            process_url('https://chartink.com/screener/sell-morning-volume-breakout-checknews-01', 'sell-morning-volume-breakout(CheckNews)-01', time_09_25, time_09_45, True)
    
        if(sb.nw>= time_09_35 and sb.nw <= time_10_30): 
            #( {cash} ( [-1] 5 minute low > [=1] 5 minute low and [-1] 5 minute low > [=1] 15 minute low and [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < -0.3 and [=1] 1 hour high > [=-1] 5 minute low and [=1] 30 minute high = [=1] 1 hour high and [-1] 10 minute high < [=1] 15 minute high and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open > -2 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open < 2 and ( ( [-1] 5 minute close - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > -2 and [0] 5 minute low < [0] 5 minute ema ( [0] 5 minute close , 50 ) and [-1] 5 minute high < [-1] 5 minute vwap and [-2] 5 minute high < [-2] 5 minute vwap and [-1] 5 minute low < [-1] 5 minute vwap and [-2] 5 minute low < [-2] 5 minute vwap and [-3] 5 minute low < [-3] 5 minute vwap and [-4] 5 minute low < [-4] 5 minute vwap ) ) 
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-02', 'check-morning-up-breakdown-02', time_09_35, time_10_30, True)
        
        if(sb.nw>= time_12_00 and sb.nw <= time_13_30):    
            #( {33489} ( ( {cash} ( [-1] 5 minute low > [=1] 5 minute low and [-1] 5 minute low > [=1] 15 minute low and [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < -0.3 and [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [=1] 30 minute low < [=2] 30 minute low and [=2] 30 minute low < [=3] 30 minute low and [=3] 30 minute low < [=4] 30 minute low and [=4] 30 minute low < [=5] 30 minute low and [=3] 30 minute high < [=5] 30 minute high and [=4] 30 minute high < [=5] 30 minute high and [-1] 5 minute vwap < [-3] 5 minute vwap and ( ( [-1] 5 minute close - [-3] 5 minute open ) * 100 ) / [-3] 5 minute open < 0 and ( ( [=1] 15 minute low - latest high ) * 100 ) / [=1] 15 minute low < -1.5 and ( ( [=1] 15 minute high - latest high ) * 100 ) / [=1] 15 minute low > -2 and ( ( [=1] 5 minute open - [=2] 30 minute high ) * 100 ) / [=1] 5 minute open < 0 and [0] 5 minute close < ( latest high - ( ( latest high - latest low ) / 3 ) ) and [0] 5 minute close > ( latest high - ( ( latest high - latest low ) / 2 ) ) and latest high > 1 day ago low ) ) and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) ) ) ) ) 
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'check-morning-up-breakdown-01', time_12_00, time_13_30, True)    
                
        if(sb.nw>= time_09_45 and sb.nw <= time_11_15):
            #( {33489} ( ( {cash} ( ( ( [-1] 5 minute vwap - [-12] 5 minute vwap ) * 100 ) / [-12] 5 minute vwap < 0.1 and ( ( [-1] 5 minute vwap - [-12] 5 minute vwap ) * 100 ) / [-12] 5 minute vwap > -0.1 and [-1] 15 minute high < [=1] 5 minute open and [-1] 15 minute high < [=1] 15 minute high and [-1] 15 minute high > [=1] 1 hour low and [-1] 15 minute high < [=-1] 1 hour low and [-2] 15 minute high < [=1] 5 minute open and [-2] 15 minute high < [=1] 15 minute high and [-2] 15 minute high > [=1] 1 hour low and ( {cash} ( ( ( [-1] 5 minute high - [-12] 5 minute high ) * 100 ) / [-12] 5 minute high < 1 and ( ( [-1] 5 minute low - [-12] 5 minute low ) * 100 ) / [-12] 5 minute low < 1 and ( ( [-8] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high < 1 and ( ( [-8] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < 1 and ( ( [-1] 5 minute high - [-12] 5 minute high ) * 100 ) / [-12] 5 minute high > -1 and ( ( [-1] 5 minute low - [-12] 5 minute low ) * 100 ) / [-12] 5 minute low > -1 and ( ( [-8] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > -1 and ( ( [-8] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1 and ( ( [=1] 5 minute low - [=-1] 15 minute low ) * 100 ) / [=-1] 15 minute low > -4 and ( ( [-1] 5 minute low - [=-1] 15 minute low ) * 100 ) / [=-1] 15 minute low > -4 and ( latest low - [=1] 5 minute low ) < ( [=1] 5 minute low - [=1] 5 minute high ) and ( [=1] 1 hour high - [-1] 5 minute close ) > ( [-1] 5 minute close - [=1] 1 hour low ) and ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close < -1 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 1 and [=-2] 2 hour low < [=-3] 2 hour low and ( ( ( [0] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 0 and ( ( ( [0] 5 minute close - [=-7] 1 hour high ) * 100 ) / [=-7] 1 hour high ) > -5 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > -2 ) ) ) ) ) ) 
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-01', 'sell-dayconsolidation-breakout-01(|_|`|follow-midcap-pattern)', time_09_45, time_11_30, True)
        
        if(sb.nw>= time_10_00 and sb.nw <= time_11_00):    
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close ) > -4 and ( ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close ) < -1.5 and ( ( ( [=1] 30 minute low - [-1] 5 minute close ) * 100 ) / [-1] 5 minute close ) > -0.5 and ( ( ( 1 day ago close - 3 days ago close ) * 100 ) / 1 day ago close ) > -6 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) > -3 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [0] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [=1] 15 minute high > 1 day ago low and [=1] 15 minute high > [=-1] 15 minute low and [-1] 5 minute high < [=1] 15 minute low and [=2] 15 minute high < [=-1] 15 minute low and [=2] 15 minute high < [=-2] 15 minute low ) ) ) ) 
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-02', 'sell-vol-dayconsol-wait', time_10_00, time_11_00, True)
            
        #if(sb.nw>= time_10_15 and sb.nw <= time_14_00):
            #process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-03', 'sell-dayconsolidation-breakout-03', time_10_15, time_14_00, True)
                
        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    