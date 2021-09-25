import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 12020})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p2")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_30):
        if(sb.nw>= time_09_15 and sb.nw <= time_10_00): 
            process_url('https://chartink.com/screener/supertrend-morning-buy', 'buy-supertrend-morning', time_09_15, time_10_00, True)
            
        if(sb.nw>= time_09_20 and sb.nw <= time_10_30):
            process_url('https://chartink.com/screener/buy-breakup-intraday-9-25-to-10-30-06', 'buy-breakupGT2-intraday-9:25-to-10:30', time_09_25, time_10_30, True)
        
        if(sb.nw>=time_09_25 and sb.nw<=time_10_15):
            process_url('https://chartink.com/screener/buy-downtrend-01', 'downlast2day(last3rdDownGT(-0.5)-Sell)(last3rdDownLt(-0.5)-Buy)', time_09_25, time_10_15, True) 
            
        if(sb.nw>= time_09_25 and sb.nw <= time_10_30):    
            process_url('https://chartink.com/screener/buy-check-morning-down-breakup-03', 'buy-check-morning-down-breakup-03', time_09_25, time_10_30)
            
        if(sb.nw>= time_11_00 and sb.nw <= time_12_30):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-03-1', 'buy-dayconsolidation-breakout-03-checkChart', time_11_00, time_12_30, True)
                 
        
            
              
        #process_url('https://chartink.com/screener/buy-check-morning-down-breakup-02', 'buy-check-morning-down-breakup-02')
        
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    