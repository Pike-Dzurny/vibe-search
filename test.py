from transformers import ClapModel, ClapProcessor
processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
print("clap loaded successfully")