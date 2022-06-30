import sbase as sb
from config import *
     
if __name__ == "__main__":
    sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 16060})
    time.sleep(1)
    sb.server.start()
    time.sleep(1)
    sb.proxy = sb.server.create_proxy()
    #regression_ta_data_sell()
    
    print("Server started")
    
    sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p8")
    sb.option.add_argument('--headless')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    
    sb.nw = datetime.now()
    
    while (sb.nw <= time_13_30):             
        if(sb.nw>= time_09_15 and sb.nw <= time_09_30): 
            #( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < [=-1] 5 minute low and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 ) ) 
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_00, time_09_30)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-2', 'morning-volume-breakout-sell-2(lastDayMid-or-2daylow)', time_09_00, time_09_30)
                    
        if(sb.nw>= time_09_20 and sb.nw <= time_09_30):    
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-3', 'breakout-morning-volume', time_09_00, time_09_30, 'brakout-morning-volume-sell')
        if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-sell*2')
        
        
        #if(sb.nw>= time_09_50 and sb.nw <= time_11_30):
            #process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-after10', 'sell-morning-volume-breakout-after10(SellInDowntrend)', time_10_00, time_11_30)
        
        if(sb.nw>= time_10_15 and sb.nw <= time_11_15):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( [=1] 5 minute high - [=1] 5 minute close ) * 100 ) / [=1] 5 minute close < 1 and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close ) ) and ( {cash} ( [=1] 5 minute close > [=-1] 5 minute high and abs ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 ) ) and ( {cash} ( ( ( [-1] 5 minute close - [0] 1 hour low ) * 100 ) / [-1] 5 minute close < 0.75 and ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [-1] 5 minute close < 2 and ( ( [=1] 1 hour high - [=1] 5 minute open ) * 100 ) / [=1] 5 minute high > 1.5 and ( ( [=1] 1 hour high - 1 day ago close ) * 100 ) / 1 day ago close > 1.5 and [0] 5 minute high < [-1] 5 minute high and [0] 5 minute high < [-2] 5 minute high and [0] 5 minute high < [-3] 5 minute high and [0] 5 minute high < [0] 5 minute vwap and [-2] 15 minute low > [=1] 5 minute open and [-1] 15 minute low > [=1] 5 minute open and [-1] 15 minute high < [=1] 15 minute high ) ) ) ) 
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', 'checkchart-morningup-VWAP-EMA-0-10:30(aroudVWAPSell-returnEMABuy)', time_10_15, time_11_15)

        if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [-1] 5 minute low < [-1] 5 minute vwap and [-2] 5 minute low < [-2] 5 minute vwap and [-3] 5 minute low < [-3] 5 minute vwap and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [-5] 5 minute high ) > -2.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [-5] 5 minute high ) < -1 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low ) > 0 and ( ( ( [=2] 5 minute high - [=1] 3 hour high ) * 100 ) / [=2] 5 minute high ) < -0.75 and ( ( ( [=1] 10 minute high - [=1] 3 hour high ) * 100 ) / [=1] 10 minute high ) < 0.5 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) < 0.5 and [=1] 3 hour high < [=-2] 15 minute high ) ) ) ) 
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-1', 'Midcap-DownSell-UpBuy-morningbreakout-up-VWAP-1-10', time_10_00, time_11_30)
            
        

        time.sleep(30)
        sb.nw = datetime.now()
        
    sb.server.stop()
    sb.driver.quit()
    