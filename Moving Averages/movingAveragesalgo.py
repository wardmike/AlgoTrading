def initialize(context):
    context.stocks= [sid(11224), sid(22215), sid(6683), sid(44125)]
    # Chosen stocks are decently volatile
    # To use more/ different stocks just type sid( and the stock's ticker )
                     
    
    # Set the allocation per stock
    pct_per_algo = 1.0 / len(context.stocks)
    
    # Make a separate algo for each stock.
    context.algos = [BuyLowSellHigh(stock, pct_per_algo) for stock in context.stocks]


def handle_data(context, data):
    # Call each individual algorithm's handle_data method
    for algo in context.algos:
        algo.handle_data(context,data)
        
        
        
# This is the original algo but it has been turned into its own class 
# with its own handle data method. Now you can create multiple instances of it.

class BuyLowSellHigh(object):
    
        
    # Initialize with a single stock and assign a proportion of the account.
    def __init__(self, security, pct_of_account):
        self.security = security
        self.pct = pct_of_account
        
    def handle_data(self, context, data):
        
        #average_price = data.history(self.security,3,'price','1d')
        average_price = data[self.security].mavg(7)
        current_price = data[self.security].price
        #current_price = data.current(self.security,'price')
                                     
        
        # Adjust the cash by the proportion allocated to this stock
        cash = context.portfolio.cash * self.pct
        # Objective to only buy when the stock is less than average
        # Sell only when higher than purchase price and average price * some gain

        if current_price < (average_price - average_price * .03) and cash > current_price: 
            #- (average_price * 1)) and cash > current_price:

            number_of_shares = int(cash / current_price)

            order(self.security, number_of_shares)
            log.info("Buying %s" % (self.security.symbol))

        elif (current_price > (average_price * 1.2)):
                    
            
            number_of_shares = int(cash / current_price)
            
            import time
          
            order_target(self.security, 0)
            log.info("Selling %s" % (self.security.symbol))
            
def initialize2(context):
    context.limit = 10
    
    schedule_function(rebalance,
                     date_rule = date_rules.every_day(),
                     time_rule = time_rules.market_open())
    
    
def rebalance(context, data):
    for stock in context.portfolio.positions:
        if stock not in context.fundamentals and stock in data:
            order_target_percent(stock, 0)
        
# Will be called on every trade event for the securities you specify. 
def before_trading_start(context, data):
    context.fundamentals = get_fundamentals(
        query(
            fundamentals.valuation_ratios.pb_ratio,
            fundamentals.valuation_ratios.pe_ratio,
        )
        .filter(
            fundamentals.valuation_ratios.pe_ratio < 14
        )
        .filter(
            fundamentals.valuation_ratios.pb_ratio < 2
        )
        .order_by(
            fundamentals.valuation.market_cap.desc()
        )
        #.limit(context.limit)
        )
    

    
    update_universe(context.fundamentals.columns.values)
    


def handle_data2(context, data):
    cash = context.portfolio.cash
    #current_positions = context.portfolio.positions
    
    for stock in data:
        current_position = context.portfolio.positions[stock].amount
        stock_price = data[stock].price
        plausible_investment = cash / context.limit
        stop_price = stock_price - (stock_price*0.095)
     
        share_amount = int(plausible_investment / stock_price)
        
        try:
            if stock_price < plausible_investment:
                if current_position == 0:
                    if context.fundamentals[stock]['pe_ratio'] < 11:
                        order(stock, share_amount, style=StopOrder(stop_price))
                    
                
            
        except Exception as e:
            print(str(e))
            
            
   