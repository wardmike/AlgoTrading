# For this example, we're going to write a simple momentum script.  When the 
# stock goes up quickly, we're going to buy; when it goes down quickly, we're
# going to sell.  Hopefully we'll ride the waves.

# To run an algorithm in Quantopian, you need two functions: initialize and 
# handle_data.

def initialize(context):
    context.fnv=sid(41886)#franco nevada corp
    context.rgld=sid(6455)#royal gold corp

def handle_data(context, data):
  
    cash = context.portfolio.cash    
    
    rgld_avg = data[context.rgld].mavg(5)
    fnv_avg = data[context.fnv].mavg(5)
    spread_avg = (rgld_avg - fnv_avg)/2.0#spread average
    
    rgld_curr = data[context.rgld].price
    fnv_curr = data[context.fnv].price
    spread_curr = (rgld_curr - fnv_curr)/2.0

    if spread_curr > spread_avg*1.10:
        order(context.rgld,-100)
        order(context.fnv,100)
    elif spread_curr < spread_avg*.90:
        order(context.rgld,100)
        order(context.fnv,-100)
    else:
        pass
