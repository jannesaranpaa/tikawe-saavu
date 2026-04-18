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

## Sovelluksen asennus ja testaaminen

### Asentaminen

Kloonaa kirjasto itsellesi ja siirry repositorioon
```shell
git clone https://github.com/jannesaranpaa/tikawe-saavu.git
cd tikawe-saavu
```

Asenna tarvittavat python-paketit
```shell
pip install -r requirements.txt
```

tai vaihtoehtoisesti
```shell
pip install flask
```

Alusta tietokanta
```shell
flask --app app init-db
```

Käynnistä sovellus
```shell
flask run
```

Nyt voit avata sovelluksen osoitteessa [127.0.0.1:5000](http://127.0.0.1:5000/)

### Testaaminen

1. Rekisteröi käyttäjä osoitteessa
   [auth/register](http://127.0.0.1:5000/auth/register)
2. Kirjaudu sisään osoitteessa [auth/login](http://127.0.0.1:5000/auth/login)
   (sinut on uudelleenohjattu tälle sivulle rekisteröitymisen jälkeen)
3. Hallitse kategorioita osoitteessa [categories/](http://127.0.0.1:5000/categories)
    - Voit luoda, muokata ja poistaa kategorioita
    - Kategorioita voisivat olla esimerkiksi _'Fyysinen esteettömyys'_ ja
      _'Kognitiivinen esteettömyys'_
4. Hallitse piirteitä osoitteessa [features/](http://127.0.0.1:5000/features)
    - Voit luoda, muokata ja poistaa piirteitä
    - Piirteitä voivat olla esimerkiksi _'Selkokieliset esittelytekstit'_ ja
      _'Riittävän leveät oviaukot'_
5. Hallitse tapahtumia osoitteessa [events/](http://127.0.0.1:5000/events)
    - Voit luoda, muokata ja poistaa tapahtumia
    - Tapahtumalle voit valita esteettömyysominaisuuksia, ja antaa niille
      kommentteja

