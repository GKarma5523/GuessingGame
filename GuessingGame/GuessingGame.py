import pyodbc
import uuid
import random

server = 'wsu-cs3550.westus2.cloudapp.azure.com'
database = 'garrettkuns'
username = 'garrettkuns'
password = 'duck.queens.ages'

connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                            server + ';DATABASE=' + database +
                            ';UID=' + username + ';PWD=' + password)

cursor = connection.cursor()

cursor.execute("SELECT @@version;")
row = cursor.fetchone()

# Game State
numToGuess = 0
guessAttempts = 0
gameKey = ''
shouldPlayAgain = False

# Game Loop
def game():
  while True:
    generateGame()
    while playerGuess():
      pass
    showSummary()
    showStats()
    playAgain()
    if shouldPlayAgain:
      continue
    else:
      break

# Create a game
def generateGame():
  global numToGuess
  numToGuess = random.randint(1, 100)

  print('Enter your name: ');
  name = input();

  cursor.execute("EXEC dbo.InsertGame @PlayerName = ?, @NumToGuess = ?", name, numToGuess)
  connection.commit()

  cursor.execute("SELECT TOP 1 GameKey FROM dbo.Game ORDER BY DatePlayed DESC")
  row = cursor.fetchone()

  global gameKey
  gameKey = row[0]

# Show game summary
def showSummary():
  print('Summary =================================================')
  cursor.execute("SELECT TOP 1 * FROM Summary ORDER BY DatePlayed DESC")
  row = cursor.fetchone()

  print('Player Name: ' + row[0])
  print('Time played: ' + str(row[1]))
  print('Number to guess: ' + str(row[2]))
  print('Number of guesses: ' + str(row[3]))
  print('');

# Show game stats
def showStats():
  print('Stats ==================================================')
  cursor.execute("SELECT * FROM Stats ORDER BY MedianGuesses")
  row = cursor.fetchone()
  print('Games Played: ' + str(row[0]))
  print('Avg Number of Guesses: ' + str(row[1]))
  print('Median Guesses: ' + str(row[2]))
  print('');

# Ask if player wants to play again
def playAgain():
  print('Do you want to play again? (y/n)')
  playAgain = input()

  global shouldPlayAgain

  if (playAgain == 'y'):
    shouldPlayAgain = True
  else:
    shouldPlayAgain = False

# Have player enter a guess
def playerGuess():
  global numToGuess

  print('Guess a number between 1 - 100 or q to exit: ')
  guess = input()

  if guess == 'q':
    print('Quitting game')
    return False

  else:
    try:
      guess = int(guess)

      global guessAttempts
      guessAttempts += 1

    except:
      print('Invalid input')
      return True

    if guess == numToGuess:
      print('Correct!')
      print('You guessed in ' + str(guessAttempts) + ' attempts')

      cursor.execute("EXEC dbo.InsertGuess @GuessValue = ?, @GuessAttempt = ?, @GameKey = ?", guess, guessAttempts, gameKey)
      connection.commit()

      return False
    elif guess > numToGuess:
      print('Too high')
      cursor.execute("EXEC dbo.InsertGuess @GuessValue = ?, @GuessAttempt = ?, @GameKey = ?", guess, guessAttempts, gameKey)
      connection.commit()

      return True
    else:
      print('Too low')
      cursor.execute("EXEC dbo.InsertGuess @GuessValue = ?, @GuessAttempt = ?, @GameKey = ?", guess, guessAttempts, gameKey)
      connection.commit()

      return True

# Start the game
game()