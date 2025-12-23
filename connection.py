import tkinter as tk
from tkinter import Button
import json
# Get answers from NYT connection game


ROOT = tk.Tk() # Creates tkinter window
DB = "answers.txt" # Local database for all games

# Takes all the lines from the DB
def get_games():
    games = []
    with open(DB, "r") as file:
        for line in file:
            games.append(json.loads(line))
    return games

GAMES = get_games() # All games

# Class that stores the main game logic
class Connections:
    __slots__ = ["__game", "__guesses", "__all_groups", "__starting", "__chosen", "__buttons", "__label"]

    # chosen            An empty set that stores the words previously clicked
    # label             The label used to show information to the user
    # game_id           The number line from the DB that is displayed
    def __init__(self, chosen:set, label:tk.Label, game_id:int):
        self.__game = GAMES[game_id]
        self.__guesses = 4
        self.__all_groups = self.__game["groups"]
        self.__starting = self.__game["startingGroups"]
        self.__chosen = chosen
        self.__buttons = dict()
        self.__label = label

    # Getter for the starting attribute
    def get_starting(self):
        return self.__starting
    
    # Adds an item to the chosen set and updates buttons
    # TO-DO: Submit button so last choice is not a mistake
    # word          The word being selected
    def add_item(self, word:str):
        pressed_button: Button = self.__buttons[word]

        if pressed_button.cget("bg") == "grey":
            pressed_button.configure(bg="white")
            self.__chosen.remove(word)
        else:
            pressed_button.configure(bg="grey")
            self.__chosen.add(word)

        if(len(self.__chosen) == 4):
            self.check_items()
            self.__chosen = set()
    
    # Checks if the 4 chosen words make up a group
    def check_items(self):
        for word in self.__chosen: # updates buttons
            self.__buttons[word].configure(bg="white")

        for key in self.__all_groups:
            found = 0
            for word in self.__all_groups[key]["members"]:
                if word in self.__chosen:
                    found += 1
            
            if found == 4: # A group is found
                self.finished(key + " found", True)
                return
            if found == 3: # One is off
                self.finished("One is off", False)
                return
        
        # Not a good guess
        self.finished("Bad guess", False)
        return
    
    # Updates screen after check_items
    # response              The change made to the label
    # done                  True if chosen make up a group, otherwise false
    def finished(self, response:str, done:bool):
        if(done): # Removes already found words
            for word in self.__chosen: 
                self.__buttons[word].configure(bg = "black")
                self.__buttons[word].configure(command = lambda:print())
        else: # User losses a guess
            self.__guesses -= 1

        # updates label
        self.__label.configure(text=response + " (" + str(self.__guesses) + " tries left)")

        # No more guesses are left
        if self.__guesses == 0:
            for child in ROOT.winfo_children():
                if type(child) == tk.Frame:
                    child.destroy()
            self.__label.configure(text="Game Over! You Lost")
            input_game_id(self.__label)

        
        complete = True
        for key in self.__buttons:
            if self.__buttons[key].cget("bg") != "black":
                complete = False
        if(complete):
            for child in ROOT.winfo_children():
                if type(child) == tk.Frame:
                    child.destroy()
            self.__label.configure(text="Winner Winner Chicken Dinner")
            input_game_id(self.__label)
            

    
    # Stores tk.Button objects as an attribute
    # buttons           dictionary with a key value of (word, button object)
    def set_buttons(self, buttons:dict):
        self.__buttons = buttons

# Creates a button for the gird
# controller            The game logic object
# frame                 The frame holding the button
# word                  The text of the button
# return                The button being made
def create_button(controller:Connections, frame:tk.Frame, word:str):
    return Button(frame, text=word, command=lambda: controller.add_item(word))

# Creates the game screen
# id                The index of the game in the DB
# label             The informational label needed to commmunicate with user
def create_game_env(id:int, label:tk.Label):
    # Creates game frame
    overallFrame=tk.Frame(ROOT,width=500,height=500,bg='lightblue')
    overallFrame.pack()

    # Creates game logic
    controller = Connections(set(), label, id)

    # Creates buttons
    game_buttons = dict()
    for row in controller.get_starting():
        frame = tk.Frame(overallFrame,width=500,height=500,bg='lightblue')
        frame.pack(side='bottom')
        for word in row:
            button = create_button(controller, frame, word)
            button.pack(side='right')
            game_buttons[word] = button
    
    # Adds buttons to the logic
    controller.set_buttons(game_buttons)

# Submits the game id and creates the environment
# label                 The informational label
# entry                 The input field that stores the input
# frame                 THe frame that holds the input widgets
def inputted_id(label:tk.Label, entry:tk.Entry, frame:tk.Frame):
    try: 
        id = int(entry.get())
        frame.destroy()
        create_game_env(id, label)
        label.pack()
    except: # if invalid, skip
        pass

# asks the user for the game that they want to play
# info_label            The label that is used to communicate with the user
def input_game_id(info_label: tk.Label):
    id_frame = tk.Frame(ROOT, bg="lightblue")
    id_frame.pack()

    input_info = "Enter a number for the game id between 0 and " + str(len(GAMES)-1)
    tk.Label(id_frame,text=input_info,bg="lightblue",fg="black").pack(pady=(50,10), padx=50)

    id_input:tk.Entry = tk.Entry(id_frame,bg="white",fg="black")
    id_input.pack(side="left", padx=(50,0), pady=(0, 50))

    Button(id_frame, text="Submit", command=lambda: inputted_id(info_label, id_input, id_frame)).pack(side="right", padx=(0, 50), pady=(0, 50))

def main():
    # Create window
    ROOT.title("Example")
    ROOT.configure(bg='lightblue')

    # creates game
    info_label = tk.Label(ROOT,text="(4 tries left)",bg="lightblue",font=('Helvetica',30))
    input_game_id(info_label)

    # Displays window
    ROOT.mainloop()

if __name__ == "__main__":
    main()