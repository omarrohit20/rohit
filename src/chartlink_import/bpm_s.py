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
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'sell-check-morning-up-breakdown-01', time_09_20, time_10_30)
        if(sb.nw>= time_09_20 and sb.nw <= time_10_30):    
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-02', 'sell-check-morning-up-breakdown-02', time_09_20, time_10_30)
            
                
        if(sb.nw>= time_09_45 and sb.nw <= time_12_30):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-01', 'sell-dayconsolidation-breakout-01', time_09_45, time_12_00)
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-02', 'sell-dayconsolidation-breakout-02', time_09_45, time_12_00)
        
        if(sb.nw>= time_10_15 and sb.nw <= time_14_00):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-03', 'sell-dayconsolidation-breakout-03', time_10_15, time_14_00)
                
        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    