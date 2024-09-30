from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random

app = Flask(__name__)

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
    # pdop = "1.0"
    # hdop = "1.0"
    # vdop = "1.0"
    # return "$GPGSA,A,3,04,05,..,29,31,.,1.8,1.0,1.5*30"

def generer_gprmc(donnees_gpgga):
    maintenant = datetime.utcnow().strftime("%H%M%S.000")
    lat = donnees_gpgga['latitude']
    dir_lat = donnees_gpgga['direction_latitude']
    lon = donnees_gpgga['longitude']
    dir_lon = donnees_gpgga['direction_longitude']
    vitesse = "0.5"
    date = datetime.utcnow().strftime("%d%m%y")
    
    return f"$GPRMC,{maintenant},A,{lat},{dir_lat},{lon},{dir_lon},{vitesse},054.7,{date},,,A*7C"

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
        fichier.write(f"GPGGA: {message_gpgga}\n")
        fichier.write(f"GPGSA: {trame_gpgsa}\n")
        fichier.write(f"GPRMC: {trame_gprmc}\n")
    
    return render_template('resultat.html', gpgsa=trame_gpgsa, gprmc=trame_gprmc)

@app.route('/trames')
def afficher_trames():

    with open("trames_nmea.txt", "r") as fichier:
        contenu = fichier.readlines()
    return render_template('trames.html', contenu=contenu)

if __name__ == '__main__':
    app.run(debug=True)
