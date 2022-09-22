<h1 align="center"> ValeBulary <br> GRE Hangman game </h1>

<!-- <div align="center">
    <img src="logo.png" width=50% height=50% align="center">
</div> -->

# 🔧 Set-up

The only dependency to run the game is `pygame`, which can be installed
via pip

```
python3 -m pip install pygame
```

More on `pygame` and how to set it up in case of troubleshooting 
can be found [on their website.](https://www.pygame.org/wiki/GettingStarted)

Additionally, if you want to re-create the vocabulary data, or modify the code
that produces it, you'll need `pandas` and `PyPDF2`.

## ⚙️  Start the game

```
python3 src/valebulary.py
```

# 📝 Instructions

## Main mechanic
The game follows a similar mechanic to that of the classic hangman.
You'll be shown a description and you'll need to guess which word it belongs to.
You won't be able to guess one letter at a time, but rather entire words (as
you're supposed to memorise them).

> You have **5 attempts** to guess the word. Each attempt draws a part of the
hangman, and once complete, the round is over. The card is added to the "Needs
to learn" stack and will be saved for a future session.

## Special buttons
You can use several hint buttons to help you remember the word. 

- Use the "Reveal Letter" button to reveal all occurrences of a single letter.
- Use the "Add Example" button to provide a sentence in which the word to guess 
is used.
- "Skip word" will put the word card at the end of the stash, and will 
appear later on
- "Show word" is essentially giving up and revealing the entire word. Choosing 
to do this is no different from running out of attempts.

## Gallery mode
You can visualise past sessions in the gallery, accessible from the main menu.