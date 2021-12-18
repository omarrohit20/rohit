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
    
    while (sb.nw <= time_11_30): 
        if(sb.nw>= time_09_30 and sb.nw <= time_10_30): 
            process_url('https://chartink.com/screener/03-sellbreakdownintraday-01', 'sell-(==Reversal-lastDayLowNotReached==)03-BreakdownIntraday', time_09_30, time_10_15, True)
            
        # if(sb.nw>= time_09_30 and sb.nw <= time_10_30): 
        #     process_url('https://chartink.com/screener/03-sellbreakdownintraday-02', '(==Reversal-Crossedlast2DayLow==)03-sellBreakdownIntraday', time_09_30, time_10_15, True)
            
        if(sb.nw>= time_09_30 and sb.nw <= time_10_45):  
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-30-to-10-3', 'sell-(=========DOWNTREND=======)breakdown-intraday-9:40-to-10:10-01', time_09_30, time_10_15, True)
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-01', 'sell-(=========DOWNTREND=======)breakdown-intraday-9:40-to-10:10-01', time_09_30, time_10_30, True)
        
        if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_11_30, True)
        
        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-sellBreakdownIntraday-10:15-to-11:15', time_10_15, time_11_15)
                        
            
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    