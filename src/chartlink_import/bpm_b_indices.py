import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 11010})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p1")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30): 
        if(sb.nw >= time_09_30 and sb.nw <= time_10_30): 
            process_url('https://chartink.com/screener/03-buybreakupintraday-01', '(==Reversal-lastDayHighNotReached==)03-buyBreakupIntraday', time_09_30, time_10_15)
        
        if(sb.nw >= time_09_30 and sb.nw <= time_10_30): 
            process_url('https://chartink.com/screener/03-buybreakupintraday-02', '(==Reversal-Crossedlast2DayHigh==)03-buyBreakupIntraday', time_09_30, time_10_15)
            
        if(sb.nw >= time_09_30 and sb.nw <= time_10_30): 
            process_url('https://chartink.com/screener/buy-breakup-intraday-9-30-to-10', '(=========UPTREND=======)buy-breakup-intraday-9:40-to-10:10', time_09_30, time_10_15)
         
        if(sb.nw >= time_10_00 and sb.nw <= time_13_30):
            process_url('https://chartink.com/screener/morning-volume-breakout-buy-consolidation-01', 'morning-volume-breakout-buy-consolidation-01', time_10_00, time_13_30)
         
        if(sb.nw >= time_10_00 and sb.nw <= time_13_30):
            process_url('https://chartink.com/screener/morning-volume-breakout-buy-consolidation-02', 'morning-volume-breakout-buy-consolidation-02', time_10_00, time_13_30)
           
        if(sb.nw >= time_10_00 and sb.nw <= time_11_30):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-04', 'buy-dayconsolidation-breakout-04(11:45-to-1:00)', time_10_00, time_11_30)
                        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/buy-breakup-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-buyBreakupIntraday-10:15-to-11:15', time_10_15, time_11_15)
        
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    