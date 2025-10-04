# edtlr-browser - Aplicația Web pentru navigarea prin intrările din eDTLR

## Cerințe software

1. Python 3.11
2. Django 5.2

## Configurearea mediului de dezvoltare

Configurearea mediului de execuție a aplicației de navigare a intrărilor din eDTLR presupune următoarele acțiuni:

1. Crearea unui mediu virtual,
2. Instalarea pachetelor necesare pentru execuție,
3. Instalarea pachetelor necesare pentru dezvoltare.

Pașii de mai sus pot fi executați rulând comanda `make dev-venv` în directorul-rădăcină al depozitului de cod, acolo unde se regăsește fișierul `Makefile`.

## Importul de date

Importul de date în aplicație poate fi executat în două moduri:
- regim normal și
- regim forțat.

Fiecare dintre aceste moduri este prezentat mai jos.

### Importul de date în regim normal

Atunci când datele sunt importate în regim normal, aplicația iterează prin fișierele cu extensia `.xml` din directorul specificat în linia de comandă. Conținutul fiecărui fișier este citit iar valorile atributelor `md5hash` sunt comparate cu valorile respective ale intrării din baza de date, identificată după valoarea atributului `entry.id`. Dacă valorile atributelor `md5hash` sunt egale cu valorile din baza de date, aplicația trece la următorul fișier; altfel, aplicația va actualiza intrarea din baza de date cu valorile citite din fișier.

Pentru a importa datele în regim normal în baza de date a aplicației, se execută (în directorul rădăcină al depozitului de cod) următoarea comandă:
```sh
make import IMPORT_DIR=<cale-director>
```
unde `<cale-director>` este calea către directorul care conține datele ce urmează să fie importate, de exemplu:
```sh
make import IMPORT_DIR=/tmp/edtrl-entries
```

### Importul de date în regim forțat

Atunci când datele sunt importate în regim forțat, aplicația iterează prin fișierele cu extensia `.xml` din directorul specificat în linia de comandă și actualizează intrările din baza de date indiferent dacă datele au fost modificate sau nu.

Pentru a importa datele în regim forțat în baza de date a aplicației, se execută (în directorul rădăcină al depozitului de cod) următoarea comandă:
```sh
make import IMPORT_DIR=<cale-director> FORCE_IMPORT=--force
```
unde `<cale-director>` este calea către directorul care conține datele ce urmează să fie importate, de exemplu:
```sh
make import IMPORT_DIR=/tmp/edtrl-entries FORCE_IMPORT=--force
```
