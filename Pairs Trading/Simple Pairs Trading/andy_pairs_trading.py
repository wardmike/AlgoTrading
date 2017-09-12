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

    if spread_curr > spread_avg*1.10:#detect a wide spread
        order(context.rgld,-100)
        order(context.fnv,100)
    elif spread_curr < spread_avg*.90:#detect a tight spread
        order(context.rgld,100)
        order(context.fnv,-100)
    else:
        pass