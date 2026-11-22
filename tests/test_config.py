import pytest

from app.config import Settings
from scripts import run_local_session


def clear_secret_environment(monkeypatch):
    for name in (
        "TAVILY_API_KEY",
        "TAVILY_API_KEY_FILE",
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_FILE",
        "MYSQL_PASSWORD",
        "MYSQL_PASSWORD_FILE",
        "PRODUCT_QA_API_KEY",
        "PRODUCT_QA_API_KEY_FILE",
    ):
        monkeypatch.delenv(name, raising=False)


def test_app_settings_load_tavily_file_secret_without_repr_leak(tmp_path, monkeypatch):
    clear_secret_environment(monkeypatch)
    key_file = tmp_path / "tavily-key"
    key_file.write_text("synthetic-tavily-key\n", encoding="utf-8")
    key_file.chmod(0o600)
    monkeypatch.setenv("TAVILY_API_KEY_FILE", str(key_file))

    settings = Settings.from_env()

    assert settings.tavily_api_key == "synthetic-tavily-key"
    assert "synthetic-tavily-key" not in repr(settings)


def test_app_settings_load_tavily_environment_secret_without_repr_leak(monkeypatch):
    clear_secret_environment(monkeypatch)
    monkeypatch.setenv("TAVILY_API_KEY", "synthetic-tavily-key")

    settings = Settings.from_env()

    assert settings.tavily_api_key == "synthetic-tavily-key"
    assert "synthetic-tavily-key" not in repr(settings)


def test_app_settings_leave_tavily_unconfigured_when_both_sources_are_absent(monkeypatch):
    clear_secret_environment(monkeypatch)

    assert Settings.from_env().tavily_api_key is None


def test_app_settings_reject_both_tavily_secret_sources(tmp_path, monkeypatch):
    clear_secret_environment(monkeypatch)
    key_file = tmp_path / "tavily-key"
    key_file.write_text("synthetic-file-key", encoding="utf-8")
    monkeypatch.setenv("TAVILY_API_KEY", "synthetic-env-key")
    monkeypatch.setenv("TAVILY_API_KEY_FILE", str(key_file))

    with pytest.raises(ValueError, match="tavily_configuration_invalid"):
        Settings.from_env()


def write_local_session_env(tmp_path, tavily_settings, *, unsafe_tavily_file=False):
    file_values = {
        "ssh-key": "synthetic-ssh-key",
        "mysql-password": "synthetic-mysql-password",
        "openai-key": "synthetic-openai-key",
        "tavily-key": "synthetic-tavily-key",
    }
    for name, value in file_values.items():
        path = tmp_path / name
        path.write_text(value, encoding="utf-8")
        path.chmod(0o644 if name == "tavily-key" and unsafe_tavily_file else 0o600)

    env_path = tmp_path / "local-session.env"
    env_path.write_text(
        "\n".join(
            (
                f"SSH_HOST={run_local_session.EXPECTED_SSH_HOST}",
                "SSH_USER=qa",
                "SSH_PORT=22",
                "SSH_PRIVATE_KEY_PATH=ssh-key",
                "MYSQL_HOST=database.internal",
                "MYSQL_PORT=3306",
                f"MYSQL_DATABASE={run_local_session.EXPECTED_DATABASE}",
                "MYSQL_USER=readonly",
                "MYSQL_PASSWORD_FILE=mysql-password",
                "OPENAI_API_KEY_FILE=openai-key",
                *tavily_settings,
            )
        ),
        encoding="utf-8",
    )
    env_path.chmod(0o600)
    return env_path


@pytest.mark.parametrize(
    "tavily_setting",
    ("TAVILY_API_KEY_FILE=tavily-key", "TAVILY_API_KEY=synthetic-tavily-key"),
)
def test_local_launcher_loads_tavily_secret_without_repr_leak(tmp_path, tavily_setting):
    env_path = write_local_session_env(tmp_path, [tavily_setting])
    settings = run_local_session.load_settings(env_path)

    assert settings.tavily_api_key == "synthetic-tavily-key"
    assert "synthetic-tavily-key" not in repr(settings)


@pytest.mark.parametrize(
    ("tavily_settings", "expected_error"),
    (
        ((), "tavily_configuration_missing"),
        (
            ("TAVILY_API_KEY=synthetic-env-key", "TAVILY_API_KEY_FILE=tavily-key"),
            "tavily_configuration_conflict",
        ),
    ),
)
def test_local_launcher_reports_tavily_configuration_state_safely(
    tmp_path, tavily_settings, expected_error
):
    env_path = write_local_session_env(tmp_path, tavily_settings)

    with pytest.raises(run_local_session.LaunchError) as error:
        run_local_session.load_settings(env_path)

    assert error.value.code == expected_error
    assert "synthetic-env-key" not in str(error.value)


def test_local_launcher_rejects_unsafe_tavily_key_file(tmp_path):
    env_path = write_local_session_env(
        tmp_path,
        ["TAVILY_API_KEY_FILE=tavily-key"],
        unsafe_tavily_file=True,
    )

    with pytest.raises(run_local_session.LaunchError) as error:
        run_local_session.load_settings(env_path)

    assert error.value.code == "secret_file_permissions_must_be_0600_or_stricter"
    assert "synthetic-tavily-key" not in str(error.value)
