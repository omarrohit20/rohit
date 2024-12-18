import pathlib
import sbase as sb
from config import *

if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p7")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    regression_ta_data_buy()
    print('Started')
    sb.nw = datetime.now()

    while (sb.nw <= time_11_00):
        if (sb.nw >= time_09_15 and sb.nw <= time_09_45):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  2 days ago volume / 15  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and ( ( ( [=1] 5 minute close - [=1] 5 minute low ) * 100 ) / 1 day ago close ) < 2 and ( ( ( 1 day ago close - 1 day ago low ) * 100 ) / 1 day ago close ) < 2 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and [=1] 5 minute open < 1 day ago high and [=1] 5 minute low < [=-2] 30 minute high and [=1] 5 minute low > 1 day ago low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'morninglow-high-volume-buy', time_09_00, time_09_45)

        if (sb.nw >= time_09_20 and sb.nw <= time_09_45):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [0] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.6 and ( ( ( [=1] 15 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.3 and ( ( ( [0] 5 minute high - [=-1] 5 minute high ) * 100 ) / [=1] 5 minute open ) > 0.5 and ( ( ( [=1] 15 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) ) ) ) 
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_00, time_09_45)

        if (sb.nw >= time_09_30 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [=2] 10 minute high - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) < 3 and ( ( ( [=1] 15 minute close - [=1] 15 minute open ) * 100 ) / [=1] 5 minute open ) < 2 and ( ( ( [=1] 30 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < 3 and ( ( ( [=1] 30 minute high - [=1] 30 minute low ) * 100 ) / [=1] 5 minute open ) < 3 and ( ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.6 and ( ( ( [=1] 15 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.3 and ( ( ( [-1] 5 minute high - [=-1] 5 minute high ) * 100 ) / [=1] 5 minute open ) > 0 and ( ( ( [=1] 15 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 1.3 and ( ( ( [=1] 5 minute close - 2 days ago open ) * 100 ) / 2 days ago open ) < 4 and ( ( ( [=1] 5 minute close - 2 days ago low ) * 100 ) / 2 days ago low ) < 5 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) < 3 and ( ( ( 1 day ago close - 1 day ago low ) * 100 ) / 1 day ago close ) < 3 and ( ( ( 1 day ago close - 3 days ago close ) * 100 ) / 1 day ago close ) > -3 and ( ( ( [=1] 15 minute high - [=-3] 2 hour low ) * 100 ) / 1 day ago close ) < 2 and [=1] 45 minute low = [=1] 15 minute low and [-1] 5 minute low > [=2] 5 minute high and [-1] 5 minute high > [=2] 5 minute low and [-2] 5 minute high > [=2] 5 minute low and [-3] 5 minute high > [=2] 5 minute low and [-4] 5 minute high > [=2] 5 minute low and abs ( [=2] 10 minute high - [=2] 5 minute high ) < abs ( [=2] 5 minute high - 1 day ago close ) ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'Breakout-Buy-2', time_09_35, time_12_30)

        if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 15  ) and [-2] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [-1] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > -0.1 and [-1] 5 minute close > [=2] 5 minute high and ( ( ( [0] 5 minute high - [-2] 5 minute low ) * 100 ) / 1 day ago close ) < 0.7 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 3 and ( ( ( [=1] 15 minute high - [=-3] 2 hour low ) * 100 ) / 1 day ago close ) < 2 and [=1] 15 minute low > [=-1] 15 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews-02', 'buy-morning-volume-breakout(Check-News)-02', time_09_50, time_11_00)

        if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and abs ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > 1.6 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 2 and ( ( ( [=1] 15 minute high - [=-3] 2 hour low ) * 100 ) / 1 day ago close ) < 2 and [-1] 5 minute open > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute high > [-2] 5 minute high and [0] 30 minute low > [=-1] 15 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews-01', 'buy-morning-volume-breakout(Check-News)-01', time_09_50, time_11_00)

        if (sb.nw >= time_09_50 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 2.5 and ( ( ( [=1] 15 minute high - [=-3] 2 hour low ) * 100 ) / 1 day ago close ) < 2 and [-1] 5 minute open > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute close > [-1] 5 minute open and [-1] 5 minute high > [-2] 5 minute high and [-1] 5 minute low > [-2] 5 minute low and [-1] 5 minute high < [=1] 10 minute high and [-1] 5 minute low > [=1] 10 minute low and [-1] 10 minute low > [=1] 10 minute low and [-1] 15 minute low > [=1] 10 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews', 'buy-morning-volume-breakout(Check-News)', time_09_50, time_11_00)


        time.sleep(5)
        sb.nw = datetime.now()

    sb.driver.quit()
    