# Automatizacija istraživanja kripto valuta

##### Proračun analize sentimenta nastupa nakon što svi Crawler-i završe poslove. Startovanje Crawler-a radi prikupljanja članaka: `python app.py`
  

##### Skripta namenjena za pokretanje trgovine, nalazi se unutar Technical_analysis foldera: `python start_trading.py`. Skripta najpre učitava rezultate sentimentalne analize. Stoga je proračun sentimenta (barem jednom) neophodan za startovanje trgovine. Binance.com API ključ je neophodan za trgovinu. Ključ se upisuje u `start_trading.py` i `binance_trade.py` skripte unutar Technical_analysis foldera. To mogu biti i dva različita ključa.

##### Testirano na Linux OS - ARCH

## Preduslov

- Python 3.x.x
- `pip install -r requirements.txt`
- Docker
- `docker run -p 8050:8050 scrapinghub/splash --max-timeout 3600`
- Binance.com API ključ
