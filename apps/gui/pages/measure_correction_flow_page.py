from nicegui.element import Element

from apps.gui.components.flows.measure_correction import MeasureCorrectionTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class MeasureCorrectionFlowPage:
    def __init__(self):
        help_text = """
        ### ℹ️ Measure Correction Flow

        Deze tool begeleidt je stap voor stap bij het analyseren en corrigeren van measures in een IMX-bestand.
        Deze actie kan leiden tot een andere set aan upadate puics, deze worden **NIET** meegenomen in de processed output.
        
        *Alleen de NewSituation waarden worden aangepast, bij elke aanpassing wordt de metadata van dat object aangepast (niet die van de ouder objecten)!*
                
        </br>
        
        **Workflow Overzicht:**

        1️⃣ **Upload Vereiste en Optionele Bestanden**  
        
        - **IMX-bestand**: Het IMX-project dat je wilt analyseren en corrigeren.  
        - **Drempelwaarde**: De drempelwaarde in meters op voor het automatisch detecteren van te corrigeren waarden.  
        - **JSON-GR-bestand** (Optioneel): Het Naiade GR JSON bestand om 'contextgebied'-objecten automatisch te classificeren en uit te sluiten van correcties.  

        </br>
        
        2️⃣ **Controleer en Markeer Revisies**
          
        - Na de analyse kun je het automatisch gegenereerde revisie-Excelbestand downloaden.  
        - Open het revisiebestand en markeer de rijen die correctie nodig hebben door de kolom `processing required` op `True` te zetten.  
        - Upload het aangepaste Excelbestand om verder te gaan.
        
        *Tip: mocht je een oud revisie bestand willen gebruiken dan kan je die ook gelijk uploaden. 
        Als er een match tussen puic / path en oude waarde is gaat dit goed. 
        Na het uitvoeren van de revisie kan je na gaan in de process excel welke wel en welke niet zijn verwerkt.*

        </br>

        3️⃣ **Controleer Revisieresultaten**  
        
        - Na verwerking kun je het bijgewerkte IMX-bestand downloaden als een ZIP-archief.  
        - Je kunt ook een Diff-rapport genereren en downloaden waarin het originele en het verwerkte IMX-bestand worden vergeleken.

        </br>

        Wanneer je alle stappen hebt doorlopen klik dan op  **Voltooien** om de tool te resetten en indien nodig een nieuw proces te starten.
        
        
        """

        def build_content(container: Element):
            MeasureCorrectionTool(container)

        ToolPanelWithHelp(
            title="IMX Measure Correction Flow",
            help_text=help_text,
            content_builder=build_content,
        )

