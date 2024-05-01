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
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [0] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.6 and ( ( ( [=1] 15 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.3 and ( ( ( [0] 5 minute high - [=-1] 5 minute high ) * 100 ) / [=1] 5 minute open ) > 0 and ( ( ( [=1] 15 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_00, time_09_45)

        if (sb.nw >= time_09_20 and sb.nw <= time_11_00):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [0] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.6 and ( ( ( [=1] 15 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.3 and ( ( ( [0] 5 minute high - [=-1] 5 minute high ) * 100 ) / [=1] 5 minute open ) > 0 and ( ( ( [=1] 15 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and latest "close - 1 candle ago close / 1 candle ago close * 100" > 1.3 and ( ( ( [0] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 1.3 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'Breakout-Buy-2', time_09_25, time_12_30)

        if (sb.nw >= time_09_40 and sb.nw <= time_11_00):
            #( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and abs ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > 1.6 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 2 and [-1] 5 minute open > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute high > [-2] 5 minute high and [0] 30 minute low > [=-1] 15 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews-01', 'buy-morning-volume-breakout(Check-News)-01', time_09_50, time_11_00)

        if (sb.nw >= time_09_50 and sb.nw <= time_11_00):
            # ({33489}(({cash}([=1] 5 minute volume > greatest(  1 day ago volume/ 24) and (
            #             (([-1] 5 minute close - 1 day ago close) * 100) / 1 day ago close) > 0.75 and (
            #                      (([-1] 5 minute close - 1 day ago close) * 100) / 1 day ago close) < 2.5 and [-1]
            #  5 minute open >[=1] 10 minute open and[-1] 5 minute close >[=1] 10 minute open and[-1] 5 minute close >[-1] 5 minute open and[-1] 5 minute high >[-2] 5 minute high and[-1] 5 minute low >[-2] 5 minute low and[-1] 5 minute high <[=1] 10 minute high and[-1] 5 minute low >[=1] 10 minute low and[-1] 10 minute low >[=1] 10 minute low and[-1] 15 minute low >[=1] 10 minute low) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews', 'buy-morning-volume-breakout(Check-News)', time_09_50, time_11_00)


        time.sleep(10)
        sb.nw = datetime.now()

    sb.driver.quit()
    