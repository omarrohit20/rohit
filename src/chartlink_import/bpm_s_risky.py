import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 15050})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p5")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_30): 
        if(sb.nw>= time_09_15 and sb.nw <= time_10_00): 
            process_url('https://chartink.com/screener/supertrend-morning-sell', 'sell-supertrend-morning', time_09_15, time_10_00)
            
        if(sb.nw>= time_09_20 and sb.nw <= time_10_30):
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-25-to-10-30-06', 'sell-breakdownGT2-intraday-9:25-to-10:30', time_09_25, time_10_30)
            
        if(sb.nw>=time_09_25 and sb.nw<=time_10_15):
            process_url('https://chartink.com/screener/sell-uptrend-01', 'uplast2day(last3rdUpLT(0.5)-Buy)(last3rdUpGT(0.5)-Sell)', time_09_25, time_10_00) 
            
        if(sb.nw>= time_09_25 and sb.nw <= time_10_30):    
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-03', 'sell-check-morning-up-breakdown-03', time_09_25, time_10_30)   
        
        if(sb.nw>= time_11_00 and sb.nw <= time_12_30):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-03-1', 'sell-dayconsolidation-breakout-03-checkChart', time_11_00, time_12_30)
           
        
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    