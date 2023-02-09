# SCRAPE_ELEGY

SCRAPE_ELEGY is a lament for what we give over to the bots. A mourning poem for the late capitalist hell that makes even the worst of us valuable. A cringe tour of the digital graveyard we make day by day. A sweet little drown in the doom scroll. A comedic monologue starring you and only you. All you need to hand over is your handle. All you will leave with is the OMG echo. 

## Installation

The project uses **pipenv**.

1. Clone this repository
2. Install **Python 3.10.4** (probably fine with a later version)
3. Install **Redis**. It may be possible to get around redis for dev work using concurrency settings in Huey, but Channels (for websockets) likely needs Redis.
   1. On Windows, may need WSL (I used WSL1), or could try https://github.com/tporadowski/redis
   2. If you're getting BZPOPMIN errors, may need a more recent version of redis (e.g. 5.x or 6.x or higher). Run `sudo add-apt-repository ppa:redislabs/redis` then update and install.
4. Install pipenv with `pip install pipenv`
5. If...
   1. You wish to install the virtualenv in the **project's directory** (don't worry - it'll be `.gitignored`) - create an empty .venv folder in the project root, e.g., `mkdir .venv`
   2. You wish to install the virtualenv in the default location - e.g., could be on your OS drive - just continue to next step
6. Install python packages: `pipenv install` (or use your IDE)
7. Install javascript packages: `cd frontend && npm install`
8. Get an Azure _Speech Service_ API key. Create a `.env` file in the project root (next to `manage.py`) like so. DO NOT COMMIT YOUR API KEYS TO GIT.
   ```
   AZURE_SPEECH_REGION=<<your region>>
   AZURE_SPEECH_KEY=<<your api key>>
   ```

## Running

Make sure that redis is running. Use default port 6379.
```
redis-server
```

Run the huey consumer (not required if using huey in immediate mode - configure in settings.py)
```
python manage.py run_huey
```

Run the django server at http://localhost:8000/admin
```
python manage.py runserver
```

Run the frontend development server at http://localhost:3000/
```
cd frontend
npm start
```
