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
        if(sb.nw>= time_10_00 and sb.nw <= time_11_30):    
            process_url('https://chartink.com/screener/buy-check-morning-down-breakup-01', 'buy-check-morning-down-breakup-01', time_10_00, time_11_30)
        if(sb.nw>= time_09_30 and sb.nw <= time_10_15):    
            process_url('https://chartink.com/screener/buy-check-morning-down-breakup-02', 'buy-check-morning-down-breakup-02', time_09_30, time_10_00) 
                
        if(sb.nw>= time_10_00 and sb.nw <= time_12_30):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-01', 'buy-dayconsolidation-breakout-01', time_10_00, time_12_00)
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-02', 'buy-dayconsolidation-breakout-02', time_10_00, time_12_00)
            
        if(sb.nw>= time_12_15 and sb.nw <= time_14_00):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-03-1', 'buy-dayconsolidation-breakout-03', time_12_15, time_14_00)
            
        time.sleep(100)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    