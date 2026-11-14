
import sqlite3
from datetime import datetime

DATABASE_NAME = "database.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS calculs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_calcul TEXT,
            m0 REAL,
            x0 REAL,
            y0 REAL,
            meau REAL,
            mResidus REAL,
            mR REAL,
            xr REAL,
            Cp REAL,
            T2 REAL,
            T3 REAL,
            x4 REAL,
            T4 REAL,
            T5 REAL,
            lambda_v REAL,
            m1 REAL,
            y1 REAL,
            m2 REAL,
            y2 REAL,
            Q3 REAL,
            m4 REAL,
            mv REAL,
            Q4 REAL,
            Q5 REAL,
            entrees REAL,
            sorties REAL,
            erreur_bilan_global REAL,
            solubles_entrantes REAL,
            solubles_sortantes REAL,
            erreur_bilan_solubles REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            device_name TEXT,
            created_at TEXT NOT NULL,
            last_seen TEXT,
            revoked INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)


    conn.commit()
    conn.close()


def enregistrer_calcul(p, r):
    conn = get_connection()

    conn.execute("""
        INSERT INTO calculs (
            date_calcul, m0, x0, y0, meau, mResidus,
            mR, xr, Cp, T2, T3, x4, T4, T5, lambda_v,
            m1, y1, m2, y2, Q3, m4, mv, Q4, Q5,
            entrees, sorties, erreur_bilan_global,
            solubles_entrantes, solubles_sortantes,
            erreur_bilan_solubles
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        p["m0"], p["x0"], p["y0"], p["meau"],
        p["mResidus"], p["mR"], p["xr"], p["Cp"],
        p["T2"], p["T3"], p["x4"], p["T4"],
        p["T5"], p["lambda_v"],
        r["m1"], r["y1"], r["m2"], r["y2"],
        r["Q3"], r["m4"], r["mv"], r["Q4"], r["Q5"],
        r["entrees"], r["sorties"],
        r["erreur_bilan_global"],
        r["solubles_entrantes"], r["solubles_sortantes"],
        r["erreur_bilan_solubles"]
    ))

    conn.commit()
    conn.close()


def recuperer_calculs():
    conn = get_connection()
    
    calculs = conn.execute(
        "SELECT * FROM calculs ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return [dict(c) for c in calculs]
