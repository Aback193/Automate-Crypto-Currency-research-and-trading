# Automatizacija istraživanja kripto valuta

##### Proračun analize sentimenta nastupa nakon što svi Crawler-i završe sa prikupljanjem članaka. Rezultati se upisuju u `Sentiment.csv` i `Sentiment.xlsx` fajlove. Startovanje Crawler-a i prikupljanja članaka se izvršava unutar: `app.py`

##### Skripta namenjena za pokretanje trgovine, nalazi se unutar Technical_analysis foldera: `start_trading.py`. Skripta najpre učitava rezultate sentimentalne analize tj. totalni sentiment iz `Sentiment.xlsx` fajla. Stoga je proračun sentimenta neophodan za startovanje trgovine. Binance.com API ključ je neophodan za trgovinu. Ključ treba upisati u `.env` fajl (API_KEY i API_SECRET).

##### Treniranje RandomForest modela se takođe inicira unutar `start_trading.py` skripte. Varijabla `classifier` može imati vrednost `retrain`, za ponovno treniranje postojećeg modela ili kreiranje novog, dok vrednost `load` učitava postojeći model za dalje pokretanje trgovine. Model se generiše za izabrani vremenski okvir, primer `timeframe = "15m"`.

##### Testirano na Linux OS - ARCH i MAC M1 Pro

## Preduslov
- Python 3.X.X
- `pip3 install setuptools`
- `pip3 install pipenv`
- `pipenv install`
- Docker
- `docker run -p 8050:8050 scrapinghub/splash --max-timeout 3600`
- Binance.com API ključ

## Startovanje Crawler-a i proračun sentimenta
- To activate this project's virtualenv, run: `pipenv shell`
- `python3 app.py`

## Startovanje trgovine
- To activate this project's virtualenv, run: `pipenv shell`
- `cd Technical_analysis`
- `python3 start_trading.py`
