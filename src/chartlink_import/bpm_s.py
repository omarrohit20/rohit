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
        if(sb.nw>= time_09_20 and sb.nw <= time_10_30): 
            #( {cash} ( [-1] 5 minute low > [=1] 5 minute low and [-1] 5 minute low > [=1] 15 minute low and [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < -0.3 and [=1] 1 hour high > [=-1] 5 minute low and [=1] 30 minute high = [=1] 1 hour high and [-1] 10 minute high < [=1] 15 minute high and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open > -2 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open < 2 and ( ( [-1] 5 minute close - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > -2 and [0] 5 minute low < [0] 5 minute ema ( [0] 5 minute close , 50 ) and [-1] 5 minute high < [-1] 5 minute vwap and [-2] 5 minute high < [-2] 5 minute vwap and [-1] 5 minute low < [-1] 5 minute vwap and [-2] 5 minute low < [-2] 5 minute vwap and [-3] 5 minute low < [-3] 5 minute vwap and [-4] 5 minute low < [-4] 5 minute vwap ) ) 
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-02', 'check-morning-up-breakdown-02', time_09_35, time_10_30)
        
        if(sb.nw>= time_11_30 and sb.nw <= time_13_30):    
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'check-morning-up-breakdown-01', time_09_35, time_10_30, True)    
                
        if(sb.nw>= time_09_45 and sb.nw <= time_11_15):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-01', 'sell-dayconsolidation-breakout-01(|_|`|follow-midcap-pattern)', time_09_45, time_11_30, True)
        
        if(sb.nw>= time_10_00 and sb.nw <= time_11_00):    
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-02', 'sell-vol-dayconsol-wait', time_10_00, time_11_00, True)
            
        if(sb.nw>= time_10_15 and sb.nw <= time_14_00):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-03', 'sell-dayconsolidation-breakout-03', time_10_15, time_14_00, True)
                
        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    