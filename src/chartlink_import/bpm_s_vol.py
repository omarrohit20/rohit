import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 16060})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    regression_ta_data_sell()
    
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p8")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_09_30):             
        if(sb.nw>= time_09_15 and sb.nw <= time_09_30):    
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_00, time_09_30)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-2', 'morning-volume-breakout-sell-2(lastDayMid-or-2daylow)', time_09_00, time_09_30)
   
        time.sleep(60)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    