# User Stories and Exceptions

User stories for our CSC365 project focused on providing a place to learn about stock market trading in a safe, educational environment.

## User Stories
1. As a new user, I want to be able to create a personalized user so that I can save my lessons/ trades.
   
2. As a first-time investor, I want to learn about stock trends risk-free so that I don't lose money. 

3. As a user, I want to create a personal watchlist of stocks so that I can easily track my favorite assets over time.

4. As a user, I want to simulate a portfolio based on historical data so that I can practice trading strategies without financial risk.

5. As a student, I want to access educational examples or sample queries so that I can learn how to use the API more effectively.

6. As a returning user, I want to have a watchlist and notes so that I can revisit my learning progress across sessions.

7. As a teacher, I want to set up a portfolio with investments of my suggestion to show them the results of my strategies without showing them my real money. I wouldn't want to be putting my personal money into a new portfolio (that mirrors what I already do) every time a new quarter comes around either.

8. As a parent, I want my children to learn about investing and develop an investment strategy that suits their risk tolerance the best.

9. As a fund manager of a recently established mutual fund, I want to be able to monitor how potential/new hires will handle our customers' money. By seeing if their investment strategies align with our customers' goals, this will give me a better sense of whether they would be a good hire or not. If I see potential, I can also give my personal insight on what can be improved.

10. As a learning investor, I want to be able to create an fake-investing portfolio so I can get a feel for what it's like to have a real investment portfolio

11. As a frequent user, I want to be able to access my portfolio in a secure way so I can easily see the progress of my fake-investment portfoloio

12. As a learning investor, I want this service to follow all the same protocols that a normal investing service would (PDT rule, market open & close times) so that I have a more seamless tranistion to a real investment portfolio


## Exceptions and Error Scenarios

<strong>Exception 1:</strong> Invalid API key or token<br>
If a user provides an invalid or expired API token, the system will return an error with a message asking them to log in again or generate a new token.

<strong>Exception 2:</strong> User tries to access another user's data<br>
If a user attempts to access another user’s watchlist or notes, the system will deny access.

<strong>Exception 3:</strong> User adds a duplicate stock to watchlist<br>
If a stock already exists in the user's watchlist, the system will inform the user: “This stock is already in your watchlist.”

<strong>Exception 4:</strong> Invalid input format<br>
If a user submits malformed input, the API will return a Bad Request error with a message: “Invalid request format. Please check your input.”

<strong>Exception 5:</strong> User tries to register with existing email/username<br>
If the user attempts to register with an already used email or username, they’ll receive a message: “That email is already associated with an account.

<strong>Exception 6:</strong> User runs out of virtual money to trade<br>
An error will be thrown that notifies the user of their unsufficient funds. Gives the option to reset their entire portfolio (and funds to default value), or to keep using their current portfolio.

<strong>Exception 7:</strong> User attempts to buy amount of shares that exceeds their current funds<br>
An error will thrown that notifies the user of their unsufficient funds and will decline the purchase. Notifies the user of the maximum amount of shares they can buy with their current funds.

<strong>Exception 8:</strong> User tries to sell amount of shares that exceeds the amount they currently have<br>
An error will be thrown that notifies the user that they cannot sell more shares of a stock than they currently have. Rejects the user's request.
