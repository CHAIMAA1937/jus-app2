
def calculer_procede(
    m0=1000,
    x0=0.02,
    y0=0.10,
    meau=0.88,
    mResidus=20,
    mR=100,
    xr=0.40,
    Cp=3.8,
    T2=20,
    T3=80,
    x4=0.40,
    T4=80,
    T5=25,
    lambda_v=2300
):
    # VERIFICATION DES DONNEES

    if m0 <= 0 or mR < 0 or mResidus < 0:
        raise ValueError("Debit invalide.")

    if mResidus >= m0:
        raise ValueError("Les residus doivent etre inferieurs a m0.")

    if not (0 <= x0 <= 1 and 0 < y0 <= 1 and 0 <= meau <= 1):
        raise ValueError("Fractions massiques invalides.")

    if abs(x0 + y0 + meau - 1) > 1e-6:
        raise ValueError("La somme des fractions doit etre egale a 1.")

    if not (0 < xr <= 1 and 0 < x4 <= 1):
        raise ValueError("Concentrations invalides.")

    if Cp <= 0 or lambda_v <= 0:
        raise ValueError("Proprietes thermiques invalides.")
    
    # OPERATION 1 : FILTRATION
    m1 = m0 - mResidus
    y1 = (y0 * m0) / m1
    # OPERATION 2 : MELANGE
    m2 = m1 + mR
    y2 = (m1 * y1 + mR * xr) / m2
    # OPERATION 3 : CHAUFFAGE
    Q3 = m2 * Cp * (T3 - T2) / 3600
    # OPERATION 4 : EVAPORATION
    m4 = (m2 * y2) / x4
    mv = m2 - m4
    if mv < -1e-9:
        raise ValueError("Concentration finale incompatible avec le bilan.")

    Q4 = (mv * lambda_v) / 3600
    # OPERATION 5 : REFROIDISSEMENT
    Q5 = m4 * Cp * (T4 - T5) / 3600
    # BILAN GLOBAL DE MATIERE
    entrees = m0 + mR
    sorties = mResidus + mv + m4
    erreur_bilan_global = entrees - sorties
    # BILAN DES MATIERES SOLUBLES
    solubles_entrantes = (m0 * y0) + (mR * xr)
    solubles_sortantes = m4 * x4
    erreur_bilan_solubles = solubles_entrantes - solubles_sortantes
    # RESULTATS
    
    resultats = {
    "m1": m1,
    "y1": y1,
    "m2": m2,
    "y2": y2,
    "Q3": Q3,
    "m4": m4,
    "mv": mv,
    "Q4": Q4,
    "Q5": Q5,
    "entrees": entrees,
    "sorties": sorties,
    "erreur_bilan_global": erreur_bilan_global,
    "solubles_entrantes": solubles_entrantes,
    "solubles_sortantes": solubles_sortantes,
    "erreur_bilan_solubles": erreur_bilan_solubles
    }

    return resultats


# TEST DU PROGRAMME

if __name__ == "__main__":

    resultats = calculer_procede()

    print("\n===== RESULTATS DU PROCEDE =====")

    for nom, valeur in resultats.items():
        print(nom, ":", round(valeur, 4))

    print("\n===== VERIFICATION DES BILANS =====")

    if abs(resultats["erreur_bilan_global"]) < 1e-6:
       print("Bilan global respecte.")

    if abs(resultats["erreur_bilan_solubles"]) < 1e-6: 
       print("Bilan des matieres solubles respecte.")
