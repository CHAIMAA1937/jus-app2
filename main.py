
from io import BytesIO

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import (
    HTMLResponse,
    StreamingResponse,
    RedirectResponse
)

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from calculs import calculer_procede
from database import init_db, enregistrer_calcul, recuperer_calculs

from auth import (
    creer_utilisateur,
    authentifier_utilisateur,
    creer_appareil,
    recuperer_utilisateur_par_appareil,
    deconnecter_appareil
)
from pydantic import BaseModel
from chatbot import repondre

app = FastAPI(
    title="Application de concentration du jus",
    description="Calcul des opérations unitaires du procédé de concentration du jus",
    version="1.0"
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()
class MessageChat(BaseModel):
    message: str

# Vérifier si l'utilisateur est connecté
def utilisateur_connecte(request: Request):
    token = request.cookies.get("device_token")
    return recuperer_utilisateur_par_appareil(token)


# -----------------------------
# PAGE SIGN UP
# -----------------------------

@app.get("/register", response_class=HTMLResponse)
async def afficher_register(request: Request):

    if utilisateur_connecte(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"erreur": None}
    )


@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"erreur": "Les deux mots de passe ne correspondent pas."}
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"erreur": "Le mot de passe doit contenir au moins 8 caractères."}
        )

    try:
        creer_utilisateur(
            username=username.strip(),
            email=email.strip(),
            password=password
        )

        return RedirectResponse("/login", status_code=303)

    except ValueError as erreur:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"erreur": str(erreur)}
        )


# -----------------------------
# PAGE SIGN IN
# -----------------------------

@app.get("/login", response_class=HTMLResponse)
async def afficher_login(request: Request):

    if utilisateur_connecte(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"erreur": None}
    )


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    remember_device: str | None = Form(None)
):

    utilisateur = authentifier_utilisateur(login.strip(), password)

    if utilisateur is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"erreur": "Email, username ou mot de passe incorrect."}
        )

    # Créer un identifiant unique pour ce navigateur
    device_name = request.headers.get(
        "user-agent", "Navigateur inconnu"
    )[:250]

    token = creer_appareil(
        utilisateur["id"],
        device_name
    )

    response = RedirectResponse("/", status_code=303)

    # Cookie de reconnaissance de l'appareil
    options_cookie = {
        "key": "device_token",
        "value": token,
        "httponly": True,
        "secure": False,
        "samesite": "lax",
        "path": "/"
    }

    # Si Remember this device est coché,
    # le navigateur conserve le cookie pendant un an.
    if remember_device == "yes":
        options_cookie["max_age"] = 60 * 60 * 24 * 365

    response.set_cookie(**options_cookie)

    return response


# -----------------------------
# DECONNEXION
# -----------------------------

@app.get("/logout")
async def logout(request: Request):

    token = request.cookies.get("device_token")

    deconnecter_appareil(token)

    response = RedirectResponse("/login", status_code=303)

    response.delete_cookie(
        key="device_token",
        path="/"
    )

    return response


# -----------------------------
# PAGE D'ACCUEIL
# -----------------------------

@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):

    utilisateur = utilisateur_connecte(request)

    if utilisateur is None:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"utilisateur": utilisateur}
    )


# -----------------------------
# CALCUL DU PROCEDE
# -----------------------------

