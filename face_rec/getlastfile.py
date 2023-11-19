import os

def son_dosyanin_tam_yolu(klasor_yolu):
    try:
        if not os.path.exists(klasor_yolu) or not os.path.isdir(klasor_yolu):
            return False

        dosya_listesi = os.listdir(klasor_yolu)

        if not dosya_listesi:
            return False

        son_dosya = None
        son_degistirme_zamani = 0

        for dosya in dosya_listesi:
            dosya_yolu = os.path.join(klasor_yolu, dosya)
            if os.path.isfile(dosya_yolu):
                degistirme_zamani = os.path.getmtime(dosya_yolu)
                if degistirme_zamani > son_degistirme_zamani:
                    son_dosya = dosya_yolu
                    son_degistirme_zamani = degistirme_zamani

        return son_dosya if son_dosya is not None else False
    except Exception:
        return False
