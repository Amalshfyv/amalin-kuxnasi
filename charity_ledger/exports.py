"""CSV / report exports. Files written to ./exports/ next to the ledger.db."""
from __future__ import annotations
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import db

EXPORT_DIR = Path(__file__).resolve().parent.parent / "exports"


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_dir() -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    return EXPORT_DIR


def _write_rows(path: Path, rows: list, header: list):
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])
    return path


def export_donors() -> Path:
    path = _ensure_dir() / f"donors_{_stamp()}.csv"
    rows = db.list_donors()
    header = ["id", "name", "email", "tier", "total_donated", "location", "joined", "projects_supported", "phone", "last_activity"]
    return _write_rows(path, rows, header)


def export_transactions(filter_status: str | None = None) -> Path:
    path = _ensure_dir() / f"transactions_{_stamp()}.csv"
    rows = db.list_transactions()
    if filter_status:
        rows = [r for r in rows if r["status"] == filter_status]
    header = ["id", "donor", "project", "date", "amount", "status", "payment_method", "blockchain_hash"]
    return _write_rows(path, rows, header)


def export_single_transaction(tx_id: str) -> Path:
    tx = db.get_transaction(tx_id)
    if not tx:
        raise ValueError(f"Transaction {tx_id} not found")
    path = _ensure_dir() / f"audit_{tx_id}_{_stamp()}.csv"
    header = ["id", "donor", "project", "date", "amount", "status", "payment_method", "blockchain_hash", "gateway_response"]
    return _write_rows(path, [tx], header)


def export_projects() -> Path:
    path = _ensure_dir() / f"projects_{_stamp()}.csv"
    rows = db.list_projects()
    header = ["id", "name", "category", "status", "raised", "goal", "backers", "days_left", "last_update"]
    return _write_rows(path, rows, header)


def export_beneficiaries() -> Path:
    path = _ensure_dir() / f"beneficiaries_{_stamp()}.csv"
    rows = db.list_beneficiaries()
    header = ["id", "name", "location", "funds_received", "funds_goal", "status", "project"]
    return _write_rows(path, rows, header)


def export_audit_report(project_id: str | None = None) -> Path:
    """Plain-text audit report. If project_id given, scope to that project."""
    path = _ensure_dir() / f"audit_report_{project_id or 'all'}_{_stamp()}.txt"
    txs = db.list_transactions()
    if project_id:
        proj = db.get_project(project_id)
        txs = [t for t in txs if t["project"] == proj["name"]] if proj else []
    lines = [
        "CHARITY TRANSPARENCY LEDGER — AUDIT REPORT",
        "=" * 50,
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Scope: {project_id or 'All projects'}",
        "",
        f"Transactions in scope: {len(txs)}",
        f"Total volume: ${sum(t['amount'] for t in txs):,.2f}",
        f"Verified: {sum(1 for t in txs if t['status'] == 'Verified')}",
        f"Pending:  {sum(1 for t in txs if t['status'] == 'Pending')}",
        f"Failed:   {sum(1 for t in txs if t['status'] == 'Failed')}",
        "",
        "LEDGER ENTRIES",
        "-" * 50,
    ]
    for t in txs:
        lines.append(f"{t['id']:<14} {t['date']:<14} {t['donor']:<22} ${t['amount']:>10,.2f}  {t['status']:<10} {t['blockchain_hash']}")
    path.write_text("\n".join(lines))
    return path


def generate_dashboard_report() -> Path:
    """Markdown-style dashboard report."""
    path = _ensure_dir() / f"dashboard_report_{_stamp()}.md"
    k = db.kpis()
    projects = db.list_projects()
    by_cat = db.stats_by_category()
    by_status = db.stats_by_status()
    lines = [
        "# Charity Transparency Ledger — Dashboard Report",
        "",
        f"_Generated {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Key Metrics",
        f"- **Total Funds Raised:** ${k['total_funds']:,.0f}",
        f"- **Active Projects:** {k['active']}",
        f"- **Total Donors:** {k['donors']}",
        f"- **Pending Verification:** {k['pending']}",
        "",
        "## Funding by Category",
    ]
    for c in by_cat:
        lines.append(f"- **{c['category'] or '—'}**: ${c['total']:,.0f} across {c['n']} projects")
    lines += ["", "## Transaction Status Distribution"]
    for s, v in by_status.items():
        lines.append(f"- **{s}**: {v['count']} transactions, ${v['total']:,.0f}")
    lines += ["", "## Top Projects"]
    for p in sorted(projects, key=lambda x: x["raised"], reverse=True)[:5]:
        pct = (p["raised"] / p["goal"] * 100) if p["goal"] else 0
        lines.append(f"- **{p['name']}** ({p['category']}): ${p['raised']:,.0f} / ${p['goal']:,.0f} — {pct:.0f}%")
    path.write_text("\n".join(lines))
    return path
