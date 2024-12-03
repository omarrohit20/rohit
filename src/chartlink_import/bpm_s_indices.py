import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p4")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_00):
        if (sb.nw >= time_09_30 and sb.nw <= time_10_00):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 1 and ( ( ( [=1] 5 minute high - [=1] 15 minute open ) * 100 ) / [=1] 5 minute open ) > 0 and ( ( ( [-1] 5 minute close - [-3] 5 minute open ) * 100 ) / [=1] 5 minute open ) < -0.5 and abs ( [0] 5 minute low - [=1] 10 minute high ) > abs ( 1 day ago close - [0] 5 minute low ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0 and ( ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < 0 and ( ( ( [=1] 5 minute high - [=1] 5 minute low ) * 100 ) / 1 day ago close ) < 2 and ( ( ( [=-4] 1 hour high - 1 day ago close ) * 100 ) / 1 day ago close ) < 4 and ( ( ( [=-8] 1 hour high - 2 days ago close ) * 100 ) / 1 day ago close ) < 4 and [0] 5 minute close < [=3] 5 minute low and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 3 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" < 1.5 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > -3 and ( ( ( [=-1] 5 minute high - [=-3] 1 hour open ) * 100 ) / [=1] 5 minute open ) < 0.5 and [-1] 5 minute high < [=1] 15 minute high and [-2] 5 minute high < [=1] 15 minute high ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', '09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', time_09_30, time_10_00)

        if (sb.nw >= time_09_40 and sb.nw <= time_12_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 15  ) and ( ( ( [0] 5 minute close - [=1] 5 minute close ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( ( ( [-1] 5 minute close - [=1] 5 minute close ) * 100 ) / [=1] 5 minute open ) < -0.3 and ( ( ( [-2] 5 minute close - [=1] 5 minute close ) * 100 ) / [=1] 5 minute open ) < -0.3 and ( ( ( [0] 5 minute low - [=-1] 5 minute close ) * 100 ) / [=1] 5 minute open ) < 0 and ( ( ( [=1] 15 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < 0.3 and ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < 0 and ( ( ( [=1] 15 minute high - [=-3] 5 minute high ) * 100 ) / [=1] 5 minute open ) < 0.3 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -0.1 and ( ( ( 1 day ago high - [=1] 10 minute low ) * 100 ) / [=1] 5 minute open ) < 2 and abs ( ( ( [=-1] 5 minute close - [=-3] 1 hour open ) * 100 ) / [=1] 5 minute open ) < 1 and ( ( ( [0] 45 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [-1] 5 minute close - [=1] 5 minute high ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [=1] 5 minute high - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < 1 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > -2 and [=5] 5 minute high < [=1] 5 minute high and [-1] 5 minute close < [-1] 15 minute open and [-1] 5 minute close < [-1] 15 minute close and market cap < 500000 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-check-morning-up-breakdown-01',  '09_45:checkChartSell-morningUp', time_09_00, time_12_00)

        #if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {cash} ( ( {cash} ( [=1] 15 minute volume > greatest(  1 day ago volume / 24  ) and [-1] 5 minute low < 1 day ago low and [-1] 5 minute low < 2 days ago low and [-1] 5 minute low < 3 days ago low and [=1] 10 minute high > 1 day ago low and [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and abs ( ( 1 day ago close - 7 days ago low ) * 100 ) / 1 day ago close > 3 and ( ( [=1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close < 0 and ( {33489} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) and ( {45603} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) and ( {166311} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/supertrend-morning-sell', 'cash-sell-morning-volume', time_09_40, time_10_30)

        time.sleep(5)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    