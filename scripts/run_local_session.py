from __future__ import annotations

import argparse
import os
import socket
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


EXPECTED_SSH_HOST = "185.25.119.96"
EXPECTED_DATABASE = "raceexpertcomua"
EXPECTED_CONNECTOR_VERSION = "26.10.0"
APP_HOST = "127.0.0.1"
APP_PORT = 8787
PRODUCT_TABLES = (
    "oc_product",
    "oc_product_description",
    "oc_product_attribute",
    "oc_attribute_description",
    "oc_stock_status",
)
ENV_KEYS = {
    "SSH_HOST",
    "SSH_USER",
    "SSH_PORT",
    "SSH_PRIVATE_KEY_PATH",
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_DATABASE",
    "MYSQL_USER",
    "MYSQL_PASSWORD_FILE",
    "OPENAI_API_KEY_FILE",
    "TAVILY_API_KEY",
    "TAVILY_API_KEY_FILE",
    "JOURNAL_PATH",
}


class LaunchError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class SessionSettings:
    ssh_host: str
    ssh_user: str
    ssh_port: int
    ssh_key: Path
    mysql_host: str
    mysql_port: int
    mysql_database: str
    mysql_user: str
    mysql_password: str = field(repr=False)
    openai_api_key: str = field(repr=False)
    journal_path: Path
    tavily_api_key: str = field(default="", repr=False)


def _parse_value(raw: str) -> str:
    value = raw.strip()
    if value.startswith(("'", '"')):
        quote = value[0]
        closing = value.find(quote, 1)
        if closing < 0 or value[closing + 1 :].strip().lstrip()[:1] not in ("", "#"):
            raise LaunchError("env_value_invalid")
        return value[1:closing]
    return value.split("#", 1)[0].strip()


def _resolve_path(value: str, env_path: Path) -> Path:
    path = Path(os.path.expandvars(os.path.expanduser(value)))
    return path if path.is_absolute() else env_path.parent / path


def _read_secret(path: Path, error_code: str) -> str:
    try:
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise LaunchError("secret_file_permissions_must_be_0600_or_stricter")
        value = path.read_text(encoding="utf-8").strip()
    except LaunchError:
        raise
    except (OSError, UnicodeError):
        raise LaunchError(error_code) from None
    if not value:
        raise LaunchError(error_code)
    return value


def load_settings(env_path: Path) -> SessionSettings:
    if not env_path.is_file():
        raise LaunchError("env_file_unavailable")
    if stat.S_IMODE(env_path.stat().st_mode) & 0o077:
        raise LaunchError("env_file_permissions_must_be_0600_or_stricter")

    values: dict[str, str] = {}
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line.removeprefix("export ").lstrip()
            key, separator, raw_value = line.partition("=")
            key = key.strip()
            if separator and key in ENV_KEYS:
                if key in values:
                    raise LaunchError("env_key_duplicated")
                values[key] = _parse_value(raw_value)
    except LaunchError:
        raise
    except (OSError, UnicodeError):
        raise LaunchError("env_file_unreadable") from None

    required = ENV_KEYS - {"JOURNAL_PATH", "TAVILY_API_KEY", "TAVILY_API_KEY_FILE"}
    if any(not values.get(key) for key in required):
        raise LaunchError("env_required_entries_missing")
    tavily_api_key_value = values.get("TAVILY_API_KEY", "").strip()
    tavily_api_key_file = values.get("TAVILY_API_KEY_FILE", "").strip()
    if tavily_api_key_value and tavily_api_key_file:
        raise LaunchError("tavily_configuration_conflict")
    if not tavily_api_key_value and not tavily_api_key_file:
        raise LaunchError("tavily_configuration_missing")
    if values["SSH_HOST"] != EXPECTED_SSH_HOST:
        raise LaunchError("ssh_host_mismatch")
    if values["MYSQL_DATABASE"] != EXPECTED_DATABASE:
        raise LaunchError("mysql_database_mismatch")

    try:
        ssh_port = int(values["SSH_PORT"])
        mysql_port = int(values["MYSQL_PORT"])
    except ValueError:
        raise LaunchError("port_invalid") from None
    if not 1 <= ssh_port <= 65535 or not 1 <= mysql_port <= 65535:
        raise LaunchError("port_invalid")

    ssh_key = _resolve_path(values["SSH_PRIVATE_KEY_PATH"], env_path)
    if not ssh_key.is_file() or stat.S_IMODE(ssh_key.stat().st_mode) & 0o077:
        raise LaunchError("ssh_private_key_unavailable_or_permissions_invalid")
    password = _read_secret(_resolve_path(values["MYSQL_PASSWORD_FILE"], env_path), "mysql_password_unavailable")
    openai_key = _read_secret(
        _resolve_path(values["OPENAI_API_KEY_FILE"], env_path), "openai_api_key_unavailable"
    )
    tavily_api_key = (
        tavily_api_key_value
        if tavily_api_key_value
        else _read_secret(
            _resolve_path(tavily_api_key_file, env_path), "tavily_api_key_unavailable"
        )
    )
    journal_value = values.get("JOURNAL_PATH", "var/qa-journal.sqlite3")
    journal_path = _resolve_path(journal_value, env_path)

    return SessionSettings(
        ssh_host=values["SSH_HOST"],
        ssh_user=values["SSH_USER"],
        ssh_port=ssh_port,
        ssh_key=ssh_key,
        mysql_host=values["MYSQL_HOST"],
        mysql_port=mysql_port,
        mysql_database=values["MYSQL_DATABASE"],
        mysql_user=values["MYSQL_USER"],
        mysql_password=password,
        openai_api_key=openai_key,
        tavily_api_key=tavily_api_key,
        journal_path=journal_path,
    )


