import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 18090})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p3")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_00): 
        if(sb.nw>= time_09_20 and sb.nw <= time_10_30):    
            #( {cash} ( [-1] 5 minute high < [=1] 5 minute high and [-1] 5 minute high < [=1] 15 minute high and [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0.3 and [=1] 1 hour low < [=-1] 5 minute high and [=1] 30 minute low = [=1] 1 hour low and [-1] 10 minute low > [=1] 1 hour low and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open < 2 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open > -2 and ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < 2 and [0] 5 minute high > [0] 5 minute ema ( [0] 5 minute close , 50 ) and [-1] 5 minute low > [-1] 5 minute vwap and [-2] 5 minute low > [-2] 5 minute vwap and [-1] 5 minute high > [-1] 5 minute vwap and [-2] 5 minute high > [-2] 5 minute vwap and [-3] 5 minute high > [-3] 5 minute vwap and [-4] 5 minute high > [-4] 5 minute vwap ) ) 
            process_url('https://chartink.com/screener/buy-check-morning-down-breakup-02', 'buy-check-morning-down-breakup-02', time_09_35, time_10_30) 
        
        if(sb.nw>= time_11_30 and sb.nw <= time_13_30):    
            process_url('https://chartink.com/screener/buy-check-morning-down-breakup-01', 'buy-check-morning-down-breakup-01', time_09_35, time_10_30)
                
        if(sb.nw>= time_09_45 and sb.nw <= time_11_15):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-01', 'buy-dayconsolidation-breakout-01(|`|_|follow-midcap-pattern)', time_09_45, time_11_30, True)
        
        if(sb.nw>= time_10_00 and sb.nw <= time_11_00):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-02', 'buy-dayconsolidation-breakout-02', time_11_00, time_12_30, True)
        
        
        if(sb.nw>= time_10_15 and sb.nw <= time_14_00):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-03', 'buy-dayconsolidation-breakout-03', time_10_15, time_14_00, True)
        
            
        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    