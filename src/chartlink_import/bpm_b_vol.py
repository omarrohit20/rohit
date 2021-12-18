import sbase as sb
from config import *


     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 13030})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    regression_ta_data_buy()
    
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p7")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30):             
        if(sb.nw>= time_09_15 and sb.nw <= time_09_30):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_00, time_09_30)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'morning-volume-breakout-buy', time_09_00, time_09_30)
   
        if(sb.nw>= time_09_30 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_30, time_09_45)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_30, time_09_45)
            
        if(sb.nw>= time_09_50 and sb.nw <= time_10_30):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'morning-volume-breakout-after10', time_10_00, time_10_30)
            
        if(sb.nw>= time_09_50 and sb.nw <= time_10_30):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-2-1', 'morning-volume-breakout-after10-consol-or-/-PCTLT1.5', time_10_00, time_10_30)
            
        if(sb.nw>= time_11_15 and sb.nw <= time_12_15):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-2-1', 'morning-volume-breakout-after(First15minuteHighestInFirstHour)11-|-|_|or/', time_11_15, time_12_15)
        
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    