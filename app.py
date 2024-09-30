from flask import Flask, render_template, request, redirect, url_for
import time
import random

app = Flask(__name__)

def calcul_checksum(check):
    checksum = 0
    for char in check:
        checksum ^= ord(char)
    return f"{checksum:02X}"

def analyser_gpgga(gpgga):
    parties = gpgga.split(',')
    temps = parties[1]
    latitude = parties[2]
    direction_latitude = parties[3]
    longitude = parties[4]
    direction_longitude = parties[5]
    qualite = parties[6]
    satellites = parties[7]
    altitude = parties[9]
    
    return {
        'temps': temps,
        'latitude': latitude,
        'direction_latitude': direction_latitude,
        'longitude': longitude,
        'direction_longitude': direction_longitude,
        'qualite': qualite,
        'satellites': satellites,
        'altitude': altitude
    }

def generer_gpgsa(donnees_gpgga):
    mode = "A"
    fix_type = donnees_gpgga['qualite']
    prns = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    prns = prns[:int(donnees_gpgga['satellites'])]
    while len(prns) < 12:
        prns.append('')
    pdop = round(random.uniform(1, 1.9), 1)
    hdop = round(random.uniform(1, 1.9), 1)
    vdop = round(random.uniform(1, 1.9), 1)
    gpgsa = f"$GPGSA,{mode},{fix_type}," + ",".join(prns) + f",{pdop},{hdop},{vdop}*30"
    return gpgsa

def generer_gprmc(donnees_gpgga):
    maintenant = time.strftime("%H%M%S", time.gmtime())
    status = 'A'
    latitude = f"{random.randint(0, 89)}{random.uniform(0, 59.999):06.3f},N"
    longitude = f"{random.randint(0, 179)}{random.uniform(0, 59.999):06.3f},E"
    vitesse = f"{random.uniform(0, 100):05.1f}"
    angle = f"{random.uniform(0, 360):05.1f}"
    date = time.strftime("%d%m%y", time.gmtime())
    variationMagn = f"{random.uniform(0, 15):05.1f},W"
    gprmc = f"GPRMC,{maintenant},{status},{latitude},{longitude},{vitesse},{angle},{date},{variationMagn}"
    checksum = calcul_checksum(gprmc)

    return f"${gprmc}*{checksum}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convertir', methods=['POST'])
def convertir():
    message_gpgga = request.form['message_gpgga']
    donnees_gpgga = analyser_gpgga(message_gpgga)
    
    trame_gpgsa = generer_gpgsa(donnees_gpgga)
    trame_gprmc = generer_gprmc(donnees_gpgga)
    

    with open("trames_nmea.txt", "w") as fichier:
        fichier.write(f"{message_gpgga}\n")
        fichier.write(f"{trame_gpgsa}\n")
        fichier.write(f"{trame_gprmc}\n")
    
    return render_template('resultat.html', gpgsa=trame_gpgsa, gprmc=trame_gprmc)

@app.route('/trames')
def afficher_trames():

    with open("trames_nmea.txt", "r") as fichier:
        contenu = fichier.readlines()
    return render_template('trames.html', contenu=contenu)

if __name__ == '__main__':
    app.run(debug=True)