@app.post("/calculer", response_class=HTMLResponse)
async def calculer(
    request: Request,
    m0: float = Form(1000),
    x0: float = Form(0.02),
    y0: float = Form(0.10),
    meau: float = Form(0.88),
    mResidus: float = Form(20),
    mR: float = Form(100),
    xr: float = Form(0.40),
    Cp: float = Form(3.8),
    T2: float = Form(20),
    T3: float = Form(80),
    x4: float = Form(0.40),
    T4: float = Form(80),
    T5: float = Form(25),
    lambda_v: float = Form(2300)
):

    utilisateur = utilisateur_connecte(request)

    if utilisateur is None:
        return RedirectResponse("/login", status_code=303)

    try:
        r = calculer_procede(
            m0=m0, x0=x0, y0=y0, meau=meau,
            mResidus=mResidus, mR=mR, xr=xr,
            Cp=Cp, T2=T2, T3=T3, x4=x4,
            T4=T4, T5=T5, lambda_v=lambda_v
        )

        parametres = {
            "m0": m0,
            "x0": x0,
            "y0": y0,
            "meau": meau,
            "mResidus": mResidus,
            "mR": mR,
            "xr": xr,
            "Cp": Cp,
            "T2": T2,
            "T3": T3,
            "x4": x4,
            "T4": T4,
            "T5": T5,
            "lambda_v": lambda_v
        }

        enregistrer_calcul(parametres, r)

        return templates.TemplateResponse(
            request=request,
            name="resultats.html",
            context={"r": r, "utilisateur": utilisateur}
        )

    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))


# -----------------------------
# HISTORIQUE DES SIMULATIONS
# -----------------------------

@app.get("/historique", response_class=HTMLResponse)
async def historique(request: Request):

    utilisateur = utilisateur_connecte(request)

    if utilisateur is None:
        return RedirectResponse("/login", status_code=303)

    calculs = recuperer_calculs()

    return templates.TemplateResponse(
        request=request,
        name="historique.html",
        context={
            "calculs": calculs,
            "utilisateur": utilisateur
        }
    )


# -----------------------------
# EXPORT EXCEL
# -----------------------------

@app.get("/export-excel")
async def exporter_excel(request: Request):

    utilisateur = utilisateur_connecte(request)

    if utilisateur is None:
        return RedirectResponse("/login", status_code=303)

    calculs = recuperer_calculs()

    wb = Workbook()
    ws = wb.active
    ws.title = "Historique des calculs"

    colonnes = [
        ("ID", "id"),
        ("Date", "date_calcul"),
        ("Débit initial", "m0"),
        ("Fraction insoluble", "x0"),
        ("Fraction soluble", "y0"),
        ("Fraction eau", "meau"),
        ("Masse résidus", "mResidus"),
        ("Masse recyclage", "mR"),
        ("Fraction recyclage", "xr"),
        ("Capacité thermique", "Cp"),
        ("Température T2", "T2"),
        ("Température T3", "T3"),
        ("Fraction x4", "x4"),
        ("Température T4", "T4"),
        ("Température T5", "T5"),
        ("Chaleur latente", "lambda_v"),
        ("Masse m1", "m1"),
        ("Fraction y1", "y1"),
        ("Masse m2", "m2"),
        ("Fraction y2", "y2"),
        ("Chaleur Q3", "Q3"),
        ("Masse concentrée m4", "m4"),
        ("Eau évaporée mv", "mv"),
        ("Chaleur Q4", "Q4"),
        ("Chaleur Q5", "Q5"),
        ("Entrées", "entrees"),
        ("Sorties", "sorties"),
        ("Erreur bilan global", "erreur_bilan_global"),
        ("Solubles entrantes", "solubles_entrantes"),
        ("Solubles sortantes", "solubles_sortantes"),
        ("Erreur bilan solubles", "erreur_bilan_solubles")
    ]

    ws.append([titre for titre, cle in colonnes])

    for calcul in calculs:
        ws.append([calcul[cle] for titre, cle in colonnes])

    for cellule in ws[1]:
        cellule.font = Font(bold=True, color="FFFFFF")
        cellule.fill = PatternFill(
            start_color="176B55",
            end_color="176B55",
            fill_type="solid"
        )
        cellule.alignment = Alignment(horizontal="center")

    for colonne in ws.columns:
        lettre = colonne[0].column_letter
        ws.column_dimensions[lettre].width = 20

    fichier = BytesIO()
    wb.save(fichier)
    fichier.seek(0)

    return StreamingResponse(
        fichier,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=historique_simulations.xlsx"
        }
    )
# CHATBOT

