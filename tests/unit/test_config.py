from app.core.config import Settings


def test_cors_origins_are_trimmed_and_empty_values_removed() -> None:
    settings = Settings(backend_cors_origins=" https://one.example, ,https://two.example ")

    assert settings.cors_origins == ["https://one.example", "https://two.example"]
