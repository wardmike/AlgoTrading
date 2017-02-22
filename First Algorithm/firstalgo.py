"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.filters.morningstar import Q500US
 
def initialize(context):
    print "hello world"
    print "context: ", context
    context.aapl = sid(24)
    context.goog = sid(46631)
    context.fb = sid(42950)
    print "new context: ", context
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
    base_universe = Q500US()

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
     
def my_assign_weights(context, data):
    """
    Assign weights to securities that we want to order.
    """
    pass #means to be written later
 
def my_rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    pass
 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass
 
def handle_data(context,data):
    """
    Called every minute.
    """
    print context.aapl
    print context.goog
    curr_aapl_price = data.current(context.aapl, "price")
    curr_goog_price = data.current(context.goog, "price")
    print "curr aapl: ", curr_aapl_price
    print "curr goog: ", curr_goog_price
    
    
    price_hist = data.history(context.aapl, 'price', 5, '1d')
    mavg_aapl_5 = price_hist.mean()
    
    price_hist = data.history(context.goog, 'price', 5, '1d')
    mavg_goog_5 = price_hist.mean()
    
    print "mavg_aapl_5: ", mavg_aapl_5
    print "mavg_goog_5: ", mavg_goog_5
    
    print price_hist
    print price_hist[0]
    print price_hist[1]
    print price_hist[2]
    
    if (curr_aapl_price > mavg_aapl_5 and price_hist[4] < mavg_aapl_5):
        order(current.aapl, 100)
    elif(curr_aapl_price < mavg_aapl_5 and price_hist[4] > mavg_aapl_5):
        order(current.aapl, -100)
    else:
        pass