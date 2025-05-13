def main():
    print("\n\nHello! Welcome to stonks.\n")
    end = False
    portfolios = []
    while (not end):
        end = prompt(portfolios)
    return 0

def prompt(portfolios):
    print("Enter a command. | (\'help\' for list of commands):\n")
    command = str(input()).lower()
    if(command == 'help'):
        print("-------------------------------------------"\
            "\n\'help\': Prints list of commands\n" \
            "\'quit\': Exit the program\n" \
            "\'list-port\': Prints list of portfolios\n" \
            "\'make-port\': Make a new portfolio\n" \
            "\'buy\': Buy shares of a stock\n" \
            "\'sell\': Sell shares of a stock\n" \
            "-------------------------------------------\n")
        return False
    

    elif(command == 'quit'):
        print('\n')
        return True
    

    elif(command == 'list-port'):
        if (not portfolios):
            print("\nNo existing portfolios.\n" \
            "Create one with \'make-port\'...\n")
            return False
        else:
            print_existing_portfolios(portfolios)
            return False
        
    
    elif(command == 'make-port'):
        print('\nWhat do you want to name this new portfolio?:\n')
        name = str(input())
        portfolios.append(portfolio(name))
        print('\nPortfolio '+name+' successfully added!\n')
        return False
    

    elif(command == 'buy'):
        if (not portfolios):
            print("\nNo existing portfolios.\n" \
            "Create one with \'make-port\'...\n")
            return False
        
        print_existing_portfolios(portfolios)
        print('\nWhich portfolio do want to use to buy?:')
        matching_port = None
        while (not matching_port):
            matching_port =  portfolio_by_name(str(input()),portfolios)
            print ('\nInvalid portfolio name.')
            print_existing_portfolios(portfolios)
        
        to_buy = stock("COST",1016.15)
        print("How many shares of "+to_buy.symbol+" would you like to buy?")
        shares = int(input())
        if(shares*to_buy.price <= matching_port.money):
            stonk = stock_by_symbol(to_buy.symbol,matching_port.stocks)
            if(stonk == None):
                matching_port.stocks.append(stock(to_buy.symbol,to_buy.price))
                stonk = stock_by_symbol(to_buy.symbol,matching_port.stocks)
            stonk.shares += shares
            matching_port.money -= (shares*to_buy.price)
            print("Successfully bought "+str(shares)+" of "+to_buy.symbol+" at $"+str(to_buy.price))
        else:
            print("Insufficient funds.\n")
        return False
    else:
        print('Invalid Command')
        return False
    
class portfolio:
    def __init__(self, name):
        self.name = name
        self.stocks = []
        self.money = 5000

class stock:
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price
        self.shares = 0
    
def print_existing_portfolios(portfolios):
    print("Existing Portfolios:")
    print('-------------------------------------------')
    for x in portfolios:
        print(x.name)
    print('-------------------------------------------\n')
    return

def portfolio_by_name(name,portfolios):
    for port in portfolios:
        if port.name == name:
            return port
    return None

def stock_by_symbol(symbol,stocks):
    for stonk in stocks:
        if stonk.symbol == symbol:
            return stonk
    return None

main()
