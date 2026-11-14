
import hashlib
import secrets
import sqlite3

from datetime import datetime
from pwdlib import PasswordHash

from database import get_connection


# Gestion sécurisée des mots de passe
password_hasher = PasswordHash.recommended()


def crypter_mot_de_passe(password):
    return password_hasher.hash(password)


def verifier_mot_de_passe(password, password_hash):
    return password_hasher.verify(password, password_hash)


# Création d'un utilisateur
def creer_utilisateur(username, email, password):
    conn = get_connection()

    try:
        utilisateur = conn.execute(
            "SELECT id FROM users WHERE username = ? COLLATE NOCASE",
            (username,)
        ).fetchone()

        if utilisateur:
            raise ValueError("Ce nom d'utilisateur existe déjà.")

        utilisateur = conn.execute(
            "SELECT id FROM users WHERE email = ? COLLATE NOCASE",
            (email,)
        ).fetchone()

        if utilisateur:
            raise ValueError("Cette adresse email est déjà utilisée.")

        password_hash = crypter_mot_de_passe(password)

        conn.execute("""
            INSERT INTO users (
                username, email, password_hash, created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:
        raise ValueError("Ce nom d'utilisateur ou cet email existe déjà.")

    finally:
        conn.close()


# Connexion avec username ou email
def authentifier_utilisateur(login, password):
    conn = get_connection()

    try:
        utilisateur = conn.execute("""
            SELECT * FROM users
            WHERE username = ? COLLATE NOCASE
               OR email = ? COLLATE NOCASE
        """, (login, login)).fetchone()

        if utilisateur is None:
            return None

        if not verifier_mot_de_passe(
            password,
            utilisateur["password_hash"]
        ):
            return None

        return dict(utilisateur)

    finally:
        conn.close()


# Création d'un appareil reconnu
def creer_appareil(user_id, device_name=None):
    conn = get_connection()

    try:
        token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        date_actuelle = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        conn.execute("""
            INSERT INTO devices (
                user_id,
                token_hash,
                device_name,
                created_at,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            token_hash,
            device_name,
            date_actuelle,
            date_actuelle
        ))

        conn.commit()

        return token

    finally:
        conn.close()


# Reconnaissance d'un appareil déjà connecté
def recuperer_utilisateur_par_appareil(token):
    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    conn = get_connection()

    try:
        utilisateur = conn.execute("""
            SELECT users.*
            FROM users
            INNER JOIN devices ON users.id = devices.user_id
            WHERE devices.token_hash = ?
              AND devices.revoked = 0
        """, (token_hash,)).fetchone()

        if utilisateur is None:
            return None

        conn.execute("""
            UPDATE devices
            SET last_seen = ?
            WHERE token_hash = ?
        """, (
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            token_hash
        ))

        conn.commit()

        return dict(utilisateur)

    finally:
        conn.close()


# Déconnexion et suppression de la reconnaissance de cet appareil
def deconnecter_appareil(token):
    if not token:
        return

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    conn = get_connection()

    try:
        conn.execute("""
            UPDATE devices
            SET revoked = 1
            WHERE token_hash = ?
        """, (token_hash,))

        conn.commit()

    finally:
        conn.close()
