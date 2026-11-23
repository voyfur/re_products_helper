from app.intent_classifier import IntentType, classify_intent, enrich_prompt_with_intent


def test_classify_intent_endurance():
    assert classify_intent("А для марафону на 42 км як приймати?") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("Чи підійде для велогонки 100 км?") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("Як пити під час бігу?") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("А для плавання в басейні норм?") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("Чи рятує цей напій від судом?") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("тобто пілся забігу?") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("ну якщо я за годину пробіжу, то це припаде на після забігу") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("Для пробіжки на 12 км") == IntentType.ENDURANCE_CARDIO
    assert classify_intent("коли пити після забігу?") == IntentType.ENDURANCE_CARDIO


def test_classify_intent_nutrition_supplements():
    assert classify_intent("Скільки калорій і цукру в одній порції?") == IntentType.NUTRITION_SUPPLEMENTS
    assert classify_intent("Який точний вміст вуглеводів і білка?") == IntentType.NUTRITION_SUPPLEMENTS
    assert classify_intent("Що таке мальтодекстрин у складі?") == IntentType.NUTRITION_SUPPLEMENTS
    assert classify_intent("Чи є сертифікат Informed Sport?") == IntentType.NUTRITION_SUPPLEMENTS
    assert classify_intent("Як він для шлунка, легко засвоюється?") == IntentType.NUTRITION_SUPPLEMENTS


def test_classify_intent_gym_strength_combat():
    assert classify_intent("Окей, супер, для борьбі норм?") == IntentType.GYM_STRENGTH_COMBAT
    assert classify_intent("Я займаюся грепплінгом, коли краще пити?") == IntentType.GYM_STRENGTH_COMBAT
    assert classify_intent("А для боксу підійде?") == IntentType.GYM_STRENGTH_COMBAT
    assert classify_intent("Чи підійде для тренажерного залу на ноги?") == IntentType.GYM_STRENGTH_COMBAT
    assert classify_intent("Підійде для набору маси?") == IntentType.GYM_STRENGTH_COMBAT
    assert classify_intent("Для кросфіту норм?") == IntentType.GYM_STRENGTH_COMBAT


def test_classify_intent_general_product():
    assert classify_intent("А що це взагалі за бренд?") == IntentType.GENERAL_PRODUCT
    assert classify_intent("Хто виробник цього товару?") == IntentType.GENERAL_PRODUCT
    assert classify_intent("Які є смаки в наявності?") == IntentType.GENERAL_PRODUCT


def test_enrich_prompt_with_intent():
    base = "Base prompt instructions"
    enriched = enrich_prompt_with_intent(base, IntentType.GYM_STRENGTH_COMBAT)
    assert base in enriched
    assert "Тренажерний зал, силові та єдиноборства" in enriched
