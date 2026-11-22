import pytest

from scripts import run_local_session


class UnbufferedCursor:
    def __init__(self, database="raceexpertcomua"):
        self.database = database
        self.rows = []
        self.unread_result = False
        self.queries = []
        self.closed = False

    def execute(self, query):
        if self.unread_result:
            raise RuntimeError("unread_result_found")
        self.queries.append(query)
        if query == "SELECT DATABASE()":
            self.rows = [(self.database,)]
        elif query == "SELECT 1":
            self.rows = [(1,)]
        elif query.startswith("SELECT * FROM"):
            self.rows = []
        else:
            raise AssertionError("unexpected_query")
        self.unread_result = True

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        rows = self.rows
        self.rows = []
        self.unread_result = False
        return rows

    def close(self):
        self.closed = True


class UnbufferedConnection:
    def __init__(self, database="raceexpertcomua"):
        self.cursor_instance = UnbufferedCursor(database)
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def close(self):
        self.closed = True


def test_preflight_consumes_each_result_before_next_query(monkeypatch):
    connection = UnbufferedConnection()
    monkeypatch.setattr(
        run_local_session,
        "_tls_connection",
        lambda settings: (connection, "TLSv1.3"),
    )

    assert run_local_session._preflight(object()) == "TLSv1.3"
    assert connection.cursor_instance.closed
    assert connection.closed
    assert len(connection.cursor_instance.queries) == 2 + len(run_local_session.PRODUCT_TABLES)


def test_preflight_rejects_unexpected_database(monkeypatch):
    connection = UnbufferedConnection(database="other_database")
    monkeypatch.setattr(
        run_local_session,
        "_tls_connection",
        lambda settings: (connection, "TLSv1.3"),
    )

    with pytest.raises(run_local_session.LaunchError, match="mysql_database_mismatch"):
        run_local_session._preflight(object())

    assert connection.closed


def test_ssh_tunnel_sends_keepalives_and_verifies_host(monkeypatch, tmp_path):
    settings = run_local_session.SessionSettings(
        ssh_host=run_local_session.EXPECTED_SSH_HOST,
        ssh_user="qa",
        ssh_port=22,
        ssh_key=tmp_path / "key",
        mysql_host="database.internal",
        mysql_port=3306,
        mysql_database=run_local_session.EXPECTED_DATABASE,
        mysql_user="readonly",
        mysql_password="unused",
        openai_api_key="unused",
        journal_path=tmp_path / "journal.sqlite3",
    )
    captured = {}

    def fake_popen(command, **kwargs):
        captured["command"] = command
        return object()

    monkeypatch.setattr(run_local_session.subprocess, "Popen", fake_popen)

    run_local_session._start_tunnel(settings, 50000)

    assert "StrictHostKeyChecking=yes" in captured["command"]
    assert "ServerAliveInterval=30" in captured["command"]
    assert "ServerAliveCountMax=3" in captured["command"]
