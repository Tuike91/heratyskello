import time
import requests
import socketio
from grove.grove_led import GroveLed
from grove.display.jhd1802 import JHD1802
import RPi.GPIO as GPIO
from datetime import datetime, timedelta

# SocketIO-yhteys
sio = socketio.Client()

# GPIO-asetukset
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
button_pin = 6
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Komponentit
buzzer = GroveLed(16)
led = GroveLed(5)

# Määritetään lcd globaaliin tilaan
lcd = None

def initialize_lcd():
    global lcd
    lcd = JHD1802()  # Alustetaan lcd näyttö

def write_lcd_row(lcd, row, text):
    lcd.setCursor(0, row)
    lcd.write(f"{text:<16}")

def write_lcd_row2(lcd, row, text):
    lcd.setCursor(1, row)
    lcd.write(f"{text:<16}")

def clear_lcd(lcd):
    lcd.clear()

def get_alarm_time():
    try:
        res = requests.get("https://heratyskello7.azurewebsites.net/hae_heratys")
        if res.status_code == 200:
            data = res.json()
            aika = data['aika']
            teksti = data["teksti"]
            return aika.strip(), teksti.strip()
        else:
            print("Virhe Azuressa:", res.status_code)
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Virhe verkossa: {e}")
        return None, None

def activate_alarm():
    print("Herätys on käynnissä!")
    while True:
        buzzer.on()
        led.on()
        time.sleep(0.5)
        led.off()
        buzzer.off()
        time.sleep(0.5)

        if GPIO.input(button_pin) == GPIO.LOW:
            print("Herätys sammutettu napin painalluksesta")
            buzzer.off()
            led.off()
            break

@sio.event
def connect():
    print("Liitetty palvelimeen!")

@sio.event
def disconnect():
    print("Yhteys katkaistu!")

@sio.event
def heratys_paivittynyt(data):
    # Kun herätysaika päivittyy, päivitä LCD-näyttö ja tarkista herätysaika
    print(f"Herätysaika päivitetty: {data['aika']} - {data['teksti']}")
    alarm_time_str = data['aika']
    teksti = data['teksti']

    # Aseta herätysaika ja odota
    now = datetime.now()
    try:
        alarm_time = datetime.strptime(alarm_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
    except ValueError:
        print("Virheellinen aikamuoto Azuresta:", alarm_time_str)
        return

    if alarm_time < now:
        # Jos aika on mennyt jo, oletetaan että se on seuraavana päivänä
        alarm_time += timedelta(days=1)

    wait_seconds = (alarm_time - now).total_seconds()
    print(f"Herätysaika asetettu: {alarm_time_str}, odotetaan {wait_seconds:.0f} sekuntia.")

    write_lcd_row(lcd, 0, f"Nyt: {now.strftime('%H:%M')}")
    write_lcd_row2(lcd, 0, f"Heratys: {alarm_time_str}")

    # Odotetaan seuraavaan herätykseen
    while wait_seconds > 0:
        current_time = datetime.now().strftime('%H:%M')
        write_lcd_row(lcd, 0, f"Aika: {current_time}")
        time.sleep(min(60, wait_seconds))  # nukutaan korkeintaan 1 min kerrallaan
        wait_seconds = (alarm_time - datetime.now()).total_seconds()
    
    current_time = datetime.now().strftime('%H:%M')
    write_lcd_row(lcd, 0, f"Aika: {current_time}")
    write_lcd_row2(lcd, 0, teksti)

    activate_alarm()

def main():
    initialize_lcd()  # Alustetaan LCD ennen yhteyden muodostamista
    sio.connect("https://heratyskello7.azurewebsites.net")  # Yhdistetään Azure WebSocket-palvelimeen

    # Tämä pysyy päällä ja odottaa viestejä
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
