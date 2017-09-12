import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from datetime import date, timedelta
import pytz
import pandas as pd

def initialize(context):
    
    # parameter setting begins
    context.lookback = 60              # this should be reasonably above SMAPeriod
    context.p_value_threshold = 0.01   #co-integration test
    context.SMAPeriod = 20            # pair bollinger band MA period
    context.StdDevDistance = 2.0        # upper/lower band std.dev. distance from SMA
    context.TP = 20                # target profit as percentage of pair value        
    context.SL = 10                # stop loss as percentage of pair value
    #parameter setting ends
    
    #context.PositionSize = 10        # pair trade position size            
    #context.pair_constant = 0.1        # pair constant(a) in Gold-a*Silver     
    
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.025,
                                              price_impact=0.1))
    set_commission(commission.PerShare(cost=0.0075, min_trade_cost=1.00))
    set_symbol_lookup_date('2017-01-01')
    
    context.index = symbol('SPY')

    context.symbols = [
        symbol('GLD'), 
        symbol('SLV')]
        
    # pair permutation    
    context.pairs = []
    s1 = symbol('GLD')
    s2 = symbol('SLV')
    context.pairs.append((s1, s2))
    #for i in range(len(context.symbols)-1):
    #    s1 = context.symbols[i]
    #    for j in range(i+1, len(context.symbols)):
    #        s2 = context.symbols[j]
    #        context.pairs.append((s1, s2))
    context.TPValue = 0.0
    context.SLValue = 0.0
    context.barCounter=0
    # schedule
    #schedule_function(check_pairs, 
    #                  date_rules.every_day(), 
    #                  time_rules.market_open(minutes=1))

    # runs every 15 min
    #total_minutes = 6*60 + 30
    #for i in range(10, total_minutes, 15):
    #    schedule_function(check_pairs, 
    #                      date_rules.every_day(), 
    #                      time_rules.market_open(minutes=i))

def coint_p_value(y, x):
    x = sm.add_constant(x)
    t_test, p_value, _ = coint(y, x)
    return p_value

def hedge_ratio(y, x):
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    return model.params[1]

def calc_target_pct(y_shares, x_shares, y_price, x_price):
    y_dollars = y_shares * y_price
    x_dollars = x_shares * x_price
    notional_dollars =  abs(y_dollars) + abs(x_dollars)
    y_target_pct = y_dollars / notional_dollars
    x_target_pct = x_dollars / notional_dollars
    return (y_target_pct, x_target_pct)


def before_trading_start(context, data):
    pass
    #create_pair_info(context, data)

    
def handle_data(context, data):
    #pass
    context.barCounter+=1
    if context.barCounter < context.lookback: return
    
    check_pairs(context, data)

    
def check_pairs(context, data):
    create_pair_info(context, data)
    if context.portfolio.positions_value==0 and len(get_open_orders())==0:
        check_pairs_for_entry(context, data)
    else:
        check_pairs_for_exit(context, data)    
    
    
def create_pair_info(context, data):    
    prices = data.history(context.symbols, "price", context.lookback, '1m')

    context.pair_info = {}
    for pair in context.pairs:
        try:
            s1, s2 = pair
            ys = prices[s1]
            xs = prices[s2]
            p_value = coint_p_value(ys, xs)
            hedge = hedge_ratio(ys, xs)
            spreads = ys - hedge*xs
            
            spreadsSMA = spreads.rolling(context.SMAPeriod).mean()
            spreadsSDEV = spreads.rolling(context.SMAPeriod).std()
            spreadsBBUPPER = spreadsSMA + context.StdDevDistance * spreadsSDEV
            spreadsBBLOWER = spreadsSMA - context.StdDevDistance * spreadsSDEV
            
            ok_to_short = (spreads[-1]>spreadsBBUPPER[-1])
            ok_to_long = (spreads[-1]<spreadsBBLOWER[-1])
            
            context.pair_info[pair] = {
                'p_value': p_value,
                'hedge': hedge,
                'spreads': spreads[-1],
                'spreadsBBUPPER': spreadsBBUPPER[-1],
                'spreadsBBLOWER': spreadsBBLOWER[-1],
                'ok_to_long': ok_to_long,
                'ok_to_short': ok_to_short
            }
        except Exception as e:
            log.warn('{} removed: {}'.format(pair, str(e)))

        
def check_pairs_for_entry(context, data):        
    pairs = []
    for pair, pair_info in context.pair_info.iteritems():
        if pair_info['p_value'] > context.p_value_threshold:
            continue
                
        y, x = data.current(pair, 'price')
        hedge = pair_info['hedge']
        target1, target2 = calc_target_pct(1, hedge, y, x)
        #target1 = context.PositionSize
        #target2 = max(int(target1*hedge),1)
        
        spreads = pair_info['spreads']
        ok_to_long = pair_info['ok_to_long']
        ok_to_short = pair_info['ok_to_short']
        
        s1, s2 = pair
        posDir = None
        if ok_to_long:
            pairs.append((s1, s2, target1, -target2, y, x, hedge))
            context.TPValue = spreads + (0.01*context.TP) * spreads
            context.SLValue = spreads - (0.01*context.SL) * spreads
            posDir = "Long"
        elif ok_to_short:
            pairs.append((s1, s2, -target1, target2, y, x, hedge))
            context.TPValue = spreads - (0.01*context.TP) * spreads
            context.SLValue = spreads + (0.01*context.SL) * spreads
            posDir = "Short"
      
    if len(pairs)>0:
        s1, s2, target1, target2, y, x, hedge = pairs[0]
        log.info('{} Enter: {} {} Equity1 Size: {} Equity2 Size: {} Equity1 Price: {} Equity2 Price: {} Pair Constant: {} Spread: {} TP: {} SL: {}'.format(posDir, s1, s2, target1, target2, y, x, hedge,spreads,context.TPValue, context.SLValue))
        #log.info('spread:{} BBupper:{}  BBlower: {}'.format(spreads,pair_info['spreadsBBUPPER'],pair_info['spreadsBBLOWER']))
        order_target_percent(s1, target1)
        order_target_percent(s2, target2)

        
def check_pairs_for_exit(context, data):
    for pair in context.pairs:
        s1, s2 = pair
        pos1 = context.portfolio.positions[s1].amount
        pos2 = context.portfolio.positions[s2].amount

        if pos1==0 and pos2==0:
            continue
         
        if pair not in context.pair_info:
            log.info('No pair info {} {}'.format(s1, s2))
            order_target_percent(s1, 0)
            order_target_percent(s2, 0)                
            continue
            
            
        pair_info = context.pair_info[pair]
        spreads = pair_info['spreads']

        s1, s2 = pair
        y, x = data.current(pair, 'price')
        if pos1>0 and pos2<0:
            if spreads > context.TPValue or spreads < context.SLValue: 
                order_target_percent(s1, 0)
                order_target_percent(s2, 0)
                log.info('Long Exit:{}{} Equity1 Price: {} Equity2 Price: {} Equity1 Size: {} Equity2 Size: {} Spread: {} TP: {} SL: {}'.format(s1, s2, y, x,pos1,pos2,spreads,context.TPValue, context.SLValue))
        elif pos1<0 and pos2>0:
            if spreads < context.TPValue or spreads > context.SLValue:
                order_target_percent(s1, 0)
                order_target_percent(s2, 0)
                log.info('Short Exit:{}{} Equity1 Price: {} Equity2 Price: {} Equity1 Size: {} Equity2 Size: {} Spread: {} TP: {} SL: {}'.format(s1, s2, y, x,pos1,pos2,spreads,context.TPValue, context.SLValue))
        