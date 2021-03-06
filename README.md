__MusicQuizzer__ (_musicquizzer_) is a Python program that can help you prepare
for any test that involves listening to excerpts of music pieces and answering
multiple choice questions about them.

# Installation

## Mac OS X

First, download and install Python 2.6.6 from
[here](http://www.python.org/ftp/python/2.6.6/python-2.6.6-macosx10.3.dmg).
Later versions of Python are unsupported on Mac OS X because pygame does not
run on them.

Next, download and install pygame from 
[here](http://pygame.org/ftp/pygame-1.9.1release-py2.6-macosx10.5.zip).

Finally,
[download MusicQuizzer](https://github.com/earwig/music-quizzer/tarball/v0.1.2)
and extract it wherever you want. To use, simply double-click on the
`mac_osx.command` file inside (do not move or delete any of the other files).

## Windows

First, download the installer for Python 2.7.1 from
[here](http://python.org/ftp/python/2.7.1/python-2.7.1.msi). Use the default
settings during installation.

Next, download and install pygame from
[here](http://pygame.org/ftp/pygame-1.9.2a0.win32-py2.7.msi).

Finally,
[download MusicQuizzer](https://github.com/earwig/music-quizzer/zipball/v0.1.2)
and extract it wherever you want. To use, simply double-click on the
`musicquizzer` file inside (do not move or delete any of the other files).

## Linux (with apt-get)

You should be on at least Python 2.7 (check with `python --version`), assuming
you keep your operating system up-to-date. Install the latest versions of
pygame and tk with:

    sudo apt-get install python-pygame python-tk

Finally,
[download MusicQuizzer](https://github.com/earwig/music-quizzer/tarball/v0.1.2)
and execute the program with `python musicquizzer.py` from your terminal.

# Usage

The first time you start the program, it will download all of the 25 necessary
(default) music pieces to the `pieces` folder. This is a ~70 MB download.

MusicQuizzer will present you with an answer sheet, containing four or five
multiple choice questions per piece (which are, of course, randomized every
time you begin a new quiz). Press `Start Quiz` to begin listening to the
excerpts. Each one is played for 30 seconds. You are then given five seconds of
rest, followed by the next piece. After all excerpts have been played, you
_cannot_ re-listen to them. Press `Submit Answers` to "hand in" your quiz and
view the results.

# Modifying

The music pieces are located in `pieces/`, in `.mp3` format. The file
`config.cfg` contains the information for each excerpt, like so:
    
    [10.mp3]
    title: Der Erlkönig
    composer: Franz Schubert
    era: Romantic
    genre: Lied
    form: Through-composed
    url: /music/10_The_Erlking_Erlkonig.mp3

The section's header is the name of the file in `pieces/` (or whatever
directory you have chosen), and the fields hold the information that
MusicQuizzer will use to generate questions. The exception is the `url` field,
which is the _direct_ URL (when combined with the `base_url` setting in the
`[general]` header) that MusicQuizzer will use to download the piece if
it does not have a file with that name.

Feel free to rename any of the pieces, delete them, add totally new ones, or
change their information. This program is designed to be customizable.

In the config file, you can also change the length of time each excerpt is
played for, the time between each excerpt, and other things. If an attribute is
not defined for a certain piece, the quizzer will not ask the question in that
excerpt, but the question will remain for other pieces.
