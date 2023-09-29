# AzureWorkshop

I denne workshoppen skal du lære hvordan man bruker Azure Blob Storage og Azure Functions. Les mer her ....

Du skal lage en applikasjon hvor du kan laste opp bilder til en Azure Blob Storage og bruke en Blob Trigger til å få varsel på når nye bilder er lastet opp. 

# Før du begynner

Før du starter, må du sørge for at du har følgende krav oppfylt:

- Python 3.x installert på datamaskinen din.
- Pip installert for å administrere Python-pakker.
- En Azure-konto.
- Visual Studio Code installert på datamaskinen din.


# Azure Funtion - Blob Trigger

Følg steget 'Create an Azure Function App' fra følgende guide: https://learn.microsoft.com/en-us/training/modules/execute-azure-function-with-triggers/4-create-timer-trigger

Deretter følger du denne guiden for å opprette en blob trigger i Azure Portal (du trenger ikke fullføre det siste steget "Create a blob", siden vi skal gjøre dette på en annen måte med stegene forklart nedenfor): https://learn.microsoft.com/en-us/training/modules/execute-azure-function-with-triggers/8-create-blob-trigger

Etter å ha fulgt denne guiden kan du åpne en ny fane med Azure portalen og gå inn i Storage-Accounten som du koblet blob-funksjonen til. Deretter i venstre meny går du inn i "Access Key" og under "Connection String" så kopierer du verdien og lagrer denne til senere.

# Installering og oppsett av Python kode for opplasting av bilder

Det første du starter med å gjøre er å opprette et prosjekt i VS Code. 
Deretter kjører du følgende kommando i terminalen for å installere Flask og Azure Storage Blob SDK.

```
pip install Flask azure-storage-blob
```

## HTML-fil

I VS Code prosjektet lager du en mappe kalt "templates" og i denne mappen oppretter du en html fil kalt 'index.html', som inneholder følgende kode:
```
<!DOCTYPE html>
<html>
<head>
    <title>Image Upload</title>
</head>
<body>
    <h1>Image Upload</h1>
    <form method="POST" enctype="multipart/form-data" action="/upload">
        <input type="file" name="image" accept="image/*" required>
        <input type="submit" value="Upload">
    </form>
</body>
</html>
```
## Yaml-fil

Du må også opprette en yaml-fil i prosjektet, kalt 'config.yaml'. Legg til følgende kode i  konfigurasjonsfilen:

```yaml
{
  "azure_storage_connectionstring": "din_azure_connection_string",
  "images_container_name": "din_container_navn"
}
```

Du må endre `"din_azure_connection_string"`, `"din_container_navn"` og `"din_kilde_mappe"` til de faktiske verdiene som passer for ditt prosjekt. `"din_azure_connection_string"` er verdien du tidligere lagret fra Access Key, og `"din_container_navn"` er navnet på containeren som du opprettet i første steg (samples-workitems).

Sørg også for at du har riktig mappestruktur og filnavn for moduler og konfigurasjonsfiler.

## Python-fil

Deretter oppretter du en python fil i prosjektet kalt 'app.py'. 

Her importerer du først de nødvendige biblotekene og modulene:

```
from flask import Flask, request, render_template, redirect, url_for
import os
import yaml
from azure.storage.blob import ContainerClient
```

Deretter oppretter du en Flask applikasjon:

```
app = Flask(__name__)

```
Så lager du en funksjon for å laste inn konfigurasjonsdata fra config.yaml-filen.

```
def load_config():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    with open(dir_root + "/config.yaml", "r") as yamlfile:
        return yaml.load(yamlfile, Loader=yaml.FullLoader)
```

Definerer en rute som viser opplastingsgrensesnittet (index.html)
```
@app.route('/')
def index():
    return render_template('index.html')

```
Så lager du funksjonen for å laste opp bilder til Azure Blob Storage.

Først defineres en rute som håndterer bildeopplasting ved HTTP POST-forespørsler. 
Deretter lastes konfigurasjonsdataen inn, og en klient for Azure Blob Storage-beholderen opprettes. 

```
@app.route('/upload', methods=['POST'])
def upload():
    config = load_config()
    container_client =   ContainerClient.from_connection_string(config["azure_storage_connectionstring"], config["images_container_name"])
```

I upload-funksjonen legger du til et sjekk om en fil med navn 'image' er inkludert i forespørselenm eller om filnavnet er tomt (ingen fil valgt). 

```
    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    if image.filename == '':
        return redirect(request.url)

```

Bruker det opprinnelige filnavnet eller genererer et unikt navn for bloben
   

