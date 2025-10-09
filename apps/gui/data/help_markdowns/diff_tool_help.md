### ℹ️ IMX Diff Report Tool

Deze tool genereerd een excel overzicht tussen twee IMX bestanden / situations. 
- Een project IMX bestand heeft situaties, een IMX container (zip) is een situatie (snapshot) en daarom is het niet mogelijk deze te kiezen.

</br>

1️⃣ **Upload IMX T1**  

- **IMX T1**: Upload het eerste IMX-bestand of container dat als basis dient voor de vergelijking.
- Indien het een project bestand is dan worden de aanwezig situations inzichtelijk in de dropdown, kies hier één van.

</br>

2️⃣ **Upload IMX T2**  

Idem als upload IMX T1, maar het is ook mogelijk om het zelfde bestand te gebruiken.
Zet hiervoor de switch **“Use same IMX for T2?”** aan. Hierna worden de aanwezig situatie in een dropdown weergegeven.
De tegenovergestelde situatie wordt automatisch geslecteerd maar kan handmatig worden overschreven.

</br>

3️⃣ **Optionele Instellingen**  

- **Generate GeoJSON?** Zet deze optie aan als je een GeoJSON-export wilt genereren.  
- **Convert to WGS84?** Deze optie verschijnt alleen als je GeoJSON aanzet en zorgt ervoor dat je GeoJSON wordt omgerekend naar WGS84-coördinaten.

</br>

5️⃣ **Specification (SpecFile) optie**  

De tool kan gebruik maken van een **specificatiebestand (CSV)** om de kolommen en velden in het resultaat extra betekenis te geven.

ℹ️ Zie de [documentatie](https://open-imx.github.io/imxInsights/reference/utils/header_annotator/#imxInsights.utils.headerAnnotator.HeaderSpec--specification-csv) voor details over de structuur van de CSV specificatie.

Je hebt drie keuzes:  

- **None** → er wordt geen specificatie gebruikt.  
- **Auto** → de tool probeert automatisch een passende specificatie te vinden.  
  - Je kunt hierbij optioneel een **versie kiezen** (bijv. `5.0.0` of `12.0.0`).  
  - Indien je **“Detect automatically”** of **`1.2.4`** kiest, dan wordt er géén specifieke versie vooraf gekozen. Als er meerdere kandidaten worden gevonden, verschijnt een popup waarin je handmatig kunt kiezen.  
  - Als je **`5.0.0`** of **`12.0.0`** selecteert en er is precies één match, dan wordt deze automatisch gebruikt zonder popup.  
- **Pick** → je kunt zelf een CSV-bestand uploaden als specificatie.  


📂 **Folderstructuur bij Auto**  
De tool zoekt specificatiebestanden in de map:  `/specifications/`

- Binnen deze map kunnen meerdere submappen aanwezig zijn.  
- Eindigt een mapnaam op een versie (bijvoorbeeld `.../5.0.0/` of `.../12.0.0/`), dan worden alle `.csv` bestanden in die map als mogelijke specificaties voor die versie beschouwd.  
- Bevindt zich **exact één** CSV-bestand in die versie-map, dan wordt deze automatisch gekozen.  
- Bevinden zich **meerdere** CSV-bestanden in die versie-map, dan krijgt de gebruiker een keuzescherm om de juiste te selecteren.  
- Bevinden zich **geen** bestanden in de juiste map, dan krijgt de gebruiker een melding.  


</br>

4️⃣ **Run de Vergelijking**  

- Klik op **“Run Comparison”** om de vergelijking uit te voeren.  
- De resultaten worden automatisch als ZIP-bestand aangeboden voor download.

</br>


Wanneer je alle stappen hebt doorlopen kun je het resultaat downloaden en opnieuw starten indien nodig. 🚂✨


⚠️ NOTE: de applicatie is niet bedoeld om grote bestanden zoals een EOS te vergelijken, dit zal resulteren in een download die niet start wegens webframework limitations. 