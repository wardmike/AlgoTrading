# For this example, we're going to write a simple momentum script.  When the 
# stock goes up quickly, we're going to buy; when it goes down quickly, we're
# going to sell.  Hopefully we'll ride the waves.

# To run an algorithm in Quantopian, you need two functions: initialize and 
# handle_data.

def initialize(context):
    context.apple = sid(4297)

def handle_data(context, data):
    
    stocks = [context.apple]
    
    cash = context.portfolio.cash    
    stock_data = data[stocks[0]]
    print "stock_data: ", stock_data

    average_price = stock_data.mavg(5)
    current_price = stock_data.price

    if current_price > average_price and cash > current_price:      
        number_of_shares = int(cash/current_price)
        order(stocks[0], number_of_shares)
    elif current_price < average_price:
        number_of_shares = context.portfolio.positions[stocks[0].sid].amount
        order(stocks[0], -number_of_shares)

