# Saavu

Saavu on järjestelmä, jossa tapahtumien järjestäjät voivat julkaista
tapahtumansa esteettömyystiedot helposti ja selkeästi, täyttämättä tapahtuman
tietoja sen omilla nettisivuilla tai sosiaalisen median julkaisuissa.

## Sovelluksen toiminnot

- [x] Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- [x] Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ominaisuuksia
  (_feature_) ja niiden kategorioita (_category_) ja luomaan tapahtumia (_event_)
    - [ ] Käyttäjä voi muokata vain itse luomiaan tapahtumia
- [x] Tapahtuman esteettömyysominaisuuksiin voi lisätä huomioita
    - [ ] Myös sellaisiin ominaisuuksiin, jotka eivät toteudu, voi lisätä
      huomioita
- [ ] Käyttäjä voi listata omat tapahtumansa

## Sovelluksen asennus

Asenna `flask`-kirjasto:
```shell
pip install flask
```

Voit käynnistää sovelluksen näin:
```shell
flask run
```
