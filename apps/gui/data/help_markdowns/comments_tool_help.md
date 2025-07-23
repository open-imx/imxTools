### 💬 IMX Review Comment Tool

Deze tool ondersteunt het reviewproces van IMX-gegevens door het mogelijk te maken om commentaar uit een Excel Diff Report te **extraheren** en vervolgens opnieuw te **projecteren** op een nieuw diff-bestand.

Tijdens dit proces maakt de tool gebruik van:

- **Notes** (ook wel celnotities genoemd, toegevoegd via `Shift + F2` in Excel)
- **Vooraf gedefinieerde celstijlen** (op basis van achtergrondkleuren) om statussen toe te wijzen zoals **OK**, **NOK**, of **VRAAG**

> **⚠️ Let op:** `Notes` zijn **geen** threaded comments! Ze worden toegevoegd als eenvoudige celopmerkingen via `Shift + F2` en zijn zichtbaar als kleine rode driehoekjes in Excel.

Deze combinatie van notities en visuele stijl maakt het eenvoudig om opmerkingen te verzamelen, te beoordelen, en systematisch terug te plaatsen in aangepaste rapportversies.


---

De tool bestaat uit twee hoofdtabbladen:

- **Extract** – Haalt alle `notes` en status styles uit een Diff Report en maakt een overzicht van in een nieuw tabblad `comments`.
- **Reproject** – Neemt een bestaande `comments`-sheet en past de opmerkingen en status stylen opnieuw toe op een nieuwe versie van het Diff Report.

---

#### 🟢 Tabblad: Extract
Upload een een diff rapportage met review comments.

> Vink **“Voeg toe aan bestaand werkboek”** aan om het comments-tabblad toe te voegen aan het originele bestand, 
en activeer **“Overschrijf bestaand comments-tabblad”** indien dat tabblad al bestaat.

---

#### 🔁 Tabblad: Reproject
Upload een een diff rapportage en een excel met een `comments`-tabblad (gemaakt met de Extract-tool). 

De cel wordt op basis van de **PUIC** en het **XML PATH** (conform de column header) opgezocht om toe te voegen:  
- De oorspronkelijke **achtergrondkleur**
- De **commentaartekst** (indien aanwezig)

Er wordt een samenvatting in het tabblad `CommentPlacementSummary` gegenereerd met daarin met 
  - Geplaatste opmerkingen
  - Overgeslagen cellen
  - Niet-gevonden rijen

---

##### 🎨 Kleuren & Stijlen

De tool gebruikt **achtergrondkleuren** om het type opmerking te herkennen. Deze zijn gedefinieerd in de `REVIEW_STYLES` mapping in imxInsights.

| Type              | Kleurcode | Omschrijving                              |
|-------------------|-----------|-------------------------------------------|
| ✅ **OK**            | `#80D462` | In orde, goedgekeurd                      |
| ✅ **OK met opm**    | `#66FF99` | In orde met een opmerking                 |
| ❌ **NOK**           | `#FF9999` | Niet in orde                              |
| ❓ **VRAAG**         | `#F1F98F` | Vraag of onduidelijkheid                  |
| ⚠️ **Bestaande fout**| `#FFCC66` | Fout die al aanwezig was                  |
| 🤔 **Aannemelijk**   | `#E4DFEC` | Lijkt juist, maar niet 100% gecontroleerd |
| 🔧 **TODO**          | `#F2CEEF` | Nog na te kijken of uit te voeren         |

> **🎯 Let op:** de stylen moeten overeenkomen met de imxInsights **Named Styles** en kunnen afwijken.

---

##### 📌 Belangrijke Opmerkingen

- Witte (`#FFFFFF`) of zwarte (`#000000`) cellen worden genegeerd.
- Header-opmerkingen gelden automatisch voor onderliggende gekleurde cellen, zolang deze geen eigen commentaar bevatten.

---