def _allocate_local_port() -> int:
    with socket.socket() as probe:
        probe.bind((APP_HOST, 0))
        return int(probe.getsockname()[1])


def _start_tunnel(settings: SessionSettings, local_port: int) -> subprocess.Popen[bytes]:
    command = [
        "ssh",
        "-i",
        str(settings.ssh_key),
        "-p",
        str(settings.ssh_port),
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "BatchMode=yes",
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=30",
        "-o",
        "ServerAliveCountMax=3",
        "-N",
        "-L",
        f"{APP_HOST}:{local_port}:{settings.mysql_host}:{settings.mysql_port}",
        f"{settings.ssh_user}@{settings.ssh_host}",
    ]
    try:
        return subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        raise LaunchError("ssh_unavailable") from None


def _wait_for_tunnel(tunnel: subprocess.Popen[bytes], local_port: int) -> None:
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        if tunnel.poll() is not None:
            raise LaunchError("ssh_tunnel_failed_check_known_hosts_and_vps_key")
        try:
            with socket.create_connection((APP_HOST, local_port), timeout=0.3):
                return
        except OSError:
            time.sleep(0.15)
    raise LaunchError("ssh_tunnel_timeout_check_vps_and_mysql_route")


def _configure_runtime(settings: SessionSettings, local_port: int) -> None:
    os.environ.update(
        MYSQL_HOST=APP_HOST,
        MYSQL_PORT=str(local_port),
        MYSQL_DATABASE=settings.mysql_database,
        MYSQL_USER=settings.mysql_user,
        MYSQL_PASSWORD=settings.mysql_password,
        MYSQL_SSL_CA="",
        OPENAI_API_KEY=settings.openai_api_key,
        TAVILY_API_KEY=settings.tavily_api_key,
        JOURNAL_PATH=str(settings.journal_path),
    )
    os.environ.pop("MYSQL_PASSWORD_FILE", None)
    os.environ.pop("OPENAI_API_KEY_FILE", None)
    os.environ.pop("TAVILY_API_KEY_FILE", None)


