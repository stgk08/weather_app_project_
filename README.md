# 🌦️ Kuben Vær-app

## 1. Introduksjon

Kuben Vær-app er et skoleprosjekt utviklet av Stefanos Gkiokas i **VG2 Informasjonsteknologi. Prosjektet er laget for å vise forståelse for hvordan en moderne web-applikasjon bygges opp ved hjelp av **backend**, **database** og **frontend**, og hvordan disse delene samarbeider.

Applikasjonen simulerer et ekte vær-system der værdata hentes, behandles, lagres i en database og deretter presenteres for brukeren i et oversiktlig og moderne brukergrensesnitt. Selv om prosjektet er relativt enkelt i funksjonalitet, representerer det et realistisk mini fullstack-prosjekt.

---

## 2. Formål med prosjektet

Formålet med Kuben Vær-app er å:

* lære hvordan en Flask-applikasjon er bygget opp
* forstå hvordan Python kan kobles til en database
* bruke SQL i praksis
* jobbe med HTML-templates
* bruke moderne CSS-verktøy (Tailwind CSS)
* trene på feilsøking av ekte feil

Prosjektet er også laget for å dokumenteres godt, slik at både lærer og andre elever kan forstå hvordan løsningen fungerer.

---

## 3. Teknologier og verktøy brukt

### 3.1 Backend

Backend er skrevet i **Python 3** og bruker **Flask** som web-rammeverk.

Flask brukes til:

* å håndtere HTTP-forespørsler
* definere ruter (URL-er)
* koble frontend og backend sammen
* sende data til HTML-templates

I tillegg brukes:

* **mysql-connector-python** for databasekommunikasjon
* **dataclasses** for ryddig strukturering av data

---

### 3.2 Database

Databasen er laget i **MariaDB / MySQL**, som er en relasjonell database.

Databasen brukes til:

* lagring av værdata
* unngå unødvendige API-kall
* caching av tidligere data

Tabellen `vaerdata` inneholder blant annet:

* id
* lokasjon
* temperatur
* beskrivelse
* tidspunkt for siste oppdatering

Databasen er en sentral del av prosjektet og var også kilden til flere av feilene som oppstod under utviklingen.

---

### 3.3 Frontend

Frontend er laget med:

* HTML5
* Jinja templates (Flask)
* Tailwind CSS

HTML-filen fungerer som en **template**, som betyr at Flask fyller inn data før siden sendes til nettleseren.

Tailwind CSS brukes til styling og gir prosjektet:

* moderne design
* responsivt layout
* ryddig og konsistent stil

---

## 4. Prosjektstruktur

```text
Miniprosjekt/
│
├── app.py               # Flask-applikasjon, backend-logikk og database
├── templates/
│   └── index.html       # HTML-template med Tailwind CSS
├── venv/                # Virtual environment
├── README.md            # Denne filen
```

Denne strukturen følger vanlig praksis for Flask-prosjekter.

---

## 5. Hvordan applikasjonen fungerer (steg for steg)

### 5.1 Oppstart

Når Flask-applikasjonen startes (`python app.py`), skjer følgende:

* Flask initialiseres
* databasekobling opprettes
* nødvendige tabeller sjekkes eller opprettes

---

### 5.2 Brukerforespørsel

Når en bruker åpner nettsiden i nettleseren:

* nettleseren sender en HTTP GET-forespørsel til Flask
* Flask mottar forespørselen på ruten `/`

---

### 5.3 Databehandling

Flask:

* sjekker om værdata finnes i databasen
* vurderer om dataene er gamle eller nye
* oppdaterer databasen hvis nødvendig

Dette gir bedre ytelse og mindre belastning.

---

### 5.4 Rendering av template

Når dataene er klare:

* Flask sender dataene til `index.html`
* Jinja erstatter variabler som `{{ lokasjon }}` med ekte data
* ferdig HTML sendes til nettleseren

---

## 6. Dataclasses og hvorfor de brukes

Prosjektet bruker Python `@dataclass` for å representere værdata.

Eksempel:

```python
@dataclass
class VaerData:
    lokasjon: str
    temperatur: float
    beskrivelse: str
    sist_oppdatert: datetime
```

Fordeler:

* mer oversiktlig kode
* mindre feil
* enklere å sende data mellom lag
* bedre struktur

---

## 7. Brukergrensesnitt og design

Designet er laget med fokus på:

* enkelhet
* tydelighet
* moderne uttrykk

Brukeren ser:

* lokasjon
* temperatur
* værbeskrivelse
* ikon basert på været
* status på data (cache/API)

Alt design håndteres via Tailwind-klasser direkte i HTML.

---

## 8. Feilsøking og utfordringer

