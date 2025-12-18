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
    
    while (sb.nw <= time_11_15):
        if (sb.nw >= time_09_22 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [0] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) < -0.6 and ( ( ( [0] 5 minute low - [=-1] 5 minute low ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.3 and ( ( ( [0] 5 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.8 and ( ( ( [=1] 5 minute open - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < 1 and ( ( ( [=1] 5 minute high - [=-1] 5 minute high ) * 100 ) / [=1] 5 minute open ) < 1.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -1 and ( ( ( [0] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.8 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_15, time_11_00)

        if (sb.nw >= time_10_00 and sb.nw <= time_12_00):
            # ( {33489} ( ( {cash} ( ( ( ( [-1] 5 minute low - 1 day ago low ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [-1] 5 minute low - 2 days ago low ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [-1] 5 minute low - 2 days ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 30 minute low - 1 day ago open ) * 100 ) / 1 day ago close ) > -3 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < 1 and ( ( ( [-1] 5 minute close - [=1] 10 minute low ) * 100 ) / 1 day ago close ) < 0 and ( ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.7 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1.3 and ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.3 and ( ( ( 1 day ago low - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.5 and ( ( ( 1 day ago open - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.5 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [=1] 1 hour high - 1 day ago close ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [=1] 1 hour low - [-1] 15 minute low ) * 100 ) / 1 day ago close ) > -0.5 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 2 and [-1] 5 minute close < [=1] 10 minute low and ( ( ( [-1] 5 minute close - [-2] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -0.7 and ( ( ( [-1] 5 minute close - [-3] 5 minute low ) * 100 ) / [=1] 5 minute open ) > -0.9 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-breakout', time_10_00, time_11_45)

        if (sb.nw >= time_09_30 and sb.nw <= time_11_00):
            # Weekly Low not reached
            # ( {33489} ( ( {33489} ( ( ( ( [0] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -2.5 and ( ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.75 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( weekly low - 1 day ago low ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( 1 week ago low - [=1] 5 minute low ) * 100 ) / 1 day ago close ) < 0 and ( ( ( 1 week ago low - 1 day ago low ) * 100 ) / 1 day ago close ) < 0 and ( [=1] 15 minute high - [-1] 5 minute high ) > ( [-1] 5 minute low - [=1] 15 minute low ) ) ) and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 15  ) and [=1] 30 minute low < [-1] 5 minute low and [=1] 5 minute low > [-1] 5 minute low and [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > -1.5 and ( ( ( 1 day ago close - 1 day ago low ) * 100 ) / 1 day ago close ) > -2 and ( ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago close ) > -2 and ( ( ( [-1] 5 minute close - [-2] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -0.7 and ( ( ( [-1] 5 minute close - [-3] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-2', 'Breakout-Siill-2', time_09_30, time_11_00)

        #if (sb.nw >= time_10_30 and sb.nw <= time_12_00):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 5 minute close - [=1] 5 minute low ) * 100 ) / 1 day ago close ) > -2 and ( ( ( 1 day ago close - 1 day ago low ) * 100 ) / 1 day ago close ) > -2 and [=1] 5 minute open > 1 day ago low and [=1] 5 minute high > [=-2] 30 minute low and [=1] 5 minute high < 1 day ago high ) ) and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [0] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) < -0.6 and ( ( ( [0] 5 minute low - [=-1] 5 minute low ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.9 and ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < 0 and [-1] 5 minute close < [=1] 5 minute open and [-1] 5 minute close < [=1] 5 minute close and ( ( ( [=1] 10 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -2 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / [=1] 5 minute open ) > -2.5 ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-3', 'Breakout-Sill-3', time_10_30, time_11_00)

        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
