from __future__ import annotations

import pytest
from app.product_context import Attribute, LanguageCard, Product
from app.suggested_questions import (
    SUGGESTED_QUESTIONS_MATRIX,
    detect_product_group,
    get_suggested_questions,
)


def _make_prod(name: str, desc: str = "") -> Product:
    return Product(
        product_id=100,
        article="TEST",
        model="TEST",
        sku="12345",
        languages={
            "uk": LanguageCard(
                language="uk",
                name=name,
                description=desc,
                attributes=(),
                stock_label="В наявності",
            )
        },
    )


def test_matrix_all_groups_have_exactly_six_questions():
    assert len(SUGGESTED_QUESTIONS_MATRIX) >= 24
    for group_name, questions in SUGGESTED_QUESTIONS_MATRIX.items():
        assert len(questions) == 6, f"{group_name} must have exactly 6 questions"
        for q in questions:
            assert isinstance(q, str) and len(q) > 10
            assert q.endswith("?"), f"Question '{q}' should end with '?'"


@pytest.mark.parametrize(
    "name,expected_group",
    [
        ("Енергетичний гель SiS Beta Fuel Energy Gel + Nootropics (яблуко) 60 мл", "ENERGY_GELS_CAFFEINE"),
        ("Гель вуглеводний з кофеїном Sponser Liquid Energy Gels Plus 70 г", "ENERGY_GELS_CAFFEINE"),
        ("Енергетичний гель Maurten Gel 100 (нейтральний) 40 г", "ENERGY_GELS_HIGH_CARB"),
        ("Енергетичний гель SiS Beta Fuel Dual Source 60 мл", "ENERGY_GELS_HIGH_CARB"),
        ("Енергетичний гель SiS GO Isotonic Energy Gel 60 мл", "ENERGY_GELS_STANDARD"),
        ("Мармелад енергетичний PF 30 Chew 34 г", "ENERGY_CHEWS_BAKES"),
        ("Печиво з начинкою SiS GO Energy Bake (тірамісу) 50 г", "ENERGY_CHEWS_BAKES"),
        ("Напій енергетичний SiS Go Energy (чорна смородина) 1,6 кг", "ENERGY_POWDERS_DRINKS"),
        ("Енергетичний напій Sponser Long Energy 1000 г", "ENERGY_POWDERS_DRINKS"),
        ("Ізотонік Precision Hydration 1500 Tube 10 таблеток", "ELECTROLYTES_TABLETS"),
        ("Електроліти в шипучих таблетках SiS Hydro 20 таблеток", "ELECTROLYTES_TABLETS"),
        ("Ізотонік Olimp Iso Plus Powder 1505 г", "ISOTONIC_POWDER"),
        ("Сольові капсули Sponser Salt Caps 120 капсул", "SALT_CAPS"),
        ("Казеїновий протеїн Nutrend Micellar Casein 2250 г", "PROTEIN_CASEIN"),
        ("Веганський протеїн Myprotein Impact Pea Protein 1000 г", "PROTEIN_VEGAN"),
        ("Сироватковий протеїн PureGold Compact Whey Gold 500 г", "PROTEIN_WHEY"),
        ("Ізолят протеїну Sponser Whey Isolate 94 1500 г", "PROTEIN_WHEY"),
        ("Відновлювальний напій Sponser Recovery Shake 900 г", "RECOVERY_COMPLEX"),
        ("Гейнер PureGold Big Mass Gainer 3000 г", "MASS_GAINER"),
        ("Креатин моногідрат Myprotein Creatine Monohydrate 500 г", "CREATINE"),
        ("Цитрулін малат BioTechUSA Citrulline Malate 300 г", "AMINO_ACIDS_PUMP"),
        ("L-аргінін Now Foods L-Arginine 500 мг 100 капсул", "AMINO_ACIDS_PUMP"),
        ("Передтренувальний комплекс Sponser Activator 200 25 мл", "PRE_WORKOUT_STIMULANTS"),
        ("Кофеїн в капсулах Sponser Caffeine Caps 90 капсул", "PRE_WORKOUT_STIMULANTS"),
        ("Протеїновий батончик Nutrend Denuts Protein 50 г", "BARS_SNACKS"),
        ("Арахісова паста Nutrend Denuts Cream 250 г", "NUT_BUTTERS"),
        ("Вівсянка з полуницею і бананом ЇDLO 100 г", "FUNCTIONAL_FOOD"),
        ("Рисовий пудинг Olimp Cream of rice 1000 г", "FUNCTIONAL_FOOD"),
        ("Колаген для суглобів Nutrend Flexit Drink 400 г", "JOINTS_COLLAGEN"),
        ("Вітаміни та мінерали OstroVit Omega-3 D3+K2 90 капсул", "VITAMINS_MINERALS"),
        ("Шейкер спортивний Wave 500 мл", "ACCESSORIES_SHAKERS"),
        ("Фляга спортивна м'яка soft flask 500 мл", "ACCESSORIES_FLASKS"),
        ("Спортивна сувенірна чашка", "GENERAL_FALLBACK"),
    ],
)
def test_detect_product_group_and_returns_six_questions(name: str, expected_group: str):
    product = _make_prod(name)
    detected = detect_product_group(product)
    assert detected == expected_group
    questions = get_suggested_questions(product)
    assert len(questions) == 6
