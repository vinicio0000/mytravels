import os
import json
import exifread

CARTELLA_FOTO = "foto"
FILE_OUTPUT = "dati.json"

def converti_in_gradi(valore):
    """
    Converte i dati GPS EXIF (Gradi, Minuti, Secondi) in formato decimale.
    """
    try:
        d = float(valore.values[0].num) / float(valore.values[0].den)
        m = float(valore.values[1].num) / float(valore.values[1].den)
        s = float(valore.values[2].num) / float(valore.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None

def estrai_gps(percorso_foto):
    """
    Estrae latitudine e longitudine dai tag EXIF dell'immagine.
    """
    try:
        with open(percorso_foto, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            
            lat_tag = tags.get('GPS GPSLatitude')
            lat_ref = tags.get('GPS GPSLatitudeRef')
            lon_tag = tags.get('GPS GPSLongitude')
            lon_ref = tags.get('GPS GPSLongitudeRef')

            if lat_tag and lat_ref and lon_tag and lon_ref:
                lat = converti_in_gradi(lat_tag)
                lon = converti_in_gradi(lon_tag)

                if lat is not None and lon is not None:
                    # Direzione Latitudine (N/S)
                    if lat_ref.values[0] != 'N':
                        lat = -lat

                    # Direzione Longitudine (E/W)
                    if lon_ref.values[0] != 'E':
                        lon = -lon

                    return lat, lon
    except Exception as e:
        print(f"Errore nella lettura di {percorso_foto}: {e}")
        
    return None, None

def genera():
    lista_dati = []

    if not os.path.exists(CARTELLA_FOTO):
        print(f"Errore: La cartella '{CARTELLA_FOTO}' non esiste.")
        return

    # Scansione di tutti i file nella cartella foto
    for file in os.listdir(CARTELLA_FOTO):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            percorso_completo = os.path.join(CARTELLA_FOTO, file)
            lat, lon = estrai_gps(percorso_completo)

            if lat is not None and lon is not None:
                
                # --- CORREZIONE LONGITUDINE MANUALE (Formato 0-360 -> GPS -180/+180) ---
                if lon > 180:
                    lon = lon - 360
                # ---------------------------------------------------------------------

                nome_senza_estensione, _ = os.path.splitext(file)
                
                lista_dati.append({
                    "nome": nome_senza_estensione,
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "foto": f"{CARTELLA_FOTO}/{file}"
                })
                print(f"✅ OK: {file} -> Lat: {round(lat, 6)}, Lon: {round(lon, 6)}")
            else:
                print(f"⚠️ Nessun dato GPS trovato in: {file}")

    # Salva il file JSON formattato
    with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(lista_dati, f, ensure_ascii=False, indent=2)

    print(f"\nOperazione completata! Creato '{FILE_OUTPUT}' con {len(lista_dati)} foto georeferenziate.")

if __name__ == "__main__":
    genera()