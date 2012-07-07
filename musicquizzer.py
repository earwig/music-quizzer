#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
MusicQuizzer is a Python program that can help you prepare for any test that
involves listening to excerpts of music pieces and answering multiple choice
questions about them. For more information, see the included README.md.
"""

from __future__ import division

import ConfigParser as configparser
import os
from pygame import mixer, error
import random
import thread
import time
from Tkinter import *
from tkFont import Font
from urllib import urlretrieve

__author__ = "Ben Kurtovic"
__copyright__ = "Copyright (c) 2011-2012 Ben Kurtovic"
__license__ = "MIT License"
__version__ = "0.1.2"
__email__ = "ben.kurtovic@verizon.net"

config_filename = "config.cfg"
config = None
piece_dir = None
download_complete = False

master_width = 500
master_height = 500
question_height = 100

class AnswerSheet(object):
    def __init__(self, master):
        self.master = master
        self.order = generate_piece_order()
        
        self.init_widgets()
        self.generate_questions()
        self.grid_questions()
        
    def init_widgets(self):
        self.scroll = Scrollbar(self.master)
        self.scroll.grid(row=1, column=1, sticky=N+S)
        
        self.canvas = Canvas(self.master, yscrollcommand=self.scroll.set,
                width=master_width, height=master_height-30)
        self.canvas.grid(row=1, column=0, sticky=N+S+E+W)
        self.canvas.grid_propagate(0)
        
        self.scroll.config(command=self.canvas.yview)
        
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        self.frame = Frame(self.canvas)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)
        
        self.header = Frame(self.master, bd=2, relief="groove")
        self.header.grid(row=0, column=0, columnspan=2)
        
        self.header_buttons = Frame(self.header, width=250, height=30)
        self.header_buttons.grid_propagate(0)
        self.header_buttons.grid(row=0, column=0)
        
        self.playing_container = Frame(self.header, width=master_width-240, height=30)
        self.playing_container.grid_propagate(0)
        self.playing_container.grid(row=0, column=1)
        
        self.play_button = Button(self.header_buttons, text="Start Quiz",
                command=self.play)
        self.play_button.grid(row=0, column=0)
        
        self.submit_button = Button(self.header_buttons, text="Submit Answers",
                command=self.submit)
        self.submit_button.grid(row=0, column=1)
        
        self.playing = StringVar()
        self.playing.set("Now Playing: None")
        self.now_playing = Label(self.playing_container, textvar=self.playing)
        self.now_playing.grid(row=0, column=0)
        
    def generate_questions(self):
        num_answers = config.getint("general", "answers")
        answer_choices = {} # dict of {category1: {choice1, choice2...}, ...}
        questions = {} # dict of {piece1: [question1, question2...], ...}
        self.number_of_questions = 0
        
        for piece in self.order:
            for category, answer_choice in config.items(piece):
                if category == "url":
                    continue
                try:
                    answer_choices[category].add(answer_choice)
                except KeyError:
                    answer_choices[category] = set([answer_choice])
        
        for piece in self.order:
            questions[piece] = dict()
            for category in config.options(piece):
                if category == "url":
                    continue
                correct_choice = config.get(piece, category)
                questions[piece][category] = [correct_choice]
                
                all_choices = list(answer_choices[category])
                all_choices.remove(correct_choice)
                
                for x in range(num_answers - 1):
                    try:
                        choice = random.choice(all_choices)
                    except IndexError:
                        break # if there aren't enough choices in the choice
                              # bank, there will be fewer answer choices than
                              # we want, but what else can we do?
                    all_choices.remove(choice)
                    questions[piece][category].append(choice)
                    
                question_choices = questions[piece][category]
                questions[piece][category] = randomize_list(question_choices)
                self.number_of_questions += 1
        
        self.questions = questions
        
    def grid_questions(self):
        self.answers = {}
        self.stuff_to_disable = [] # what gets turned off when we press submit?
        question_grid = Frame(self.frame)
        this_row_number = 0
        
        excerpt = "A"
        
        for piece in self.order:
            question_row_number = 1
            
            piece_questions = self.questions[piece].keys()
            piece_questions.reverse() # correct ordering issues
            
            self.answers[piece] = {}
            
            height = question_height * len(piece_questions) + 20
            piece_grid = Frame(question_grid, width=master_width,
                    height=height)
            
            title = Label(piece_grid, text="Excerpt {0}".format(excerpt),
                    font=Font(family="Verdana", size=10, weight="bold"))
            excerpt = chr(ord(excerpt) + 1) # increment excerpt by 1 letter
            title.grid(row=0, column=0, columnspan=3)
            
            for question in piece_questions:
                agrid = LabelFrame(piece_grid, text=question.capitalize(),
                        width=master_width, height=question_height)
                
                a = StringVar()
                self.answers[piece][question] = a
                
                w = (master_width / 2) - 4
                lhgrid = Frame(agrid, width=w, height=question_height)
                rhgrid = Frame(agrid, width=w, height=question_height)
                
                this_row = 0
                left_side = True
                
                for choice in self.questions[piece][question]:
                    if left_side:
                        r = Radiobutton(lhgrid, text=choice,
                                value=choice, variable=a)
                        left_side = False
                    else:
                        r = Radiobutton(rhgrid, text=choice,
                                value=choice, variable=a)
                        left_side = True
                        this_row += 1
                    r.grid(row=this_row, column=0, sticky=W)
                    self.stuff_to_disable.append(r)
                                
                lhgrid.grid_propagate(0)
                lhgrid.grid(row=0, column=1)
                
                rhgrid.grid_propagate(0)
                rhgrid.grid(row=0, column=2)
                                
                agrid.grid_propagate(0)
                agrid.grid(row=question_row_number, column=0)
                question_row_number += 1
            
            piece_grid.grid_propagate(0)
            piece_grid.grid(row=this_row_number, column=0)
            this_row_number += 1
            
        question_grid.grid(row=0, column=0)

    def play(self):
        self.play_button.configure(state=DISABLED)
        thread.start_new_thread(self.play_pieces, ())
    
    def play_pieces(self):
        self.excerpt_length = (config.getfloat("general", "excerpt_length") - 5) * 1000
        break_length = config.getfloat("general", "break_length")
        cur_excerpt = "A"
        
        mixer.init()
        for piece in self.order:
            try:
                self.playing.set("Now Playing: Excerpt {0}".format(cur_excerpt))
                before = time.time()
                self.play_piece(piece)
                after = time.time()
                while after - before < 3:  # if the piece played for less than
                    before = time.time()   # 3 seconds, assume something went
                    self.play_piece(piece) # wrong loading and try to replay it
                    after = time.time()
                self.playing.set("That was Excerpt {0}...".format(cur_excerpt))
                cur_excerpt = chr(ord(cur_excerpt) + 1)
                time.sleep(break_length)
            except error: # Someone quit our mixer? STOP EVERYTHING.
                break
        
        self.playing.set("Finished playing.")

    def play_piece(self, piece):
        mixer.music.load(os.path.join(piece_dir, piece))
        mixer.music.play()
            
        fadeout_enabled = False
        while mixer.music.get_busy():
            if mixer.music.get_pos() >= self.excerpt_length:
                if not fadeout_enabled:
                    mixer.music.fadeout(5000)
                    fadeout_enabled = True
            time.sleep(1)

    def submit(self):
        self.submit_button.configure(state=DISABLED)
        self.play_button.configure(state=DISABLED)
        for item in self.stuff_to_disable:
            item.configure(state=DISABLED)
        
        try:
            mixer.quit()
        except error: # pygame.error
            pass # music was never played, so we can't stop it
        
        right = 0
        wrong = []
        
        excerpt = "A"
        for piece in self.order:
            questions = self.questions[piece].keys()
            questions.reverse() # correct question ordering
            for question in questions:
                correct_answer = config.get(piece, question)
                given_answer = self.answers[piece][question].get()
                if given_answer == u"Der Erlk\xf6nig": # unicode bugfix
                    given_answer = "Der Erlk\xc3\xb6nig"
                if correct_answer == given_answer:
                    right += 1
                else:
                    wrong.append((excerpt, config.get(piece, "title"),
                            question, given_answer, correct_answer))
            excerpt = chr(ord(excerpt) + 1)
        
        results = Toplevel() # make a new window to display results
        results.title("Results")
        
        noq = self.number_of_questions
        text = "{0} of {1} answered correctly ({2}%):".format(right, noq,
                round((right / noq) * 100, 2))
        
        if right == noq:
            text += "\n\nCongratulations, you got everything right!"
        
        else:
            text += "\n"
            for excerpt, title, question, given_answer, correct_answer in wrong:
                if not given_answer:
                    if question == "title":
                        text += "\nYou left the title of Excerpt {0} blank; it's \"{1}\".".format(
                                excerpt, correct_answer)
                    else:
                        text += "\nYou left the {0} of \"{1}\" blank; it's {2}.".format(
                                question, title, correct_answer)
                elif question == "title":
                    text += "\nExcerpt {0} was {1}, not {2}.".format(
                            excerpt, correct_answer, given_answer)
                else:
                    text += "\nThe {0} of \"{1}\" is {2}, not {3}.".format(
                            question, title, correct_answer, given_answer)
            
        label = Label(results, text=text, justify=LEFT, padx=15, pady=10,
                font=Font(family="Verdana", size=8))
        label.pack()
        
        
def randomize_list(old):
    new = []
    while old:
        obj = random.choice(old)
        new.append(obj)
        old.remove(obj)
    return new

def generate_piece_order():
    pieces = config.sections()
    pieces.remove("general") # remove config section that is not a piece
    return randomize_list(pieces)

def load_config():
    global config, piece_dir
    config = configparser.SafeConfigParser()
    config.read(config_filename)
    if not config.has_section("general"):
        exit("Your config file is missing or malformed.")
    
    piece_dir = os.path.abspath(config.get("general", "piece_dir"))

def get_missing_pieces(root):
    pieces = config.sections()
    pieces.remove("general")
    missing_pieces = []
    
    for piece in pieces:
        if not os.path.exists(os.path.join(piece_dir, piece)):
            missing_pieces.append(piece)
    
    if missing_pieces:
        window = Toplevel()
        window.title("PyQuizzer")
        window.protocol("WM_DELETE_WINDOW", root.destroy)
        
        status = StringVar()
        status.set("I'm missing {0} music ".format(len(missing_pieces)) +
                "pieces;\nwould you like me to download them for you now?")
        
        head_label = Label(window, text="Download Music Pieces", font=Font(
                family="Verdana", size=10, weight="bold"))
        head_label.grid(row=0, column=0, columnspan=2)
                
        status_label = Label(window, textvar=status, justify=LEFT, padx=15,
                pady=10)
        status_label.grid(row=1, column=0, columnspan=2)
        
        quit_button = Button(window, text="Quit", command=lambda: exit())
        quit_button.grid(row=2, column=0)
        
        dl_button =  Button(window, text="Download",
                command=lambda: do_pieces_download(missing_pieces, status,
                dl_button, status_label, window))
        dl_button.grid(row=2, column=1)
    
        window.mainloop()
    
    else:
        global download_complete
        download_complete = True

def do_pieces_download(pieces, status, dl_button, status_label, window):
    global download_complete
    dl_button.configure(state=DISABLED)
    
    if not os.path.exists(piece_dir):
        os.mkdir(piece_dir)
    
    counter = 1
    for piece in pieces:
        url = config.get("general", "base_url") + config.get(piece, "url")
        name = "{0} of {1}: {2}".format(counter, len(pieces),
                config.get(piece, "title"))
        urlretrieve(url, os.path.join(piece_dir, piece),
                lambda x, y, z: progress(x, y, z, name, status, status_label))
        counter += 1
    
    window.quit()
    window.withdraw()
    download_complete = True

def progress(count, block_size, total_size, name, status, label):
    percent = int(count * block_size * 100 / total_size)
    status.set("Downloading pieces...\n" + name + ": %2d%%" % percent)
    label.update_idletasks()

def run():
    root = Tk()
    root.withdraw()
    
    load_config()
    get_missing_pieces(root)
    
    while not download_complete:
        time.sleep(0.5)
    
    window = Toplevel() 
    window.title("MusicQuizzer")
    answer_sheet = AnswerSheet(window)
    answer_sheet.canvas.create_window(0, 0, anchor=NW,
            window=answer_sheet.frame)
    answer_sheet.frame.update_idletasks()
    answer_sheet.canvas.config(scrollregion=answer_sheet.canvas.bbox("all"))

    window.protocol("WM_DELETE_WINDOW", root.destroy) # make the 'x' in the
            # corner quit the entire program, not just this window
    window.mainloop()

if __name__ == "__main__":
    run()
