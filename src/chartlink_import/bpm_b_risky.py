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
            
        if(sb.nw>=time_09_25 and sb.nw<=time_10_15):
            process_url('https://chartink.com/screener/buy-downtrend-01', 'buy-downlast2day)', time_09_25, time_10_15, True) 
            
        if(sb.nw>=time_09_45 and sb.nw<=time_11_00):
            process_url('https://chartink.com/screener/buy-ema-up0', 'buy-ema-up0', time_09_45, time_11_00)
            process_url('https://chartink.com/screener/buy-ema-up1', 'buy-ema-up1', time_09_45, time_11_00)
        
        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    