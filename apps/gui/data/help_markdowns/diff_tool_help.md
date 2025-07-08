### ℹ️ IMX Diff Tool

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

4️⃣ **Run de Vergelijking**  

- Klik op **“Run Comparison”** om de vergelijking uit te voeren.  
- De resultaten worden automatisch als ZIP-bestand aangeboden voor download.

</br>

Wanneer je alle stappen hebt doorlopen kun je het resultaat downloaden en opnieuw starten indien nodig. 🚂✨


⚠️ NOTE: de applicatie is niet bedoeld om grote bestanden zoals een EOS te vergelijken, dit zal resulteren in een download die niet start wegens webframework limitations. 