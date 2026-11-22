#!/usr/bin/env python3
"""Render deterministic, buyer-readable model contexts from product facts."""

import argparse
import json
from pathlib import Path


NUTRIENT_LABELS = {
    "ru": {
        "energy_kcal": "энергия",
        "fat_g": "жиры",
        "saturated_fat_g": "насыщенные жиры",
        "carbohydrates_g": "углеводы",
        "sugars_g": "сахара",
        "protein_g": "белок",
        "salt_g": "соль",
        "digezyme_mg": "DigeZyme",
    },
    "uk": {
        "energy_kcal": "енергія",
        "fat_g": "жири",
        "saturated_fat_g": "насичені жири",
        "carbohydrates_g": "вуглеводи",
        "sugars_g": "цукри",
        "protein_g": "білок",
        "salt_g": "сіль",
        "digezyme_mg": "DigeZyme",
    },
}


def number(value):
    if isinstance(value, str):
        value = value.rstrip("0").rstrip(".") if "." in value else value
    return str(value).replace(".", ",")


def nutrient_value(key, value):
    if key.endswith("_kcal"):
        unit = "ккал"
    elif key.endswith("_mg"):
        unit = "мг"
    else:
        unit = "г"
    return f"{number(value)} {unit}"


def render_nutrients(values, language):
    return "; ".join(
        f"{NUTRIENT_LABELS[language][key]} {nutrient_value(key, value)}"
        for key, value in values.items()
    )


def render_availability(product, language):
    facts = product[language]
    availability = facts["availability"]
    if language == "ru":
        return (
            f"На карточке показано «{availability['stock_status_label']}»; "
            f"в поле количества указано {number(availability['quantity'])}, "
            "но возможность заказа по этим сведениям не подтверждена."
        )
    return (
        f"У картці показано «{availability['stock_status_label']}»; "
        f"у полі кількості зазначено {number(availability['quantity'])}, "
        "але можливість замовлення за цими відомостями не підтверджена."
    )


def render_price(facts, language):
    price = number(facts["base_price"])
    if language == "ru":
        return f"Базовая цена в карточке — {price}; валюта и специальная цена не проверялись."
    return f"Базова ціна в картці — {price}; валюту й спеціальну ціну не перевіряли."


