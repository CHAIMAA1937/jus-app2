
import unicodedata


def normaliser(texte):
    texte = texte.lower().strip()

    texte = unicodedata.normalize("NFD", texte)

    texte = "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )

    return texte


def repondre(message):

    question = normaliser(message)

    if not question:
        return "Bonjour ! Posez-moi une question sur l'application."

    # Salutations
    if any(mot in question for mot in ["bonjour", "salut", "bonsoir", "hello"]):
        return (
            "Bonjour ! Je suis l'assistant de votre application "
            "de concentration du jus. Comment puis-je vous aider ?"
        )

    # Présentation de l'application
    if "application" in question or "fonctionnement" in question:
        return (
            "Cette application permet de simuler un procédé de "
            "concentration du jus. Elle calcule les masses, les "
            "quantités de chaleur et les bilans du procédé."
        )

    # Débit initial
    if "m0" in question or "debit du jus brut" in question:
        return (
            "m0 représente le débit massique initial du jus brut, "
            "exprimé en kg/h."
        )

    # Fractions
    if "x0" in question:
        return "x0 représente la fraction insoluble du jus brut."

    if "y0" in question:
        return "y0 représente la fraction soluble du jus brut."

    if "meau" in question or "fraction d'eau" in question:
        return "meau représente la fraction d'eau dans le jus brut."

    # Résidus
    if "mresidus" in question or "residus" in question:
        return (
            "mResidus représente le débit massique des résidus "
            "éliminés pendant le procédé, en kg/h."
        )

    # Recyclage
    if "recyclage" in question or "xr" in question or "mr" in question:
        return (
            "mR représente le débit du jus concentré recyclé. "
            "xr représente sa fraction soluble."
        )

    # Concentration finale
    if "x4" in question or "concentration finale" in question:
        return (
            "x4 représente la concentration finale définie "
            "comme paramètre dans le formulaire."
        )

    # Températures
    if any(mot in question for mot in ["temperature", "t2", "t3", "t4", "t5"]):
        return (
            "Les températures T2, T3, T4 et T5 représentent les "
            "températures des différentes étapes du procédé : "
            "chauffage et refroidissement."
        )

    # Chaleur
    if any(mot in question for mot in ["q3", "q4", "q5", "chaleur"]):
        return (
            "Q3, Q4 et Q5 représentent les quantités de chaleur "
            "calculées aux différentes étapes thermiques du procédé."
        )

    # Eau évaporée
    if "evaporation" in question or "mv" in question or "eau evaporee" in question:
        return (
            "mv représente la masse d'eau évaporée pendant "
            "l'opération de concentration."
        )

    # Bilans matière
    if "bilan" in question:
        return (
            "Le bilan matière permet de comparer les masses entrantes "
            "et sortantes. L'application calcule également le bilan "
            "des matières solubles."
        )

    # Historique
    if "historique" in question:
        return (
            "La page Historique permet de consulter les simulations "
            "déjà réalisées et enregistrées dans la base de données."
        )

    # Excel
    if "excel" in question or "export" in question:
        return (
            "Vous pouvez télécharger l'historique des simulations "
            "au format Excel en utilisant le bouton d'exportation."
        )

    # Authentification
    if any(mot in question for mot in ["connexion", "connecter", "login", "inscription"]):
        return (
            "L'application possède un système Sign Up et Sign In. "
            "Chaque navigateur peut être reconnu après sa première "
            "connexion lorsque Remember this device est activé."
        )

    # Remerciement
    if "merci" in question:
        return "Avec plaisir ! Je reste à votre disposition."

    # Réponse par défaut
    return (
        "Je n'ai pas compris votre question. Vous pouvez me demander "
        "des informations sur les paramètres du procédé, les bilans "
        "matière, la concentration, l'historique ou l'export Excel."
    )
