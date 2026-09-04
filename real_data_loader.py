import os
import sqlite3


def find_db(filename="patterns_v2.db"):
    """
    Locate the real OMNIS/SHOGUN database.

    Search order:
    1. Current working directory
    2. HOME
    3. Known OMNIS/SHOGUN locations
    4. Recursive HOME search
    """

    home = os.path.expanduser("~")

    candidates = [
        os.path.join(os.getcwd(), filename),
        os.path.join(home, filename),

        os.path.join(
            home,
            "SHOGUN_OS",
            "08_INTELLIGENCE",
            filename,
        ),

        os.path.join(
            home,
            "AAR_CORE",
            filename,
        ),
    ]

    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)

    for root, dirs, files in os.walk(home):
        dirs[:] = [
            d for d in dirs
            if d not in {
                ".cache",
                ".npm",
                ".gradle",
                "node_modules",
                "__pycache__",
            }
        ]

        if filename in files:
            return os.path.abspath(
                os.path.join(root, filename)
            )

    return None


def _table_columns(conn, table):
    rows = conn.execute(
        'PRAGMA table_info("' +
        table.replace('"', '""') +
        '")'
    ).fetchall()

    return [row[1] for row in rows]


def load_real_outcomes(
    db_path,
    limit=500,
    canonical_id=None,
):
    """
    Load REAL historical outcomes from the discovered
    SQLite schema.

    Expected real schema:

        outcomes(
            id,
            timestamp,
            canonical_id,
            dna_key,
            action,
            reward,
            pnl,
            success,
            confidence,
            trust,
            regime
        )

    No synthetic records are generated.
    """

    if not db_path:
        raise ValueError("db_path is required")

    db_path = os.path.abspath(
        os.path.expanduser(db_path)
    )

    if not os.path.isfile(db_path):
        raise FileNotFoundError(db_path)

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive integer")

    conn = sqlite3.connect(db_path)

    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table'"
            ).fetchall()
        }

        if "outcomes" not in tables:
            raise RuntimeError(
                "Database does not contain outcomes table"
            )

        columns = _table_columns(conn, "outcomes")

        required = {
            "id",
            "timestamp",
            "canonical_id",
            "dna_key",
            "action",
            "reward",
            "pnl",
            "success",
            "confidence",
            "trust",
            "regime",
        }

        missing = sorted(required - set(columns))

        if missing:
            raise RuntimeError(
                "outcomes schema missing required columns: "
                + repr(missing)
            )

        query = """
            SELECT
                id,
                timestamp,
                canonical_id,
                dna_key,
                action,
                reward,
                pnl,
                success,
                confidence,
                trust,
                regime
            FROM outcomes
        """

        params = []

        if canonical_id is not None:
            query += """
                WHERE canonical_id = ?
            """
            params.append(canonical_id)

        query += """
            ORDER BY id DESC
            LIMIT ?
        """

        cur = conn.execute(
            query,
            tuple(params) + (limit,),
        )

        rows = cur.fetchall()

        fields = [
            "id",
            "timestamp",
            "canonical_id",
            "dna_key",
            "action",
            "reward",
            "pnl",
            "success",
            "confidence",
            "trust",
            "regime",
        ]

        return [
            dict(zip(fields, row))
            for row in rows
        ]

    finally:
        conn.close()
