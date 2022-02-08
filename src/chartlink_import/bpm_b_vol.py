import sbase as sb
from config import *


     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 13030})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    #regression_ta_data_buy()
    
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p7")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30):             
        if(sb.nw>= time_09_15 and sb.nw <= time_09_25):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_00, time_09_30)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs', 'morning-volume-bs', time_09_00, time_09_30)
            
        if(sb.nw>= time_09_20 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'morning-volume-breakout-buy', time_09_00, time_09_30)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_00, time_09_30)
            
        if(sb.nw>= time_09_15 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-3', 'morning-volume-breakout-buy-lastDayDown', time_09_00, time_09_30)
            
   
        if(sb.nw>= time_09_50 and sb.nw <= time_11_30):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'morning-volume-breakout-after10(BuyInUptrend)', time_10_00, time_11_30)
            
        if(sb.nw>= time_11_30 and sb.nw <= time_12_15):
            #( {cash} ( abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( [-1] 5 minute close - [-6] 5 minute close ) * 100 ) / [-6] 5 minute close ) > 0.3 and ( ( ( [=1] 30 minute high - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.75 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0.3 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [-1] 1 hour "close - 1 candle ago close / 1 candle ago close * 100" > -0.3 and [0] 5 minute high < [=1] 30 minute high and [-1] 5 minute high < [=1] 30 minute high and [-1] 5 minute low > [-1] 5 minute ema ( [-1] 5 minute close , 50 ) and [-3] 5 minute low > [-3] 5 minute ema ( [-3] 5 minute close , 50 ) and [-6] 5 minute low > [-6] 5 minute ema ( [-6] 5 minute close , 50 ) and [-12] 5 minute low > [-12] 5 minute ema ( [-12] 5 minute close , 50 ) and [-1] 5 minute low > [-1] 5 minute sma ( [-1] 5 minute close , 50 ) and [-3] 5 minute low > [-3] 5 minute sma ( [-3] 5 minute close , 50 ) and [-6] 5 minute low > [-6] 5 minute sma ( [-6] 5 minute close , 50 ) and [-1] 5 minute sma ( [-1] 5 minute close , 50 ) > [-3] 5 minute sma ( [-3] 5 minute close , 50 ) and [-3] 5 minute sma ( [-3] 5 minute close , 50 ) > [-6] 5 minute sma ( [-6] 5 minute close , 50 ) and [-1] 5 minute ema ( [-1] 5 minute close , 50 ) > [-3] 5 minute ema ( [-3] 5 minute close , 50 ) and [-3] 5 minute ema ( [-3] 5 minute close , 50 ) > [-6] 5 minute ema ( [-6] 5 minute close , 50 ) and [-6] 5 minute ema ( [-6] 5 minute close , 50 ) > [-12] 5 minute ema ( [-12] 5 minute close , 50 ) and [-12] 5 minute ema ( [-12] 5 minute close , 50 ) > [-24] 5 minute ema ( [-24] 5 minute close , 50 ) and ( ( ( [-1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago open ) > 0 and ( ( ( [-1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago open ) < 3 and ( ( ( [=1] 5 minute open - 2 days ago open ) * 100 ) / 2 days ago open ) < 5 and ( ( ( [=1] 5 minute open - 1 day ago open ) * 100 ) / 1 day ago open ) < 4 and ( ( ( [=1] 30 minute high - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) < 3 and ( ( ( [=-2] 5 minute high - [=-25] 5 minute high ) * 100 ) / [=-2] 5 minute high ) < 1 and [=2] 5 minute low > [=2] 5 minute ema ( [=2] 5 minute close , 50 ) and [=3] 5 minute low > [=3] 5 minute ema ( [=3] 5 minute close , 50 ) and [=3] 5 minute high > [=3] 5 minute vwap and [=1] 15 minute low < [=-2] 2 hour high ) ) 
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'morning-volume-breakout-after11:30', time_11_30, time_12_15)
        
        if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
            #( {cash} ( [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < -1.5 and [=1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < -1.5 and [-1] 5 minute high < [-1] 5 minute ema ( [0] 5 minute close , 50 ) and [-2] 5 minute high < [-1] 5 minute ema ( [-2] 5 minute close , 50 ) and [-3] 5 minute high < [-1] 5 minute ema ( [-3] 5 minute close , 50 ) and [-4] 5 minute high < [-1] 5 minute ema ( [-4] 5 minute close , 50 ) and [-5] 5 minute high < [-1] 5 minute ema ( [-5] 5 minute close , 50 ) and [-1] 5 minute high > [-1] 5 minute vwap and [-2] 5 minute close > [-1] 5 minute vwap and [-3] 5 minute close > [-1] 5 minute vwap and [-4] 5 minute close > [-1] 5 minute vwap and [-5] 5 minute close > [-1] 5 minute vwap and [-6] 5 minute close > [-1] 5 minute vwap and [-7] 5 minute close > [-1] 5 minute vwap and [-8] 5 minute close > [-1] 5 minute vwap and [-1] 5 minute close > [-1] 5 minute vwap and [=1] 30 minute high = [=1] 1 hour high and [=2] 30 minute high < [=1] 30 minute high and ( ( ( [=1] 30 minute high - [=2] 30 minute high ) * 100 ) / [=2] 30 minute high ) > 0.5 ) ) 
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-1', 'buy-morning-down-breakout-VWAP-10', time_10_00, time_11_30)
            
        if(sb.nw>= time_11_30 and sb.nw <= time_13_00):
            #( {cash} ( [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < -1.5 and [=1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < -1.5 and [-1] 5 minute low > [-1] 5 minute ema ( [0] 5 minute close , 50 ) and [-1] 5 minute close > [-1] 5 minute ema ( [0] 5 minute close , 50 ) and [-1] 5 minute low > [-1] 5 minute sma ( [-1] 5 minute close , 50 ) and [-1] 5 minute close > [-1] 5 minute sma ( [-1] 5 minute close , 50 ) and [-1] 5 minute low > [-1] 5 minute vwap and [-1] 5 minute close > [-1] 5 minute vwap ) ) 
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-0', 'buy-morning-down-breakout-VWAP-11:30', time_11_30, time_13_00)
        
        if(sb.nw>= time_09_45 and sb.nw <= time_11_00):
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'buy-morning-down-breakout-VWAP-09:45', time_09_45, time_11_00)
            
        if(sb.nw>= time_11_30 and sb.nw <= time_13_30):
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-3', 'buy-morning-down-breakout-VWAP-11:30', time_11_30, time_13_30)
        
        
            
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    