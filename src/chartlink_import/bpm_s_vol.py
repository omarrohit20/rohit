import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p8")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    regression_ta_data_sell()
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_11_00):
        if(sb.nw>= time_09_15 and sb.nw <= time_09_30):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 10 minute close < [=-1] 5 minute low and abs ( ( ( [=1] 10 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( [=1] 10 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [=1] 10 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.75 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" > -1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_00, time_09_30)

        if (sb.nw >= time_09_40 and sb.nw <= time_11_00):
            # ( {46553} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.75 and [-1] 5 minute low < [=2] 5 minute low and [-1] 5 minute close < [=2] 5 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-checknews-01', 'sell-morning-volume-breakout(Check-News)-01', time_09_40, time_11_00)

        if (sb.nw >= time_09_50 and sb.nw <= time_11_00):
            # ({33489}(({cash}([=1] 5 minute volume > greatest(  1 day ago volume/ 24) and (
            #             (([-1] 5 minute close - 1 day ago close) * 100) / 1 day ago close) < -0.75 and (
            #                      (([-1] 5 minute close - 1 day ago close) * 100) / 1 day ago close) > -2.5 and [-1]
            #  5 minute open <[=1] 5 minute open and[-1] 5 minute close <[=1] 5 minute open and[-1] 5 minute close <[-1] 5 minute open and[-1] 5 minute low <[-2] 5 minute low and[-1] 5 minute high <[-2] 5 minute high and[-1] 5 minute low >[=1] 10 minute low and[-1] 5 minute high <[=1] 10 minute high and[-1] 10 minute high <[=1] 10 minute high and[-1] 15 minute high <[=1] 10 minute high) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-checknews', 'buy-morning-volume-breakout(Check-News)', time_09_50, time_11_00)


        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