# Afficher la page du chatbot
@app.get("/chatbot", response_class=HTMLResponse)
async def afficher_chatbot(request: Request):

    utilisateur = utilisateur_connecte(request)

    if utilisateur is None:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="chatbot.html",
        context={"utilisateur": utilisateur}
    )


# Recevoir une question et envoyer une réponse
@app.post("/chatbot")
async def discuter(
    request: Request,
    data: MessageChat
):

    utilisateur = utilisateur_connecte(request)

    if utilisateur is None:
        raise HTTPException(
            status_code=401,
            detail="Veuillez vous connecter."
        )

    reponse = repondre(data.message)

    return {"reponse": reponse}


import unicodedata


# Normaliser les questions : minuscules et suppression des accents
def normaliser(texte):
    texte = texte.lower().strip()

    texte = unicodedata.normalize("NFD", texte)

    texte = "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )

    return texte


# Générer une réponse au message de l'utilisateur
def repondre(message):

    question = normaliser(message)

    if not question:
        return "👋 Bonjour ! Posez-moi une question sur l'application. 😊"

    # 1. Salutations
    if any(mot in question for mot in ["bonjour", "salut", "bonsoir", "hello"]):
        return (
            "👋 Bonjour ! Je suis l'assistant virtuel de votre application "
            "de concentration du jus. 🍹\n\n"
            "😊 Comment puis-je vous aider aujourd'hui ?"
        )

    # 2. Présentation de l'application
    if "application" in question or "fonctionnement" in question:
        return (
            "🍹 Bienvenue dans notre application de concentration du jus !\n\n"
            "📊 Cette application permet de simuler un procédé de concentration "
            "du jus.\n\n"
            "🧮 Elle calcule notamment les masses, les quantités de chaleur "
            "et les bilans matière.\n\n"
            "✅ Elle permet également de consulter l'historique et d'exporter "
            "les résultats vers Excel."
        )

    # 3. Débit initial
    if "m0" in question or "debit du jus brut" in question:
        return (
            "📊 **m0** représente le débit massique initial du jus brut, "
            "exprimé en kg/h.\n\n"
            "💡 Il correspond à la quantité de jus introduite dans le procédé "
            "par heure."
        )

    # 4. Fraction insoluble
    if "x0" in question:
        return (
            "🧪 **x0** représente la fraction insoluble du jus brut.\n\n"
            "💡 Elle correspond à la proportion des matières insolubles "
            "présentes dans le jus."
        )

    # 5. Fraction soluble
    if "y0" in question:
        return (
            "🧪 **y0** représente la fraction soluble du jus brut.\n\n"
            "💡 Elle correspond à la proportion des matières solubles "
            "présentes dans le jus."
        )

    # 6. Fraction d'eau
    if "meau" in question or "fraction d'eau" in question:
        return (
            "💧 **meau** représente la fraction d'eau dans le jus brut.\n\n"
            "💡 Elle indique la proportion d'eau présente dans le produit."
        )

    # 7. Résidus
    if "mresidus" in question or "residus" in question:
        return (
            "🗑️ **mResidus** représente le débit massique des résidus "
            "éliminés pendant le procédé.\n\n"
            "📏 Son unité est le kg/h."
        )

    # 8. Recyclage
    if any(mot in question for mot in ["recyclage", "xr", "mr"]):
        return (
            "♻️ Le recyclage permet de réintroduire une partie du jus "
            "concentré dans le procédé.\n\n"
            "📊 **mR** représente le débit du jus concentré recyclé.\n"
            "🧪 **xr** représente sa fraction soluble."
        )

    # 9. Concentration finale
    if "x4" in question or "concentration finale" in question:
        return (
            "🎯 **x4** représente la concentration finale définie "
            "comme paramètre dans le formulaire.\n\n"
            "💡 Elle permet de déterminer la concentration souhaitée "
            "du jus à la fin du procédé."
        )

    # 10. Températures
    if any(mot in question for mot in ["temperature", "t2", "t3", "t4", "t5"]):
        return (
            "🌡️ Les températures T2, T3, T4 et T5 correspondent "
            "aux différentes étapes thermiques du procédé.\n\n"
            "🔥 Elles permettent de décrire les étapes de chauffage "
            "et de refroidissement."
        )

    # 11. Capacité calorifique
    if "cp" in question or "capacite calorifique" in question:
        return (
            "🌡️ **Cp** représente la capacité calorifique du jus.\n\n"
            "📏 Elle s'exprime en kJ/kg.K et indique l'énergie nécessaire "
            "pour augmenter la température d'un kilogramme de produit "
            "d'un degré."
        )

    # 12. Chaleur
    if any(mot in question for mot in ["q3", "q4", "q5", "chaleur"]):
        return (
            "🔥 Q3, Q4 et Q5 représentent les quantités de chaleur "
            "calculées aux différentes étapes thermiques du procédé.\n\n"
            "🧮 Elles permettent d'évaluer les besoins énergétiques "
            "des opérations."
        )

    # 13. Chaleur latente
    if "lambda" in question or "chaleur latente" in question:
        return (
            "🔥 La chaleur latente représente l'énergie nécessaire "
            "pour vaporiser une unité de masse d'eau sans changement "
            "de température.\n\n"
            "📏 Elle s'exprime généralement en kJ/kg."
        )

    # 14. Eau évaporée
    if any(mot in question for mot in ["evaporation", "mv", "eau evap"]):
        return (
            "💨 **mv** représente la masse d'eau évaporée pendant "
            "l'opération de concentration.\n\n"
            "💧 Cette opération permet d'augmenter la concentration "
            "du jus en éliminant une partie de son eau."
        )

    # 15. Bilan matière
    if "bilan" in question:
        return (
            "⚖️ Le bilan matière permet de comparer les masses entrantes "
            "et les masses sortantes du procédé.\n\n"
            "🧪 L'application calcule également le bilan des matières "
            "solubles.\n\n"
            "✅ Un bilan équilibré indique que les entrées et les sorties "
            "sont cohérentes."
        )

    # 16. Historique
    if "historique" in question:
        return (
            "📚 La page Historique permet de consulter les simulations "
            "déjà réalisées et enregistrées dans la base de données.\n\n"
            "🔎 Vous pouvez retrouver les résultats de vos anciens calculs."
        )

    # 17. Exportation Excel
    if "excel" in question or "export" in question:
        return (
            "📥 Vous pouvez télécharger l'historique des simulations "
            "au format Excel.\n\n"
            "📊 Cliquez sur le bouton d'exportation Excel dans la page "
            "Historique."
        )

    # 18. Authentification
    if any(mot in question for mot in ["connexion", "connecter", "login", "inscription", "sign in", "sign up"]):
        return (
            "🔐 L'application possède un système d'authentification "
            "avec Sign Up et Sign In.\n\n"
            "👤 Chaque utilisateur peut créer un compte et se connecter.\n\n"
            "💻 Le navigateur peut être reconnu après sa première connexion "
            "lorsque Remember this device est activé."
        )

    # 19. Remerciements
    if "merci" in question:
        return (
            "🥰 Avec plaisir !\n\n"
            "🌸 Je reste à votre disposition pour toute autre question."
        )

    # 20. Au revoir
    if any(mot in question for mot in ["au revoir", "a bientot", "bye"]):
        return (
            "👋 Au revoir et à bientôt !\n\n"
            "🍹 Merci d'avoir utilisé notre application."
        )

    # 21. Réponse par défaut
    return (
        "🤔 Je n'ai pas bien compris votre question.\n\n"
        "💡 Vous pouvez me poser des questions sur :\n\n"
        "🍹 Le fonctionnement de l'application\n"
        "📊 Les paramètres du procédé\n"
        "🧪 Les fractions solubles et insolubles\n"
        "🔥 Les températures et les quantités de chaleur\n"
        "⚖️ Les bilans matière\n"
        "📚 L'historique et l'exportation Excel\n\n"
        "😊 Je suis là pour vous aider !"
    )
