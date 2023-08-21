import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p2")
    sb.option.add_argument('--headless=new')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_11_00):
        if (sb.nw >= time_09_40 and sb.nw <= time_11_30):
            # ( {cash} ( ( {cash} ( abs ( [-1] 5 minute close - [-1] 5 minute sma ( [-1] 5 minute close , 200 ) * 100 ) / [-1] 5 minute close > 3.5 and abs ( [=-1] 5 minute close - [=-1] 5 minute sma ( [=-1] 5 minute close , 200 ) * 100 ) / [-1] 5 minute close < 2 and [=-5] 2 hour high >= 2 days ago "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" and abs ( [-1] 5 minute close - [0] 5 minute open * 100 ) / [-1] 5 minute close < 2 and abs ( [-1] 5 minute close - [-2] 5 minute open * 100 ) / [-1] 5 minute close < 2 and abs ( [-1] 5 minute close - [-1] 5 minute open * 100 ) / [-1] 5 minute close < 1 and [-1] 5 minute volume > [=1] 5 minute volume and [-1] 5 minute volume > [=2] 5 minute volume and [-1] 5 minute volume > [=3] 5 minute volume and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 2 and [0] 5 minute close > 50 and [0] 5 minute close < 3000 and market cap > 1000 ) ) ) )
            process_url('https://chartink.com/screener/buy-ema-up0', 'buy-sma200-up', time_09_40, time_11_30)

        if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close and ( ( ( [=2] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0.1 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) < 6 and 1 day ago close > 3 days ago close and [=1] 5 minute open < 1 day ago high and [=2] 30 minute low > 2 days ago high and ( {cash} ( [=2] 5 minute high > [=1] 5 minute high and [-1] 5 minute high > [=3] 5 minute close and [-1] 5 minute high > [=3] 5 minute open and [-1] 5 minute high > [=1] 5 minute open and [-1] 5 minute high > [=1] 5 minute close and [-1] 5 minute low > [-1] 5 minute vwap ) ) ) ) ) )
            process_url('https://chartink.com/screener/morning-volume-breakout-1-2', '$buy-morning-up-volume-breakout', time_09_45, time_10_15)


        if (sb.nw >= time_09_40 and sb.nw <= time_10_00):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and [=1] 30 minute high > 1 day ago close and [=1] 30 minute high = [=1] 20 minute high and [-1] 5 minute vwap < [-3] 5 minute vwap and [=1] 5 minute close > [=1] 5 minute open and [=2] 5 minute close > [=1] 5 minute open and [=2] 5 minute open > [=1] 5 minute open and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [-1] 5 minute close - [=-1] 5 minute high ) * 100 ) / 1 day ago close ) > 1.2 and ( ( ( [-1] 5 minute close - [=1] 5 minute high ) * 100 ) / 1 day ago close ) < -0.75 and ( ( ( [=1] 1 hour low - [=-1] 5 minute high ) * 100 ) / 1 day ago close ) > -1.5 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > 0 ) ) ) )
            process_url('https://chartink.com/screener/buy-breakup-intraday-9-25-to-10-30-06', '$buy-morningUp-downConsolidation', time_09_40, time_10_00)

        if (sb.nw >= time_09_20 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 0.5 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" < 0 and 3 days ago "close - 1 candle ago close / 1 candle ago close * 100" < 0 and ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago open < -1 and ( ( 3 days ago close - 3 days ago open ) * 100 ) / 3 days ago open < -1.5 and ( ( 1 day ago close - 4 days ago close ) * 100 ) / 3 days ago close < -3 and ( ( 1 day ago close - 3 days ago open ) * 100 ) / 3 days ago open < -3 and abs ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago open > 0.5 and 1 day ago low < 2 days ago low and [0] 5 minute high > 1 day ago high ) ) ) )
            process_url('https://chartink.com/screener/buy-downtrend-01', 'downlast3day: $buy-lastDayDoji/buy-first10minuteHigh-below-2-day-ago-close/SELL-first10minuteHigh-gt-2day-ago-close/)', time_09_25, time_10_30)


        # if (sb.nw >= time_10_30 and sb.nw <= time_13_15):
        # ( {57960} ( ( {cash} ( ( latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" - [=1] 15 minute high ) < ( [=1] 15 minute high - latest "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" ) and ( latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" - [-1] 5 minute high ) > ( [-1] 5 minute high - latest "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" ) and [=1] 1 hour low < [=1] 15 minute low and [=1] 2 hour low < latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago high)" and [-1] 5 minute high > latest "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > 0.5 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > 0.5 and ( latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" - latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago high)" ) * 100 / latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago high)" > 2 ) ) ) )
        # process_url('https://chartink.com/screener/buy-ema-up1', 'buy-ema-up1', time_10_30, time_13_15)

        #time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    