# User Stories and Exceptions

User stories for our CSC365 project focused on providing a place to learn about stock market trading in a safe, educational environment.

## User Stories
1. As a new user, I want to be able to create a personalized user so that I can save my lessons/ trades.
   
2. As a first-time investor, I want to learn about stock trends risk-free so that I don't lose money. 

3. As a user, I want to create a personal watchlist of stocks so that I can easily track my favorite assets over time.

4. As a user, I want to simulate a portfolio based on historical data so that I can practice trading strategies without financial risk.

5. As a student, I want to access educational examples or sample queries so that I can learn how to use the API more effectively.

6. As a returning user, I want to have a watchlist and notes so that I can revisit my learning progress across sessions.



## Exceptions and Error Scenarios

Exception 1: Invalid API key or token
If a user provides an invalid or expired API token, the system will return an error with a message asking them to log in again or generate a new token.

Exception 2: User tries to access another user's data
If a user attempts to access another user’s watchlist or notes, the system will deny access.

Exception 3: User adds a duplicate stock to watchlist
If a stock already exists in the user's watchlist, the system will inform the user: “This stock is already in your watchlist.”

Exception 4: Invalid input format 
If a user submits malformed input, the API will return a Bad Request error with a message: “Invalid request format. Please check your input.”

Exception 5: User tries to register with existing email/username
If the user attempts to register with an already used email or username, they’ll receive a message: “That email is already associated with an account.
