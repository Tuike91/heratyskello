import requests
import time
from datetime import datetime

print("Herätyskello käynnissä...")

while True:
    try:
        res = requests.get("https://heratyskello7.azurewebsites.net/hae_heratys")
        data = res.json()
        aika = data["aika"]
        teksti = data["teksti"]

        nyt = datetime.now().strftime("%H:%M")
        print(f"Nyt: {nyt}, Herätys: {aika}")

        if nyt == aika:
            print("\n\nHERÄTYS:", teksti)
            break

    except Exception as e:
        print("Virhe:", e)

    time.sleep(30)
