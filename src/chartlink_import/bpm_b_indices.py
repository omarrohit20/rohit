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
        if(sb.nw>= time_09_40 and sb.nw <= time_10_30): 
            process_url('https://chartink.com/screener/03-buybreakupintraday-01', '(==Reversal==)03-buyBreakupIntraday', time_09_40, time_09_50)
        
        if(sb.nw>= time_09_40 and sb.nw <= time_11_00): 
            process_url('https://chartink.com/screener/03-buybreakupintraday-02', '(==Continue==)03-buyBreakupIntraday', time_09_40, time_10_30)
            
        if(sb.nw>= time_09_40 and sb.nw <= time_10_30):  
            process_url('https://chartink.com/screener/buy-breakup-intraday-9-30-to-10', '(=========UPTREND=======)buy-breakup-intraday-9:40-to-10:10-01', time_09_40, time_10_15)
        
        if(sb.nw>= time_09_20 and sb.nw <= time_10_30):
            process_url('https://chartink.com/screener/buy-breakup-intraday-9-25-to-10-30-06', 'buy-breakupGT2-intraday-9:25-to-10:30', time_09_25, time_10_30)
            
        if(sb.nw>= time_11_30 and sb.nw <= time_13_30):
            process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-04', 'buy-dayconsolidation-breakout-04(11:45-to-1:00)', time_11_30, time_13_00)
        
        
                        
        # if(sb.nw>= time_10_15 and sb.nw <= time_11_30):   
        #     process_url('https://chartink.com/screener/buy-breakup-intraday-9-50-to-10-10-04', '(==AvoidSpikeMA50==)04-buyBreakupIntraday-10:15-to-11:15', time_10_15, time_11_15)
        
        
        time.sleep(100)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    