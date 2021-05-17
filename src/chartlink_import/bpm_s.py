import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'port': 16090})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p6")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30):
        if(sb.nw>=time_09_25 and sb.nw<=time_10_15):
            process_url('https://chartink.com/screener/sell-uptrend-01', 'sell-uptrendlast2day', time_09_25, time_10_00) 
            process_url('https://chartink.com/screener/sell-downtrend-01', 'sell-downtrendlast2day', time_09_25, time_10_00) 
        
            
        if(sb.nw>= time_09_20 and sb.nw <= time_11_30):    
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-02', 'sell-check-morning-up-breakdown-02', time_09_20, time_11_30)
            
                
        if(sb.nw>= time_10_00 and sb.nw <= time_12_30):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-01', 'sell-dayconsolidation-breakout-01', time_10_00, time_12_00)
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-02', 'sell-dayconsolidation-breakout-02', time_10_00, time_12_00)
        
        if(sb.nw>= time_11_15 and sb.nw <= time_14_00):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-03-1', 'sell-dayconsolidation-breakout-03', time_11_15, time_14_00)    
        
        time.sleep(200)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    