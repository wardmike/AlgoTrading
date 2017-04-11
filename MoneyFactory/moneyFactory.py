"""
MoneyFactory - algorithm by Michael Ward in USU Investment Club.
"""
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.filters.morningstar import Q1500US
 
def initialize(context):

    context.aapl = sid(24)

    context.bought_aapl = False

    """
    Called once at the start of the algorithm.
    """   
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))
     
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())
     
    # Create our dynamic stock selector.
    attach_pipeline(make_pipeline(), 'my_pipeline')
         
def make_pipeline():
    """
    A function to create our dynamic stock selector (pipeline). Documentation on
    pipeline can be found here: https://www.quantopian.com/help#pipeline-title
    """
    
    # Base universe set to the Q500US
    base_universe = Q1500US()

    # Factor of yesterday's close price.
    yesterday_close = USEquityPricing.close.latest
     
    pipe = Pipeline(
        screen = base_universe,
        columns = {
            'close': yesterday_close,
        }
    )
    return pipe
 
def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = pipeline_output('my_pipeline')
  
    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index
 
def handle_data(context,data):
    #
    curr_aapl_price = data.current(context.aapl,"price")

    price_hist_aapl = data.history(context.aapl, 'price', 5, '1d')
    mavg_aapl_5 = price_hist_aapl.mean()

    if(curr_aapl_price > mavg_aapl_5 and price_hist_aapl[3] < mavg_aapl_5 and (not context.bought_aapl)):
        order(context.aapl, 100)
    elif (curr_aapl_price < mavg_aapl_5 and price_hist_aapl[3] > mavg_aapl_5):
        order(context.aapl, -100)
    else:
        pass
