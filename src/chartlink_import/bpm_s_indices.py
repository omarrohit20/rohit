import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 14040})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p4")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_12_00): 
        if(sb.nw>=time_09_25 and sb.nw<=time_10_15):
            process_url('https://chartink.com/screener/sell-uptrend-01', 'sell-uptrendlast2day', time_09_25, time_10_00) 
        
        if(sb.nw>= time_10_00 and sb.nw <= time_12_00):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_12_00)
        
        if(sb.nw>= time_09_40 and sb.nw <= time_10_30): 
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-03', '(==MidcapLastDayDown==)03-sellBreakdownIntraday-9:40-to-9:50', time_09_40, time_09_50)
            
        if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-sellBreakdownIntraday-10:15-to-11:15', time_10_15, time_11_15)
                        
#         if(sb.nw>= time_10_30 and sb.nw <= time_13_30):
#             process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-02', 'sell-dayconsolidation-breakout-02', time_10_30, time_13_30)
            
        time.sleep(100)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    