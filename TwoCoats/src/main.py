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
            "\'open-port\': Make a new portfolio\n" \
            "-------------------------------------------\n")
        return False
    elif(command == 'quit'):
        print('\n')
        return True
    
    elif(command == 'list-port'):
        print('\n')
        if (not portfolios):
            print("No existing portfolios.\n" \
            "Create one with \'make-port\'...\n")
            return False
        else:
            print('-------------------------------------------')
            for x in portfolios:
                print(x.name)
            print('-------------------------------------------\n')
            return False
        
    elif(command == 'open-port'):
        print('\n')
        return False
    
    elif(command == 'make-port'):
        print('\nWhat do you want to name this new portfolio?:\n')
        name = str(input())
        portfolios.append(portfolio(name,[]))
        print('\nPortfolio '+name+' successfully added!\n')
        return False
    
    else:
        print('Invalid Command')
        return False
    
class portfolio:
    def __init__(self, name, stocks):
        self.name = name
        self.stocks = []

class stock:
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price
    

main()
