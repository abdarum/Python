''' This is program that change words to similar words that are on the list.

Program wrote by Stefan in february 2018.
'''
__version__ = '0.05'



oryginal_list_of_words = ['frytek','wóda','kamień','fryzjer','mikrob']



from tkinter import * 

from difflib import SequenceMatcher
def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()


class Basic_word:
    ''' Class contain word and ratio of similarity to original word.'''
    
    input_word = ''

    def __init__(self,inserted_word,inserted_sim_ratio=0):
        self.word = inserted_word
        self.similar_ratio = inserted_sim_ratio

    def set_input_word(self, text_to_encourage_typing='',inserted_word = ''):
        ''' This method set input_word to inserted_word, but if it is empty method read text from console. '''
        if len(inserted_word) == 0:
            # text_to_encourage_typing = "Type anything you want ;) " 
            Basic_word.input_word = input()
        else:
            Basic_word.input_word = inserted_word

    def get_similar_ratio(self):
        self.similar_ratio = similar(self.word, Basic_word.input_word)

    def print(self):
        print("Word: {:20} similar ratio: {:.2f}%".format(self.word, self.similar_ratio*100))




class List_of_words:
    ''' Class contain a list of Basic_word. '''
    the_best_word = ''
    def __init__(self, inserted_list_of_words=[]):
        self.list = list() 
        if len(inserted_list_of_words) != 0:
            for i in inserted_list_of_words:
                self.list.append(Basic_word(i))

    def add_elements(self, inserted_list_of_words):
        for i in inserted_list_of_words:
            self.list.append(Basic_word(i))
            #print(i)

    def get_similar_ratio(self):
        for i in self.list:
            i.get_similar_ratio()
    
    def print(self):
        print("\n\t\n"+self.list[0].input_word+"\n") 
        for i in self.list:
            i.print()
        print("===================================================")
    
    def set_input_word(self,text_to_encourage_typing='',inserted_word = ''):
        if len(self.list) > 0:
            self.list[0].set_input_word(text_to_encourage_typing,inserted_word)
        else:
            print("You must add some item to list to insert word to compare")

    def sort(self):
        self.list.sort(key=lambda word: word.similar_ratio, reverse=True) 

    def find_the_best_word(self):
        self.get_similar_ratio()
        self.sort()
        for i in self.list:
            if  i.similar_ratio != 1 and i.similar_ratio > 0.5:
                List_of_words.the_best_word = i.word
                break
            elif self.list[0].input_word == "Kornel" or self.list[0].input_word == "stefan":
                List_of_words.the_best_word = "Stefan" 
            elif self.list[0].input_word == "kornel":
                List_of_words.the_best_word = "stefan"
            else:
                List_of_words.the_best_word = self.list[0].input_word  



def CLI():
    my_list = List_of_words(oryginal_list_of_words)
    looping = True
    print("This is program that change words to similar words that are on the list.")
    while(looping==True):
        print("\nWrite anything you want below:\n\t")
        my_list.set_input_word()
        print("")
        my_list.find_the_best_word()
        print("Ideal word is: "+my_list.the_best_word,"\n")

        print("What would you like to do next?")
        print("Type: "+"n to write something new")
        print("      "+"q to quit from this program")

        menu_input= input()
        if menu_input == "n":
            looping = True
        elif menu_input =="q":
            looping = False
        elif menu_input == "show_list":
            my_list.print()

class GUI:
     

    def __init__(self, master):
        self.my_list = List_of_words(oryginal_list_of_words)
        
        self.bg_color="black"
        self.button_color="MediumPurple4"
        self.font_color="yellow"
        self.master = master
        master.title("Change word!")
        master.configure(background=self.bg_color)

        self.label = Label(master, bg=self.bg_color, fg=self.font_color, text="Type anything you want!", font="none 14")
        self.label.pack()
        #self.label.grid(row=0,column=1)

        Label(master, bg=self.bg_color).pack()

        self.v = StringVar()
        self.v.set("")
        self.text_box = Entry(master, textvariable=self.v, width=60, bg="grey", fg="black", font="none 12")
        self.text_box.pack()
        #self.master.bind("<Enter>", self.get_input_word())
        #self.text_box.grid(row=2,column=1)
        self.text_box.bind('<Return>', self.get_input_word)

        Label(master, bg=self.bg_color).pack()
        
        self.generate_button = Button(master, bg=self.button_color, fg=self.font_color, text="Generate output word", command=self.get_input_word)
        self.generate_button.pack(side=LEFT)
        #self.generate_button.grid(row=4,column=0)

        self.greet_button = Button(master, bg=self.button_color, fg=self.font_color, text="Clear", command=self.input_box_clean)
        self.greet_button.pack(side=RIGHT)
        #self.greet_button.grid(row=4,column=2)



       
    def get_input_word(self, *ignore):
        input_text = self.text_box.get()
        if input_text != "":
            self.my_list.set_input_word(inserted_word = input_text)
            self.my_list.find_the_best_word()
            self.v.set(self.my_list.the_best_word)
            #self.my_list.print()
        else:
            #print("Nothing on input")
            pass


    def input_box_clean(self):
        self.v.set("")
        


root = Tk()
my_gui = GUI(root)
root.mainloop()
