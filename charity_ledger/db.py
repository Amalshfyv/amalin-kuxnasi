from __future__ import annotations
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "ledger.db"


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    status TEXT,
    raised REAL,
    goal REAL,
    backers INTEGER,
    days_left INTEGER,
    last_update TEXT,
    leads TEXT,
    hero_image TEXT
);
CREATE TABLE IF NOT EXISTS donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    tier TEXT,
    total_donated REAL,
    last_activity TEXT,
    location TEXT,
    joined TEXT,
    projects_supported INTEGER,
    phone TEXT,
    avatar TEXT
);
CREATE TABLE IF NOT EXISTS beneficiaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    funds_received REAL,
    funds_goal REAL,
    status TEXT,
    project TEXT,
    avatar TEXT
);
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    donor TEXT,
    project TEXT,
    date TEXT,
    amount REAL,
    status TEXT,
    payment_method TEXT,
    blockchain_hash TEXT,
    gateway_response TEXT
);
CREATE TABLE IF NOT EXISTS donation_trends (
    month TEXT PRIMARY KEY,
    amount REAL
);
CREATE TABLE IF NOT EXISTS project_funding_trends (
    project_id TEXT,
    month TEXT,
    amount REAL,
    PRIMARY KEY (project_id, month)
);
"""


def init_db(force_reseed: bool = False):
    fresh = not DB_PATH.exists()
    if force_reseed and DB_PATH.exists():
        DB_PATH.unlink()
        fresh = True
    c = conn()
    c.executescript(SCHEMA)
    c.commit()
    if fresh:
        seed(c)
    c.close()


def seed(c):
    projects = [
        ("PRJ-001", "Clean Water Initiative", "Constructing solar-powered wells across remote villages in the Sahel region to provide sustainable clean water access.", "Environment", "In Progress", 187500, 250000, 412, 12, "2 hours ago", "AP,BP,CP,DR,EM,FN", "water"),
        ("PRJ-002", "Urban Education Fund", "Supplying books and training for local teachers across urban districts to boost literacy and student outcomes.", "Education", "In Progress", 42000, 100000, 188, 30, "1 day ago", "GS,HJ,IK", "education"),
        ("PRJ-003", "Forest Reforestation", "Restoring biodiversity through native tree planting programs across deforested coastal regions.", "Environment", "In Progress", 465000, 500000, 902, 5, "5 hours ago", "JK,LM,NO,PQ", "forest"),
        ("PRJ-004", "Emergency Relief Hub", "Rapid response logistics and shelter for communities affected by natural disasters.", "Humanitarian", "In Progress", 58000, 75000, 234, 18, "3 hours ago", "RS,TU,VW", "relief"),
        ("PRJ-005", "Wildlife Sanctuary Support", "Protecting endangered species through habitat restoration and anti-poaching patrols.", "Environment", "In Progress", 89000, 150000, 167, 45, "6 hours ago", "XY,ZA,BC", "wildlife"),
        ("PRJ-006", "Global Literacy Fund", "Supplying books and training for local teachers in underserved regions worldwide.", "Education", "In Progress", 124000, 200000, 301, 22, "1 day ago", "DE,FG,HI", "literacy"),
    ]
    c.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", projects)

    donors = [
        ("Sarah Jenkins", "s.jenkins@example.com", "Platinum", 12500, "2 hours ago", "Seattle, WA", "Oct 2021", 12, "+1 (555) 012-3456", "sarah"),
        ("Michael Chen", "m.chen@example.com", "Gold", 8400, "1 day ago", "San Francisco, CA", "Mar 2022", 7, "+1 (555) 234-5678", "michael"),
        ("Elena Rodriguez", "e.rodriguez@example.com", "Silver", 3200, "3 days ago", "Austin, TX", "Jul 2023", 4, "+1 (555) 345-6789", "elena"),
        ("James Wilson", "j.wilson@example.com", "Bronze", 1500, "1 week ago", "Boston, MA", "Jan 2024", 2, "+1 (555) 456-7890", "james"),
        ("Amina Okafor", "a.okafor@example.com", "Platinum", 25000, "5 mins ago", "Lagos, NG", "Feb 2020", 18, "+234 803 123 4567", "amina"),
        ("David Thompson", "d.thompson@example.com", "Silver", 2750, "2 days ago", "Denver, CO", "May 2023", 3, "+1 (555) 567-8901", "david"),
        ("Global Tech Corp", "donations@globaltech.com", "Platinum", 75000, "1 day ago", "New York, NY", "Jan 2019", 24, "+1 (555) 999-0000", "globaltech"),
    ]
    c.executemany(
        "INSERT INTO donors (name,email,tier,total_donated,last_activity,location,joined,projects_supported,phone,avatar) VALUES (?,?,?,?,?,?,?,?,?,?)",
        donors,
    )

    beneficiaries = [
        ("Unity Wells Foundation", "Sub-Saharan Africa", 35000, 50000, "Active", "Clean Water For All", "unity"),
        ("Kyoto Reforestation Center", "Kyoto, Japan", 12000, 25000, "Active", "Green Canopy 2024", "kyoto"),
        ("Sarah Jenkins Trust", "London, UK", 5000, 5000, "Active", "Artist Emergency Fund", "sjt"),
        ("Dhaka Education Hub", "Dhaka, Bangladesh", 2000, 15000, "Pending", "", "dhaka"),
        ("Andes Medical Relief", "Peru", 0, 80000, "On Hold", "High-Altitude Healthcare", "andes"),
        ("Beirut Youth Shelter", "Beirut, Lebanon", 22500, 45000, "Active", "Urban Refuge Program", "beirut"),
    ]
    c.executemany(
        "INSERT INTO beneficiaries (name,location,funds_received,funds_goal,status,project,avatar) VALUES (?,?,?,?,?,?,?)",
        beneficiaries,
    )

    txs = [
        ("TX-9021", "Sarah Jenkins", "Clean Water Initiative", "Oct 24, 2024", 2500, "Verified", "Stripe / Credit Card", "0x33e1...a8f7", '{"code": 200, "message": "Authorized", "auth_code": "AUTH_2219"}'),
        ("TX-8842", "Michael Chen", "Urban Education Fund", "Oct 24, 2024", 500, "Pending", "PayPal", "0x44b2...c9e1", '{"code": 102, "message": "Processing"}'),
        ("TX-8810", "Global Tech Corp", "Forest Reforestation", "Oct 23, 2024", 15000, "Verified", "Wire Transfer", "0x55cc...d0a2", '{"code": 200, "message": "Authorized", "auth_code": "AUTH_3104"}'),
        ("TX-8795", "Elena Rodriguez", "Emergency Relief Hub", "Oct 22, 2024", 1200, "Verified", "Stripe / Credit Card", "0x66dd...e1b3", '{"code": 200, "message": "Authorized", "auth_code": "AUTH_2998"}'),
        ("TX-8750", "David Thompson", "Clean Water Initiative", "Oct 22, 2024", 750, "Failed", "Stripe / Credit Card", "0x77ee...f2c4", '{"code": 402, "message": "Card declined"}'),
        ("TX-8702", "Amina Okafor", "Wildlife Sanctuary Support", "Oct 21, 2024", 5000, "Verified", "ACH", "0x88ff...03d5", '{"code": 200, "message": "Authorized", "auth_code": "AUTH_3201"}'),
        ("TX-55401-88", "Michael O'Neill", "Wildlife Sanctuary Support", "Oct 21, 2024", 1200, "Verified", "Stripe / Credit Card", "0x33e1...a8f7", '{"code": 200, "message": "Authorized", "auth_code": "AUTH_2219"}'),
    ]
    c.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)", txs)

    trends = [("Jan", 90000), ("Feb", 120000), ("Mar", 110000), ("Apr", 175000), ("May", 200000), ("Jun", 270000)]
    c.executemany("INSERT INTO donation_trends VALUES (?,?)", trends)

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    by_proj = {
        "PRJ-001": [22, 28, 18, 38, 30, 42],
        "PRJ-002": [10, 14, 9, 19, 16, 24],
        "PRJ-003": [55, 65, 48, 80, 72, 95],
    }
    for pid, vals in by_proj.items():
        c.executemany(
            "INSERT INTO project_funding_trends VALUES (?,?,?)",
            [(pid, m, v * 1000) for m, v in zip(months, vals)],
        )

    c.commit()


def list_projects():
    c = conn()
    rows = c.execute("SELECT * FROM projects ORDER BY rowid").fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_project(pid: str):
    c = conn()
    r = c.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    c.close()
    return dict(r) if r else None


def list_donors():
    c = conn()
    rows = c.execute("SELECT * FROM donors ORDER BY total_donated DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]


def list_beneficiaries():
    c = conn()
    rows = c.execute("SELECT * FROM beneficiaries ORDER BY rowid").fetchall()
    c.close()
    return [dict(r) for r in rows]


def list_transactions(limit: int | None = None):
    c = conn()
    sql = "SELECT * FROM transactions ORDER BY date DESC, id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    rows = c.execute(sql).fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_transaction(tx_id: str):
    c = conn()
    r = c.execute("SELECT * FROM transactions WHERE id=?", (tx_id,)).fetchone()
    c.close()
    return dict(r) if r else None


def next_project_id() -> str:
    c = conn()
    n = c.execute("SELECT COUNT(*) FROM projects").fetchone()[0] or 0
    c.close()
    return f"PRJ-{n + 1:03d}"


def insert_project(p: dict):
    c = conn()
    c.execute(
        "INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            p["id"], p["name"], p.get("description", ""), p.get("category", ""),
            p.get("status", "In Progress"), float(p.get("raised", 0)), float(p.get("goal", 0)),
            int(p.get("backers", 0)), int(p.get("days_left", 30)),
            p.get("last_update", "just now"), p.get("leads", ""), p.get("hero_image", ""),
        ),
    )
    c.commit()
    c.close()


def update_project(p: dict):
    c = conn()
    c.execute(
        "UPDATE projects SET name=?, description=?, category=?, status=?, goal=?, last_update=? WHERE id=?",
        (
            p["name"], p.get("description", ""), p.get("category", ""),
            p.get("status", "In Progress"), float(p.get("goal", 0)),
            "just now", p["id"],
        ),
    )
    c.commit()
    c.close()


def archive_project(pid: str):
    c = conn()
    c.execute("UPDATE projects SET status='Archived', last_update='just now' WHERE id=?", (pid,))
    c.commit()
    c.close()


def insert_donor(d: dict):
    c = conn()
    c.execute(
        "INSERT INTO donors (name,email,tier,total_donated,last_activity,location,joined,projects_supported,phone,avatar) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            d["name"], d.get("email", ""), d.get("tier", "Silver"),
            float(d.get("total_donated", 0)), d.get("last_activity", "just now"),
            d.get("location", ""), d.get("joined", ""), int(d.get("projects_supported", 0)),
            d.get("phone", ""), d.get("avatar", ""),
        ),
    )
    c.commit()
    c.close()


def insert_beneficiary(b: dict):
    c = conn()
    c.execute(
        "INSERT INTO beneficiaries (name,location,funds_received,funds_goal,status,project,avatar) VALUES (?,?,?,?,?,?,?)",
        (
            b["name"], b.get("location", ""),
            float(b.get("funds_received", 0)), float(b.get("funds_goal", 0)),
            b.get("status", "Pending"), b.get("project", ""), b.get("avatar", ""),
        ),
    )
    c.commit()
    c.close()


def update_beneficiary_project(bid: int, project: str):
    c = conn()
    c.execute(
        "UPDATE beneficiaries SET project=?, status=CASE WHEN ?='' THEN 'Pending' ELSE 'Active' END WHERE id=?",
        (project, project, bid),
    )
    c.commit()
    c.close()


def update_transaction_status(tx_id: str, status: str):
    c = conn()
    c.execute("UPDATE transactions SET status=? WHERE id=?", (status, tx_id))
    c.commit()
    c.close()


def delete_transaction(tx_id: str):
    c = conn()
    row = c.execute("SELECT amount, project, status FROM transactions WHERE id=?", (tx_id,)).fetchone()
    if row and row["status"] == "Verified":
        c.execute("UPDATE projects SET raised = raised - ? WHERE name=?", (row["amount"], row["project"]))
    c.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
    c.commit()
    c.close()


def stats_by_status() -> dict:
    c = conn()
    rows = c.execute("SELECT status, COUNT(*) AS n, COALESCE(SUM(amount),0) AS total FROM transactions GROUP BY status").fetchall()
    c.close()
    return {r["status"]: {"count": r["n"], "total": r["total"]} for r in rows}


def stats_by_category() -> list:
    c = conn()
    rows = c.execute("SELECT category, COUNT(*) AS n, COALESCE(SUM(raised),0) AS total FROM projects GROUP BY category").fetchall()
    c.close()
    return [dict(r) for r in rows]


def insert_transaction(tx: dict):
    c = conn()
    c.execute(
        "INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)",
        (
            tx["id"],
            tx["donor"],
            tx["project"],
            tx["date"],
            tx["amount"],
            tx["status"],
            tx["payment_method"],
            tx["blockchain_hash"],
            tx["gateway_response"],
        ),
    )
    c.execute(
        "UPDATE projects SET raised = COALESCE(raised,0) + ? WHERE name = ?",
        (tx["amount"], tx["project"]),
    )
    c.commit()
    c.close()


def donation_trends():
    c = conn()
    rows = c.execute("SELECT * FROM donation_trends").fetchall()
    c.close()
    return [dict(r) for r in rows]


def project_funding_trend(pid: str):
    c = conn()
    rows = c.execute("SELECT * FROM project_funding_trends WHERE project_id=?", (pid,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def kpis():
    c = conn()
    total_funds = c.execute("SELECT COALESCE(SUM(raised),0) FROM projects").fetchone()[0]
    active = c.execute("SELECT COUNT(*) FROM projects WHERE status='In Progress'").fetchone()[0]
    donor_ct = c.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
    pending = c.execute("SELECT COUNT(*) FROM transactions WHERE status='Pending'").fetchone()[0]
    c.close()
    return {
        "total_funds": total_funds,
        "active": active,
        "donors": donor_ct,
        "pending": pending,
    }
