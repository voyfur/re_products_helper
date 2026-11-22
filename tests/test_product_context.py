from app.product_context import build_model_context, html_to_safe_text

from tests.conftest import sample_product


def test_product_context_uses_only_ukrainian_card():
    context = build_model_context(sample_product(), "uk")
    assert "Немає в наявності" in context
    assert "Нет в наличии" not in context
    assert "500 мл" in context


def test_description_strips_scripts_and_formats_text():
    text = html_to_safe_text("<p>Вода</p><script>alert(1)</script><p>Суміш</p>")
    assert text == "Вода\nСуміш"
    assert "alert" not in text
