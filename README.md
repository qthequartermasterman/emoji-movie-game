# emoji-movie-game

This is a fun little game where the player is presented with a movie plot told using only emoji, and they have to guess the movie's title.

This is a fun project that was thrown together quickly, and is not even remotely "production-ready". 

This requires an OpenAI API Key set in your environment.


## Example

The player will be presented with a string of emoji.

```
👫🎲📜➡️🌳🌿😱🙅‍♀️🚪⏳➡️🏠🕰️👧👦🎲💨🧔🌳🐒🐘🐍🌪️🌧️✨🏃‍♂️🏞️🦹‍♂️🎯🌆🐅💧🔥🚗🤝👦👧🧔👱‍♀️🎲💥🚪🔄🔙🕰️➡️
```

They then have to guess the title of the emoji. These emoji describe the plot of the movie listed below (under the spoiler warning).

<details>
  <summary>Spoiler warning</summary>
  
  ```
  Jumanji
  ```
  
</details>

## Installing

First install the necessary requirements.

```bash
python -m pip install -r requirements.txt
```

OR 

```bash
uv pip install -r requirements.txt
```

## Running

Then, simply run the game script.

```bash
python game.py
```

Then open the local URL that is printed to the terminal in your browser.
