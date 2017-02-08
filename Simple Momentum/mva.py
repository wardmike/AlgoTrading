# For this example, we're going to write a simple momentum script.  When the 
# stock goes up quickly, we're going to buy; when it goes down quickly, we're
# going to sell.  Hopefully we'll ride the waves.

# To run an algorithm in Quantopian, you need two functions: initialize and 
# handle_data.

def initialize(context):
    context.apple = sid(24)
    context.yhoo = sid(14848)

def handle_data(context, data):
    
    stocks = [sid(24),sid(14848)]
    for stock in stocks:
        print "stock: ", stock
        cash = context.portfolio.cash
        stock_data = data[stock]
        print "stock_data: ", stock_data
        
        
        average_price = data[context.apple].mavg(5)
        print "average price: ",average_price
        average_price = stock_data.mvag(5)
        current_price = stock_data.price
        
        if current_price > average_price and cash > current_price:      
            number_of_shares = int(cash/current_price)
            order(stock, number_of_shares)
        elif current_price < average_price:
            number_of_shares = context.portfolio.positions[stock.sid].amount
            order(stock, -number_of_shares)