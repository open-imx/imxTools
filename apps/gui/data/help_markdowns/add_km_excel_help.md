### ℹ️ KM Excel Tool

Met deze tool voeg je automatisch **KM-waarden** toe aan een Excel-bestand met RD-coördinaten.
De KM-waarden worden berekend via de externe service [kmService](https://open-imx.github.io/kmService/).

---

#### 1️⃣ Upload je Excel-bestand

- Upload de Excel waarin je KM-waarden wilt toevoegen. Dit kan een diff- of populatierapport zijn, maar ook een Excel met een sheet waarin een kolom eindigt op `Point.gml:coordinates`.
- Er wordt uitgegaan van één GML-kolom per sheet. De coördinaten moeten in het RD-stelsel staan (`EPSG:28992`).
- Lijnstrings worden niet ondersteund, omdat deze in Excel soms afgekapt worden als ze erg lang zijn.

---

#### 2️⃣ Optionele instelling

- **Alleen simpele weergave gebruiken**  
  Standaard aangevinkt. Dit geeft een samengevoegde tekst, bijvoorbeeld: `km 81.610 (Hlg-Nscg)`.
  Zet deze optie uit als je ook de HM-waarde, afstand in meters en lintnaam als losse kolommen wilt toevoegen.

---

#### 3️⃣ Voeg KM toe

- Klik op **‘Add KM’** om de KM-berekening te starten. De verwerking kan enkele minuten duren.
- In het resultaat worden objecten per lintnaam gegroepeerd, zodat objecten binnen hetzelfde lint netjes onder elkaar staan.
- Als een object op meerdere linten valt (bijvoorbeeld bij flyovers of dive-unders), worden er meerdere linten gevuld.

⚠️ In sommige situaties zijn er geen raaien aanwezig in de GIS-data. Indien mogelijk wordt een lagere raai binnen de sub-geocode gebruikt. Lukt dit niet, dan kan er geen KM-waarde berekend worden.

---

Wanneer je klaar bent, kun je een nieuw bestand uploaden en het proces opnieuw doorlopen. 🚂📏✨

