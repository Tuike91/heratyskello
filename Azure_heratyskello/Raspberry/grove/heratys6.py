import time
import requests
from grove.factory import Factory
from grove.grove_led import GroveLed
from grove.display.jhd1802 import JHD1802

# Grove-komponenttien alustaminen
buzzer = Factory.getGpioWrapper("Buzzer", 16)  # Buzzeri D3 porttiin
led = GroveLed(5)
button = Factory.getButton("GPIO-LOW", 6)  # Button on GPIO pin 6

# LCD-näyttö
def initialize_lcd():
    return JHD1802()

def write_lcd_row(lcd, row, text):
    lcd.setCursor(0, row)
    lcd.write(f"{text:<16}")

def write_lcd_row2(lcd, row, text):
    lcd.setCursor(1, row)
    lcd.write(f"{text:<16}")

def clear_lcd(lcd):
    lcd.clear()

# ThingsPeak API-asetukset
api_key = "0J8XLC93667WYU8H"
channel_id = "2824504"
thingspeak_url = f"https://api.thingspeak.com/channels/{channel_id}/fields/1.json"

def get_alarm_time():
    """Haetaan herätysaika ThingsPeakistä"""
    try:
        response = requests.get(thingspeak_url + f"?api_key={api_key}&results=1")
        if response.status_code == 200:
            data = response.json()
            alarm_time = data['feeds'][0]['field1']
            return alarm_time
        else:
            print("Virhe ThingsPeakissä")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Virhe verkossa: {e}")
        return None

def activate_alarm():
    """Aktivoi herätyksen ja odottaa napin painallusta pysäyttääkseen sen"""
    print("Herätys on käynnissä!")
    while True:
        buzzer.on()
        led.on()  # LED päälle
        time.sleep(0.5)  # Soi ja vilkkuu 0.5 sekuntia
        led.off()
        buzzer.off()
        time.sleep(0.5)  # Tauko 0.5 sekuntia

        if button.is_pressed():  # Tarkista, onko nappi painettu
            print("Herätys sammutettu napin painalluksesta")
            buzzer.off()
            led.off()  # Pysäytetään LED
            break  # Poistutaan silmukasta ja lopetetaan herätys

def main():
    lcd = initialize_lcd()

    while True:
        alarm_time = get_alarm_time()
        if alarm_time:
            current_time = time.strftime('%H:%M:%S')  # Hanki nykyinen aika
            print(f"Nykyinen aika: {current_time}, Herätysaika: {alarm_time}")
            
            # Näytetään herätysaika LCD-näytöllä
            write_lcd_row2(lcd, 0, f"Heratys:{alarm_time}")

            # Varmistetaan, että vertaamme aikaa oikein (formatointi)
            if current_time == alarm_time:
                print("Aika herätykselle!")
                write_lcd_row2(lcd, 0, "Heratys!")
                activate_alarm()
                # Odotetaan napin painallusta ennen uuden herätyksen asettamista
                while not button.is_pressed():
                    time.sleep(0.1)
            else:
                write_lcd_row(lcd, 0, current_time)

        time.sleep(1)

if __name__ == '__main__':
    main()
