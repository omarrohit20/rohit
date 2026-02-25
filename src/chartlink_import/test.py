import pathlib
import sbase as sb
from config import *
from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    
    # Initialize Playwright
    with sync_playwright() as p:
        # Launch browser with persistent context (for user data directory)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(script_directory / "profiles" / "p6"),
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu'
            ]
        )
        
        # Create a page from the context
        page = context.new_page()
        
        # Store page and context in sbase for functions to use
        sb.driver = page
        sb.context = context
        
        print('Started')
        sb.nw = datetime.now()

        if (sb.nw >= time_00_15 and sb.nw <= time_24_00):
            process_url_volBreakout('https://chartink.com/screener/morning-volume-bs', 'morning-volume-bs', time_09_00,
                                     time_10_00)
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-1', 'morning-volume-breakout-buy', time_09_15, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'Breakout-Beey-2', time_09_30, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-dayconsolidation-breakout-04', 'buy-breakout', time_10_00, time_11_45)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-1', 'morning-volume-breakout-sell', time_09_15, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-2', 'Breakout-Siill-2',
                                     time_09_30, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-breakout',
                                     time_10_00, time_11_45)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-check-morning-down-breakup-01','buy-check-morning-down-breakup-02', time_09_35, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'supertrend-morningdown-buy', time_10_00, time_11_45)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-check-morning-down-breakup-02','buy-check-morning-down-breakup-02', time_09_45, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-consolidation-01',
                                         'buy-dayconsolidation-breakout-01', time_10_15, time_12_30)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-consolidation-02',
                                         'buy-dayconsolidation-breakout-03', time_09_45, time_11_30)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-breakup-intraday-9-25-to-10-30-06',
                                         '1-Bbuyy-morningUp-downConsolidation', time_10_15, time_11_30)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-3',
                                         'Breakout-Buy-after-10', time_09_40, time_11_30)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews',
                                         'buy-morning-volume-breakout(Check-News)', time_09_50, time_12_30, dropDB=True)
            #
            process_url_volBreakout('https://chartink.com/screener/supertrend-morning-buy', 'supertrend-morning-buy', time_09_40, time_12_00)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-0', '09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', time_09_25, time_12_00)
            # # ( {33489} ( ( {cash} ( [=1] 15 minute high > [=-1] 3 hour high and [-1] 5 minute high > [=1] 10 minute high and ( ( ( [-1] 5 minute close - [=2] 5 minute high ) * 100 ) / 1 day ago close ) > 0.3 and ( ( ( [-1] 5 minute close - [=1] 5 minute high ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 1 day ago close ) > -0.1 and ( ( ( 2 days ago close - 3 days ago close ) * 100 ) / 2 days ago open ) > -1 and ( ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago open ) > -2 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1.3 and ( ( ( [=1] 5 minute open - 1 day ago low ) * 100 ) / 1 day ago close ) < 2.5 and ( ( ( [=1] 5 minute open - 2 days ago close ) * 100 ) / 1 day ago close ) < 2 and ( ( ( [=1] 5 minute open - 3 days ago close ) * 100 ) / 1 day ago close ) < 2 and ( ( ( [=1] 5 minute low - [=-1] 15 minute low ) * 100 ) / 1 day ago close ) > -0.3 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > -0.7 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [=1] 15 minute close - [=2] 30 minute low ) * 100 ) / 1 day ago close ) < 0.5 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-1', '09_30:checkChartBuy', time_09_25, time_10_15)
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-1', '09_30:checkChartBuy', time_11_00, time_12_00)
            #
            process_url_volBreakout('https://chartink.com/screener/buy-breakup-intraday-9-30-to-10', 'crossed-day-high', time_09_20, time_13_00)
            #
            #
            #
            #
            process_url_volBreakout('https://chartink.com/screener/temp-rohit-2', 'temp-rohit', time_09_20, time_12_00)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-1-2', 'week2lh-not-reached', time_09_45, time_11_00)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-2', 'supertrend-morningup-sell',
                                         time_10_00, time_11_45)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-check-morning-up-breakdown-02',
                                         'sell-check-morning-up-breakdown-02', time_09_45, time_11_15)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-consolidation-01',
                                         'sell-dayconsolidation-breakout-01', time_10_15, time_12_30)
            #
            process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-consolidation-02',
                                         'sell-dayconsolidation-breakout-03', time_10_00, time_11_30)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-04',
                                         '1-Sselll-morningDown-upConsolidation', time_10_15, time_11_30)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-after10',
                                         'Breakout-Sell-after-10', time_09_40, time_11_30)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-morning-volume-breakout-checknews', 'sell-morning-volume-breakout(Check-News)', time_09_50, time_12_30, dropDB=True)
            #
            process_url_volBreakout('https://chartink.com/screener/supertrend-morning-sell', 'supertrend-morning-sell', time_09_40, time_12_00)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', '09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', time_09_25, time_12_00)
            #
            # # ( {33489} ( ( {cash} ( [=1] 15 minute low < [=-1] 3 hour low and [-1] 5 minute low < [=1] 10 minute low and [=1] 5 minute high >= [=1] 1 hour high and ( ( ( [-1] 5 minute close - [=2] 5 minute low ) * 100 ) / 1 day ago close ) < -0.3 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 1 day ago close ) < 0.1 and ( ( ( 2 days ago close - 3 days ago close ) * 100 ) / 2 days ago open ) < 1 and ( ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago open ) < 2 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.3 and ( ( ( [=1] 5 minute close - 1 day ago high ) * 100 ) / 1 day ago close ) > -2.5 and ( ( ( [=1] 5 minute close - 2 days ago close ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [=1] 5 minute close - 3 days ago close ) * 100 ) / 1 day ago close ) > -2 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < 0.7 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > -0.5 and ( ( ( [=1] 15 minute close - [=2] 30 minute high ) * 100 ) / 1 day ago close ) > -0.5 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-1', '09_30:checkChartSell', time_09_25, time_12_00)
            #
            process_url_volBreakout('https://chartink.com/screener/sell-breakdown-intraday-9-30-to-10-3', 'crossed-day-low', time_09_20, time_13_00)



        print('Hello')
        time.sleep(10)

        #if (sb.nw >= time_10_00 and sb.nw <= time_24_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close ) > 1.1 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute open ) < 2 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute open ) > 0.75 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( 1 day ago close - 3 days ago close ) * 100 ) / 1 day ago close ) < 6 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) < 3 and [0] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > -0.3 and [0] 5 minute high < [=1] 15 minute high and [=1] 15 minute low < 1 day ago high and [=2] 15 minute low > [=-1] 15 minute high ) ) ) )
            #process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-02', 'test_process_url', time_09_00, time_15_30)

        # Close Playwright resources
        # page.close() is automatic when exiting the with block