```
    blob_name = image.filename
    blob_client = container_client.get_blob_client(blob_name)
```
Sjekker om bloben allerede eksisterer i beholderen
    

```
if not blob_client.exists():
        # Lagrer den opplastede filen i Azure Blob Storage
        blob_client.upload_blob(image)
        return "Image uploaded successfully."
    else:
        return "Image already exists in the container. Skipping upload."
```

Starter Flask-applikasjonen hvis dette er hovedprogrammet.

```
if __name__ == '__main__':
    app.run(debug=True)
```


Til slutt vil python koden se slik ut:

```python
{
  from flask import Flask, request, render_template, redirect, url_for
import os
import yaml
from azure.storage.blob import ContainerClient

app = Flask(__name__)

def load_config():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    with open(dir_root + "/config.yaml", "r") as yamlfile:
        return yaml.load(yamlfile, Loader=yaml.FullLoader)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    config = load_config()
    container_client = ContainerClient.from_connection_string(config["azure_storage_connectionstring"], config["images_container_name"])

    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    if image.filename == '':
        return redirect(request.url)

    blob_name = image.filename
    blob_client = container_client.get_blob_client(blob_name)

    if not blob_client.exists():
        blob_client.upload_blob(image)

        return "Image uploaded successfully."
    else:
        return "Image already exists in the container. Skipping upload."

if __name__ == '__main__':
    app.run(debug=True)

}

```

## Kjøre kode

For å kjøre python-koden må du kjøre denne kommandoen. Kontroller at du er i samme mappe som app.py-filen. Her vil du få opp en url i terminalen med Flask-applikasjonen. 

```
 python -m flask run --no-debug
```


## Teste Blob Trigger funksjonen

Kontroller at du har aktivert blobtrigger-funksjonen i Azure portalen. Dette gjør du ved å følge steget "Turn on your blob trigger" i guiden gitt tidligere (https://learn.microsoft.com/en-us/training/modules/execute-azure-function-with-triggers/8-create-blob-trigger).

Nå er du klar for å teste at funksjonen fungerer som den skal.
Gå inn i url-en til Flask-applikasjonen (sørg for at den er oppe og kjører), og last opp et bilde her. Når du får melding om at bildet er lastet opp, går du tilbake Deretter til blob funksjonen i Azure portalen og nå vil du se at en blob trigger er utført. 

Nå kan du selv utforske litt hvordan dette fungerer ved å endre 'run.csx' filen som du ønsker. Her er noen forslag til ting du kan prøve:

- Legg til timestamp: Legg til tidspunkt for når bildene blir lastet opp. 
- Legg til logger: Legg til logger eller Console.WriteLine-setninger for å logge hendelser og meldinger i funksjonen. Dette hjelper med feilsøking og gir en bedre forståelse av hvordan funksjonen blir utløst og kjører.
- Endre filtype: Endre Blob Trigger-funksjonen for å reagere på en bestemt type filer. For eksempel kan du filtrere ut bestemte filtyper som .jpg, .png eller .pdf.
- Legg til ekstra behandling: Etter at Blob Trigger-funksjonen har blitt utløst, kan deltakerne legge til mer logikk for å behandle filene. Dette kan inkludere omforming, overføring av filer til en annen beholder eller utføre spesifikke operasjoner basert på filens innhold.
- Behandle flere beholdere: Deltakerne kan tilpasse Blob Trigger-funksjonen til å reagere på flere beholdere i stedet for bare én. Dette gjøres ved å definere flere Blob Triggers med ulike bindings.
- Endre triggere: Azure Functions støtter ulike typer triggere, ikke bare Blob Trigger. Deltakerne kan eksperimentere med andre triggere, som Timer Trigger eller Queue Trigger, og kombinere dem med Blob Trigger for å oppnå mer kompleks oppførsel.
- Tidsplanlegging: Utforsk muligheten til å planlegge når Blob Trigger-funksjonen skal kjøre ved å bruke Time Trigger. Dette lar deg kontrollere når funksjonen skal overvåke beholdere for nye filer.



(Dette gjør du ved å gå inn i Function App-en du opprettet tidligere, og under funksjoner finnner du funksjonen du opprettet tidligere, antagelivis kalt 'BlobTrigger1'. Trykk på denne funsjonen og deretter trykker du på "Code + Test" fra menyen i venstre under "Developer". Så trykker du på pilen ned ved siden av "App Insights Logs" og bytter til "Filesystem Logs". Trykk OK på pop opp vinduet. Hvis alt er som det skal vil du se "Connected!" på skjermen. )