def render_product(product, language, product_code):
    facts = product[language]
    paragraphs = [f"Товар: {facts['name']}."]
    paragraphs.append(f"Модель — {product['model']}; SKU — {product['sku']}.")

    if product_code == "RE89157":
        if language == "ru":
            paragraphs.append(
                f"В названии указано {number(facts['package_title_g'])} г, "
                f"а в описании также встречается {number(facts['package_description_also_says_g'])} г; "
                "размер упаковки противоречив."
            )
            paragraphs.append(f"Порция — {number(facts['serving_g'])} г.")
            paragraphs.append(
                f"На порцию {number(facts['serving_g'])} г: "
                f"{render_nutrients(facts['nutrition_per_32g'], language)}."
            )
            paragraphs.append(f"На 100 г: {render_nutrients(facts['nutrition_per_100g'], language)}.")
            paragraphs.append(f"Приготовление: {facts['mixing']}")
            paragraphs.append("Подсластители: " + " и ".join(facts["sweeteners"]) + ".")
            paragraphs.append("Состав: " + "; ".join(facts["ingredients"]) + ".")
        else:
            paragraphs.append(
                f"У назві зазначено {number(facts['package_title_g'])} г, "
                f"а в описі також зустрічається {number(facts['package_description_also_says_g'])} г; "
                "маса упаковки суперечлива."
            )
            paragraphs.append(f"Порція — {number(facts['serving_g'])} г.")
            paragraphs.append(
                f"На порцію {number(facts['serving_g'])} г: "
                f"{render_nutrients(facts['nutrition_per_32g'], language)}."
            )
            paragraphs.append(f"На 100 г: {render_nutrients(facts['nutrition_per_100g'], language)}.")
            paragraphs.append(f"Приготування: {facts['mixing']}")
            paragraphs.append("Підсолоджувачі: " + " й ".join(facts["sweeteners"]) + ".")
            paragraphs.append("Склад: " + "; ".join(facts["ingredients"]) + ".")

    elif product_code == "RE1687":
        if language == "ru":
            paragraphs.append("Текущая проверка подтвердила цену, поля наличия и наличие описания.")
            paragraphs.append(
                "Инструкция по приготовлению и сведения о натрии взяты из более раннего снимка описания "
                "и не перепроверены текущим запросом."
            )
            paragraphs.append(f"В более раннем описании указано: {facts['preparation_from_earlier_description']}")
            claims = "; ".join(facts["sodium_claims_from_earlier_description"])
            paragraphs.append(f"Там же указаны сведения о натрии: {claims}.")
            paragraphs.append("Точное количество натрия на таблетку не указано.")
            paragraphs.append("Точный список ингредиентов и значения таблицы электролитов в этом контексте отсутствуют.")
        else:
            paragraphs.append("Поточна перевірка підтвердила ціну, поля наявності та наявність опису.")
            paragraphs.append(
                "Інструкцію з приготування та відомості про натрій узято з давнішого знімка опису "
                "й не переперевірено поточним запитом."
            )
            paragraphs.append(f"У давнішому описі зазначено: {facts['preparation_from_earlier_description']}")
            claims = "; ".join(facts["sodium_claims_from_earlier_description"])
            paragraphs.append(f"Там само наведено відомості про натрій: {claims}.")
            paragraphs.append("Точну кількість натрію на таблетку не зазначено.")
            paragraphs.append("Точного переліку інгредієнтів і значень таблиці електролітів у цьому контексті немає.")

    elif product_code == "RE0731":
        if language == "ru":
            paragraphs.append(f"Объём — {number(facts['capacity_ml'])} мл.")
            if facts["includes_blenderball_whisk"]:
                paragraphs.append("В описании упоминается шарик-венчик BlenderBall; его функция подробно не описана.")
            paragraphs.append(facts["bpa_claim"])
            paragraphs.append(facts["closure"])
            paragraphs.append(facts["cleaning"])
            if not product[language]["real_weight_or_dimensions_confirmed"]:
                paragraphs.append("Фактический вес и габариты товара в сохранённых данных не подтверждены.")
        else:
            paragraphs.append(f"Об’єм — {number(facts['capacity_ml'])} мл.")
            if facts["includes_blenderball_whisk"]:
                paragraphs.append("В описі згадується кулька-вінчик BlenderBall; її функцію докладно не описано.")
            paragraphs.append(facts["bpa_claim"])
            paragraphs.append(facts["closure"])
            paragraphs.append(facts["cleaning"])
            if not product[language]["real_weight_or_dimensions_confirmed"]:
                paragraphs.append("Фактичну вагу й габарити товару в збережених даних не підтверджено.")
    else:
        raise ValueError(f"Unsupported product code: {product_code}")

    paragraphs.extend((render_availability(product, language), render_price(facts, language)))
    return " ".join(paragraphs)


def render_contexts(source):
    products = source["products"]
    rendered = {}
    for product_code in ("RE89157", "RE1687", "RE0731"):
        product = products[product_code]
        for language in ("ru", "uk"):
            rendered[f"{product_code}_{language}"] = render_product(product, language, product_code)
    return {
        "context_set_version": "2.2",
        "note": (
            "Контексты автоматически сформированы из product-contexts.json. "
            "Структурированные факты и источники в том файле остаются основой проверки."
        ),
        "contexts": rendered,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("evals/product-contexts.json"))
    parser.add_argument("--output", type=Path, default=Path("evals/model-contexts.json"))
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    rendered = render_contexts(source)
    args.output.write_text(json.dumps(rendered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {len(rendered['contexts'])} localized product contexts to {args.output}")


if __name__ == "__main__":
    main()