def _tls_connection(settings: Any) -> tuple[Any, str]:
    import mysql.connector
    from mysql.connector.connection import MySQLConnection

    if mysql.connector.__version__ != EXPECTED_CONNECTOR_VERSION:
        raise LaunchError("mysql_connector_version_mismatch")

    class RequiredTLSConnection(MySQLConnection):
        def _do_handshake(self) -> None:
            verify_cert = self._ssl.get("verify_cert", False)
            self._ssl["verify_cert"] = True
            try:
                super()._do_handshake()
            finally:
                self._ssl["verify_cert"] = verify_cert

    connection = None
    try:
        connection = RequiredTLSConnection(
            host=APP_HOST,
            port=settings.port,
            database=settings.database,
            user=settings.user,
            password=settings.password,
            ssl_disabled=False,
            ssl_verify_cert=False,
            ssl_verify_identity=False,
            allow_local_infile=False,
            connection_timeout=5,
        )
        if not getattr(connection, "_ssl_active", False):
            raise LaunchError("mysql_tls_not_active")
        ssl_socket = getattr(getattr(connection, "_socket", None), "sock", None)
        tls_version = ssl_socket.version() if ssl_socket is not None else None
        if tls_version not in ("TLSv1.2", "TLSv1.3"):
            raise LaunchError("mysql_tls_version_unacceptable")
        return connection, tls_version
    except LaunchError:
        if connection is not None:
            connection.close()
        raise
    except Exception:
        if connection is not None:
            connection.close()
        raise LaunchError("mysql_connection_failed") from None


def _preflight(settings: Any) -> str:
    connection, tls_version = _tls_connection(settings)
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DATABASE()")
            rows = cursor.fetchall()
            if not rows or rows[0][0] != EXPECTED_DATABASE:
                raise LaunchError("mysql_database_mismatch")
            cursor.execute("SELECT 1")
            rows = cursor.fetchall()
            if not rows or rows[0][0] != 1:
                raise LaunchError("mysql_preflight_failed")
            for table in PRODUCT_TABLES:
                cursor.execute(f"SELECT * FROM {table} LIMIT 0")
                cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()
    return tls_version


def _stop_tunnel(tunnel: subprocess.Popen[bytes] | None) -> None:
    if tunnel is None or tunnel.poll() is not None:
        return
    tunnel.terminate()
    try:
        tunnel.wait(timeout=5)
    except subprocess.TimeoutExpired:
        tunnel.kill()
        tunnel.wait(timeout=5)


def run_session(env_path: Path) -> int:
    root = Path(__file__).resolve().parents[1]
    settings = load_settings(env_path.resolve())
    local_port = _allocate_local_port()
    tunnel = _start_tunnel(settings, local_port)
    try:
        _wait_for_tunnel(tunnel, local_port)
        _configure_runtime(settings, local_port)
        os.chdir(root)
        sys.path.insert(0, str(root))

        from app.catalog import CatalogSettings, OpenCartCatalog
        from app.config import Settings as AppSettings
        from app.journal import Journal
        from app.main import create_app

        mysql_settings = CatalogSettings(
            host=APP_HOST,
            port=local_port,
            database=settings.mysql_database,
            user=settings.mysql_user,
            password=settings.mysql_password,
        )
        tls_version = _preflight(mysql_settings)
        app_settings = AppSettings.from_env()
        journal = Journal(app_settings.journal_path)
        catalog = OpenCartCatalog(lambda: _tls_connection(mysql_settings)[0])
        app = create_app(catalog=catalog, journal=journal, settings=app_settings)

        print("mysql_database=ok q_and_a_table_permissions=ok", flush=True)
        print(
            f"mysql_tls={tls_version} required=true certificate_verification=disabled_for_local_ssh_session",
            flush=True,
        )
        print("app_url=http://127.0.0.1:8787", flush=True)
        print("/health and startup do not call OpenAI; Q&A runs only after a question is submitted.", flush=True)

        import uvicorn

        uvicorn.run(app, host=APP_HOST, port=APP_PORT, log_level="info", access_log=False)
        return 0
    finally:
        _stop_tunnel(tunnel)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local Q&A app through the approved SSH tunnel."
    )
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    arguments = parser.parse_args()
    try:
        return run_session(arguments.env_file)
    except KeyboardInterrupt:
        print("session_stopped", flush=True)
        return 130
    except LaunchError as error:
        print(f"session_start_failed={error.code}", file=sys.stderr, flush=True)
        return 1
    except Exception:
        print("session_start_failed=unexpected_error", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
