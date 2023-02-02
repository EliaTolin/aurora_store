![Logo](https://www.auroradigital.it/logo_aurora_store.png)

# AuroraStore 📲

[![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)]()[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)]()[![Html](https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white)]()[![Css](https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white)]()

AuroraStore è un progetto universitario per l'esame Tecnologie Web.

E' uno store di vendita e acquisto applicazioni sia per iOS che per Android.

Potrai vendere ed acquistare le App per entrambi i tuoi dispositivi, un'acquisto rapido ed sicuro.

## Prerequisiti ⏮

Per avviare il progetto sono necessari i seguenti prerequisiti

- _Python3_
- _pip3_

## Installazione 🥇

Le seguenti fasi sono necessarie affinchè il progetto sia utilizzabile in locale.

### Clone del progetto

```bash
    git clone https://github.com/EliaTolin/aurorastore.git
    cd aurorastore
```

### Virtualenv (consigliato)

Si consiglia di utilizzare un ambiente _virtual enviroment_ in modo tale da realizzare un ambiente indipendente alla tua installazione Python. Le modifiche scaricate rimarranno locali al Virtualenv.

#### Windows

```bash
    pip install virtualenv
    python3 -m venv env
    cd env
    .\Scripts\activate
```

#### MacOS / Linux

```bash
    python3 -m venv env
    cd env
    source env/bin/activate
```

### Installazione dipendenze

Tramite il file requirements.txt verranno scaricate le precise dipendenze necessarie al progetto.

```bash
    pip3 install -r requirements.txt
```

## Docker 🐳

Per lo sviluppo è possibile utilizzare il _Dockerfile_.

```bash
    docker build -t aurorastore .
    docker run -p 8000:8000 aurorastore
```

## Tests 💯

Per eseguire i test, utilizzare il seguente comando

```bash
    python manage.py tests
```

## Creazione Admin 👮

E' possibile creare un utente admin tramite il seguente comando, in tal modo è possibile accedere alla pagina dell'admin e gestire la piattaforma AuroraStore.

```bash
    python manage.py createsuperuser
```

## Disclaimer ❗️

La piattaforma viene rilasciata con un Database già strutturato con le tabelle, ma vuoto di contenuto.
In tal modo non sarà necessario procedere alla strutturazione delle tabelle nello storage tramite i comandi:

```bash
    python manage.py migrate --run-syncdb
```

## Acknowledgements 📚

- [Esame di Tecnologie Web](https://personale.unimore.it/rubrica/contenutiad/clcanali/2022/65389/N0/N0/9999)

## Contributing ⭐️

Dopo l'8 Febbraio 2023 è possibile contribuire!