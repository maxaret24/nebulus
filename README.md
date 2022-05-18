# Nebulus [BETA]

A minimalistic yet powerful userbot written from scratch in pyrogram. It's still BETA and a lot of features are yet to be added.

# Before you deploy

* Create a slave bot using [@Botfather](https://telegram.me/Botfather).

* Send `/setinline` and choose your bot. Then give a desired placeholder message [Example: Choose]. This will enable inline settings of your bot.

* You'll require the API token provided by Botfather during the setup

* Next up, you need to generate a session string<br>
[![Run on Repl.it](https://replit.com/badge/github/greplix/nebulus)](https://replit.com/@greplix/Nebuli-string-session)<br>
Run this repl to generate

* You'll get a session string in your Saved Messages. Keep it safe.


# Deploy

* <b>Railway</b>

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/eE5QG2?referralCode=6B3Q1r)

* <b>Heroku</b>

[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/greplix/nebulus)

* <b>Locally/VPS</b>

- You need to edit `nebulus.yml` locally. Supply the required values. Also supply `true` in `localdeploy:`.

>Docker

```
git clone https://github.com/greplix/nebulus.git
cd nebulus
docker build . -t ub
docker run ub
```

>Without Docker

```
git clone https://github.com/greplix/nebulus.git
cd nebulus
pip3 install -r requirements.txt
python3 -m ub
```

# Post-Deploy

After successfully deploying Nebulus, send `.alive` for stats or `.help` in any chat to get started!