Feilsøking var en **svært sentral del av dette prosjektet**, og en av de viktigste læringsprosessene. Prosjektet fungerte ikke som forventet i starten, og det oppstod flere feil samtidig. Dette gjorde feilsøkingen mer krevende, men også mer realistisk sammenlignet med ekte IT-prosjekter.

### 8.1 500 Internal Server Error

En av de første og mest forvirrende feilene var at nettsiden viste:

```
500 Internal Server Error
```

Denne feilen betyr at:

* Flask-applikasjonen krasjer på serversiden
* nettleseren får ikke ferdig HTML
* feilen må finnes i backend (Python eller database)

Dette lærte meg at man **ikke skal feilsøke i HTML først**, men lese feilmeldinger i terminalen der Flask kjører.

---

### 8.2 SQL-syntaksfeil (Error 1064)

En av de viktigste feilene var:

```
1064 (42000): You have an error in your SQL syntax
```

Årsakene var blant annet:

* bruk av `#` som kommentar i SQL (ikke støttet i MariaDB/MySQL)
* feil formatering av SQL-strenger i Python
* flere SQL-kommandoer kjørt samtidig

Dette førte til at:

* tabellen ikke ble opprettet
* INSERT- og SELECT-spørringer feilet

Løsningen var å:

* rydde SQL-koden
* bruke korrekt SQL-syntaks
* teste SQL manuelt i databasen

---

### 8.3 Manglende database og tabell (Error 1146)

En annen kritisk feil var:

```
1146 (42S02): Table 'vaer_kuben_db.vaerdata' doesn't exist
```

Dette betydde at:

* databasen eller tabellen ikke eksisterte
* Flask prøvde å hente data før tabellen var opprettet

Jeg løste dette ved å:

* sjekke databasen manuelt med `SHOW DATABASES;`
* sjekke tabeller med `SHOW TABLES;`
* legge inn `CREATE TABLE IF NOT EXISTS` i koden

Dette lærte meg viktigheten av å **alltid sikre at databasen er klar før bruk**.

---

### 8.4 Feil databasenavn og inkonsistente navn

Et annet problem var at databasenavn og tabellnavn:

* var skrevet forskjellig i SQL og Python
* inneholdt norske bokstaver (æ, ø, å)

Dette førte til uventede feil og gjorde feilsøking vanskeligere.

Løsningen var å:

* standardisere navn (kun a–z)
* bruke konsekvente navn overalt
* velge enkle og tydelige tabellnavn

---

### 8.5 Problemer med Python-miljø (pip / venv)

Underveis oppstod også problemer med Python-miljøet:

```
ImportError: cannot import name 'guess_lexer_for_filename'
```

Dette skyldtes:

* ødelagt `pip`-installasjon i virtual environment
* konflikter mellom pakkeversjoner

I stedet for å fortsette å installere og avinstallere pakker, lærte jeg å:

* stoppe opp
* identifisere om feilen faktisk var relevant for prosjektet
* fokusere på kjerneproblemene først

---

### 8.6 Hva feilsøkingen lærte meg

Gjennom feilsøkingen lærte jeg:

* hvordan man leser og tolker feilmeldinger
* forskjellen på frontend-feil og backend-feil
* viktigheten av å teste én ting av gangen
* at små feil kan føre til store problemer
* at strukturert feilsøking sparer tid

Feilsøkingen var krevende, men ga mye læring og bedre forståelse av hvordan hele systemet henger sammen.

---

## 9. Hvordan kjøre prosjektet lokalt

### 9.1 Kloning av repo

```bash
git clone <repo-url>
```

### 9.2 Aktivere virtual environment

```bash
venv\Scripts\activate
```

### 9.3 Installere avhengigheter

```bash
pip install flask mysql-connector-python
```

### 9.4 Starte applikasjonen

```bash
python app.py
```

### 9.5 Åpne i nettleser

```
http://127.0.0.1:5000
```

---

## 10. Videre forbedringer

Hvis prosjektet skulle videreutvikles, kunne man:

* hente ekte værdata fra et API
* legge til flere lokasjoner
* legge til brukerinnlogging
* forbedre feilhåndtering
* deploye prosjektet til skyen

---

## 11. Hva jeg har lært

Dette prosjektet har lært meg:

* hvordan et fullstack-prosjekt er bygget opp
* hvordan backend og frontend samarbeider
* hvordan databaser brukes i praksis
* hvordan man feilsøker systematisk
* viktigheten av god dokumentasjon

---

## 12. Konklusjon

Kuben Vær-app er et gjennomført skoleprosjekt som kombinerer flere teknologier i én løsning. Prosjektet var utfordrende, spesielt på grunn av mange feil i starten, men gjennom grundig feilsøking og strukturert arbeid ble alle problemene løst.

Prosjektet har gitt verdifull erfaring innen både teknisk utvikling og problemløsning, og fungerer som et godt grunnlag for videre arbeid med webutvikling og IT-prosjekter.
