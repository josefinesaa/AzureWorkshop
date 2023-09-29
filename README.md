# AzureWorkshop

I denne workshoppen skal du lære hvordan man bruker Azure Blob Storage og Azure Functions. Les mer her ....

Du skal lage et program som automatisk laster opp bilder til et Azure Blob Storage og bruke en Blob Trigger til å få varsel på når nye bilder er lastet opp. 

# Opplasting av filer til Azure Blob Storage

Dette er en enkel Python-funksjon som brukes til å laste opp filer til Azure Blob Storage. Denne koden kan være nyttig når du vil overføre filer til en Azure Blob Storage-container.


```python
{
  import os
  import yaml
  from azure.storage.blob import ContainerClient
  
  
  def load_config():
      dir_root = os.path.dirname(os.path.abspath(__file__))
      with open(dir_root + "/config.yaml", "r") as yamlfile:
          return yaml.load(yamlfile, Loader=yaml.FullLoader)
      
  
  def get_files(dir):
      with os.scandir(dir) as entries:
          for entry in entries:
              if entry.is_file() and not entry.name.startswith("."):
                  yield entry
  
  def upload(files, connection_string, container_name):
      #print("files: ", files, "Connection String:", config["azure_storage_connectionstring"], "Container name:", config["images_container_name"])
      container_client = ContainerClient.from_connection_string(connection_string, container_name)
      print("Uploading files to blob storage...")
      
      for file in files:
          blob_name = os.path.basename(file.path)  # Use the base filename as the blob name
          blob_client = container_client.get_blob_client(blob_name)
  
          if not blob_client.exists():
              with open(file.path, "rb") as data:
                  blob_client.upload_blob(data)
                  print(f'{blob_name} uploaded to blob storage')
                  #os.remove(file)
                  #print(f'{blob_name} removed from folder')
          else:
              print(f'{blob_name} already exists in the container. Skipping upload.')
  config = load_config()
  images = get_files(config["source_folder"] + "/images")
  upload(images, config["azure_storage_connectionstring"], config["images_container_name"])

}

```

## Bruk

Før du bruker denne koden, må du sørge for at du har riktig konfigurasjon i en konfigurasjonsfil, for eksempel `config.yaml`. Her er en eksempelkonfigurasjon:

```yaml
{
  "azure_storage_connectionstring": "din_azure_connection_string",
  "images_container_name": "din_container_navn",
  "source_folder": "din_kilde_mappe"
}
```

Du må endre `"din_azure_connection_string"`, `"din_container_navn"` og `"din_kilde_mappe"` til de faktiske verdiene som passer for ditt prosjekt. Sørg også for at du har riktig mappestruktur og filnavn for moduler og konfigurasjonsfiler.


# Azure Funtion - Blob Trigger

Følge denne guiden for å opprette en blob trigger: https://learn.microsoft.com/en-us/training/modules/execute-azure-function-with-triggers/8-create-blob-trigger







