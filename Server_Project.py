# Server
import socket
import threading
import time
import random

# Define constants
HOST = '127.0.0.1'  # Localhost using the loopback address referring to the local client and assuming the clients are on the same machine as the server
PORT = 5000  # Choose a port number
NUM_PLAYERS = 2  # Number of players in the game, we are working with 2 players
NUM_ROUNDS = 3 # Number of rounds in the game
total_round_counter = 0 # Counter that counts the value of all the rounds of all the players
barrier = threading.Barrier(NUM_PLAYERS) # A barrier that helps us keep the game synchronized for both players
print_lock = threading.Lock() # A print lock for redundancy in printing
cumulative_score = [0, 0] # Cumulative score list of both players

# Define a function to handle each client connection     ### Hoda wrote the initial server code and everyone took part in debugging it
def handle_client(connection, player_id):
    scores = []  # List to store scores for each player
    global NUM_PLAYERS, total_round_counter # Global variables rather than local to be able to use outside the function
    welcome_msg = "Welcome to the game!" # Convert the string to bytes and send
    connection.send(welcome_msg.encode())
    
    time.sleep(1) # Delay because sometimes the random number is sent with the string itself
    barrier.wait() # Barrier to make both players start together the game together
    while True:
        
        barrier.wait() # Barrier to make the player stay on the current round until both players have finished
        try:
            # Generate a random number and send it to player
            random_number = str(random.randint(0, 9)).encode()
            connection.send(random_number)
            
            # Receive player input and calculate RTT
            start_time = time.time()  # Get the start time
            player_input = connection.recv(1024)
            end_time = time.time()    # Get the end time
            rtt = end_time - start_time # Calculate the RTT
            
            # Check if the player's input is correct and if it is correct append his score to his scores list and add the score to his cumulative score
            if player_input == random_number:
                score = rtt
                scores.append(score)
                x = cumulative_score[player_id-1]
                cumulative_score[player_id-1] = x + score
                
            # If the input is not correct disqualify the player and give him a score equal to the timeout
            elif player_input == b"quit": ## The quit conditions were added by Shafik and Mahdi
                quitmessage = "You have quitted the game and lost"
                connection.send(quitmessage.encode())
                if player_id == 1:
                    print("Player 2 wins")
                else:
                    print("Player 1 wins")
                connection.close()
                return
            else:
                score = 20
                scores.append(score)
                x = cumulative_score[player_id-1]
                cumulative_score[player_id-1] = x + score
                disq = "You are disqualified from this round because you entered a wrong number."
                connection.send(disq.encode())
            
            results[player_id-1] =  scores
            total_round_counter +=1
            
            # Only print on even number of total rounds which means both players have finished
            # Abed contributed this part 
            if total_round_counter%NUM_PLAYERS == 0: 
                    with print_lock:  
                        i = len(scores) - 1
                        print("Round %d scores:" % len(scores)) ## These conditions are put to make sure to print the scores in descending order
                        if results[0][i] > results[1][i]:
                            print("1. Player 1: %.2f seconds" % results[0][i])
                            print("2. Player 2: %.2f seconds" % results[1][i])
                        elif results[0][i] < results[1][i]:
                            print("1. Player 2: %.2f seconds" % results[1][i])
                            print("2. Player 1: %.2f seconds" % results[0][i])
                        print("Cumulative scores:")
                        if cumulative_score[0] > cumulative_score[1]:
                            print("1. Player 1: %.2f seconds" % cumulative_score[0])
                            print("2. Player 2: %.2f seconds\n" % cumulative_score[1])
                        else:
                            print("1. Player 2: %.2f seconds" % cumulative_score[1])
                            print("2. Player 1: %.2f seconds\n" % cumulative_score[0])
                        if total_round_counter == 6:
                            if cumulative_score[0] > cumulative_score[1]:
                                print("The Winner Is Player 2!")
                            elif cumulative_score[0] < cumulative_score[1]:
                                print("The Winner Is Player 1!")
            
            barrier.wait() # Barrier so that the game ends together
            # End the players game when he reaches 3 rounds
            if len(scores) == NUM_ROUNDS:  ## Mahdi and shafik wotte this and abed debugged it
                if cumulative_score[0] > cumulative_score[1]:
                    winner_message = "The Winner Is Player 2!"
                    connection.send(winner_message.encode())
                elif cumulative_score[0] < cumulative_score[1]:
                    winner_message = "The Winner Is Player 1!"
                    connection.send(winner_message.encode())
                end_message = "The Game Has Ended!"
                time.sleep(0.1)
                connection.send(end_message.encode())
                connection.close()
                results[player_id-1] =  scores
                break
        except ConnectionResetError: ## The error handling was contributed by Mahdi and debugged by shafik
            print("Player", player_id, "got disconnected")
            if player_id == 1:
                print("Player 2 is the winner")
                connection.close()
                return
            else:
                print("Player 1 is the winner")
                connection.close()
                return
# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", PORT))
server_socket.listen(NUM_PLAYERS)

# Wait for all players to connect
print("Waiting for players to join...")
### Hoda wrote this part then it was edited by Mahdi and Shafik

results = [ [] for i in range(NUM_PLAYERS)]
for k in range(NUM_PLAYERS):
    connection, addr = server_socket.accept()
    player_id = k + 1
    k +=1
    print("Player %d connected from %s:%d" % (player_id, addr[0], addr[1]))
    t = threading.Thread(target=handle_client, args=(connection, player_id)) #We use the handle_client function which uses threading so that it executes concurrently which allows the server to accept new clients while handling existing clients at the same time
    t.start()
t.join()


