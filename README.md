# 24-Game Discord bot
A minimal discord bot that lets players play the classic **24 Game** math game. In case if you don't know what that is: you are given 4 numbers from 1 to 13 and have to make a 24 using the four basic arithmetic operations (as well as parenthesis). 

Start a multi-round game with `/game`, and submit answers through the popup form.

Invite link:
https://discord.com/oauth2/authorize?client_id=1537995314806652958&permissions=274877982720&integration_type=0&scope=bot

## Credits
Pulls a data set of valid 24-game combinations from nlile's HuggingFace dataset.

HACK CLUB AI DISCLOSURE: Used AI to give me a brief crash course on how to use the Discord.py framework. Pretty much all the code here is hand-written, though.


## Tech Stack
- **Python** - core language
- **[discord.py](https://discordpy.readthedocs.io/)** - bot framework
- **[simpleeval](https://pypi.org/project/simpleeval/)** - safe evaluation of player-submitted math expressions
- **[Hugging Face `datasets`](https://huggingface.co/docs/datasets/)** - puzzle data loading
- **Flask** - lightweight keep-alive endpoint for hosting
- **[Render](https://render.com/)** - deployment/hosting