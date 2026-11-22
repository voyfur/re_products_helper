# Product QA Evaluation

## Наборы и исходные данные

- `product-contexts.json` — структурированные утверждённые тестовые факты и ограничения по товарам.
- `model-contexts.json` — воспроизводимый RU/UA-контекст, собранный скриптом из структурированных фактов; каждый контекст содержит проверенные модель и SKU, чтобы модель могла закрепить ответ за текущим товаром. Это тестовая проекция, не подтверждённый payload будущего backend.
- `product-qa-cases.jsonl` — 60 development/regression вопросов: 20 на товар, поровну RU/UA.
- `holdout-cases.jsonl` — 30 вопросов для отложенной проверки: 10 на товар, поровну RU/UA. Набор подготовлен в рамках этой же работы и потому не считается независимым слепым тестом.
- `guardrail-cases.jsonl` — отдельные 30 RU/UA вопросов: 10 на товар, по пять парных сценариев для грубого, бессмысленного или направленного на извлечение закрытых данных ввода. Этот пакет не смешивается с текущими 60/30 прогонами.
- `guardrail-model-contexts.json` — отдельные тестовые контексты с синтетическими маркерами секрета и данных покупателя. Маркеры заведомо фальшивые, нужны только для проверки, что модель не цитирует закрытое даже при его случайном попадании в контекст; в production их и реальные секреты/данные передавать нельзя.
- Единица вопроса и единица сценария различаются: 60 development-вопросов — это 30 парных RU/UA сценариев (10 сценариев на товар); текущие 30 holdout-вопросов — 15 парных сценариев (5 на товар). Порог `29/30` оценивает языковые ответы, а не 30 независимых ситуаций.
- Для финального независимого blind-gate нужен отдельный набор после заморозки prompt: 60 вопросов, 30 парных RU/UA сценариев и 10 уникальных сценариев на каждый товар. Его должен составить независимый автор по проверенным фактам; после раскрытия результатов набор нельзя использовать для настройки этого prompt.
- `validate_eval.py` проверяет баланс и обязательные категории по каждому товару во всех наборах, а для RU/UA-пары — одинаковую категорию и набор критических тегов. `check_acceptance.py` перед оценкой сверяет метаданные ответа с выбранным кейсом, отклоняет пустые/повторяющиеся/некорректные теги и проверяет структуру RU/UA-пар и покрытие категорий. В режиме `compare` передавай через `--models` полный список ожидаемых моделей: без него запуск отклоняется, чтобы модель с нулём результатов не исчезла из отчёта. В режиме `fallback` этот параметр не нужен.
- `../prompts/product-assistant-system-v0.md`–`v7.md` — история промпта; v5 — последняя версия с завершёнными точечными модельными проверками, v6 — заморожен для текущего сравнения, v7 добавляет Guardrails и ждёт отдельного модельного прогона.
- `acceptance-criteria.md` и `scoring-rubric.md` — заранее заданные пороги и шкала.
- `runs/` — неизменяемые результаты запусков. Не записывай туда API-ключ.

## Локальная проверка фикстур и инструментов

Из корня проекта:

```sh
python3 evals/render_contexts.py
python3 evals/render_guardrail_contexts.py
python3 evals/validate_eval.py
python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance
```

Первый рендерер без `--output` обновляет `model-contexts.json`; второй строит из него отдельные synthetic-canary контексты для Guardrails. Валидатор проверяет баланс base/holdout/guardrail-наборов, RU/UA-пары и совпадение критических тегов, наличие canary-контекстов и источников, соответствие model/SKU текущему товару, а также что числовые факты и распознанные единицы из `must_cover` присутствуют в контексте именно этого товара и языка. Например, 500 мл не считается равным 500 г. Эти проверки не заменяют смысловую ручную оценку.

## Проверка бесплатных моделей и прогон

`--provider auto` (по умолчанию) сначала проверяет OpenRouter: наличие нужных моделей `:free`, нулевую цену и остаток квоты. Если OpenRouter не проходит preflight, runner переключается на Gemini. Ключи читаются только из соответствующих переменных окружения либо точных строк корневого `.env`: `OPENROUTER_API_KEY` и `GEMINI_API`; файл не загружается целиком.

Для проекта Race в Google AI Studio на 2026-11-11 отображались Free-tier лимиты модели `gemini-3.1-flash-lite`: **15 RPM, 250 000 входных токенов в минуту, 500 RPD**. В таблице пиков за 28 дней отображалось 4/15 RPM, 1,48K/250K TPM и 11/500 RPD; это исторический пик, а не текущий остаток дневной квоты. Runner отправляет Gemini запросы последовательно, максимум **10 RPM**; делает до двух повторов с экспоненциальной задержкой, jitter и учётом `Retry-After`/`RetryInfo`, максимум 60 секунд ожидания на повтор. Ошибку дневной квоты он не повторяет, а переключает провайдера. Google сообщает, что RPD сбрасывается в полночь по Pacific Time, а фактические лимиты следует сверять в [Google AI Studio Rate Limit](https://aistudio.google.com/rate-limit) и [документации Gemini](https://ai.google.dev/gemini-api/docs/rate-limits).

Если оба provider preflight не проходят, runner повторно проверяет их каждые 15 секунд до 120 секунд. После этого он завершается с кодом 75 и сообщением `PAUSED`; генерации не отправляются. В режиме `auto` результаты разных провайдеров пишутся в отдельные файлы с суффиксами `-openrouter` и `-gemini`, а при переключении полный набор запускается заново, чтобы ответы не смешивались в одном сравнении.

Набор моделей по умолчанию: Nemotron 3 Ultra, Nemotron 3.5 Lightning и Nemotron 3.5 Super VL. Каждая недавно вернула ответ на одном и том же критическом кейсе; Xing4.0 в той же проверке вернул HTTP 429. Это выбор по наблюдаемой доступности, не по сравнительному качеству. Перед каждым запуском все IDs проверяются в текущем каталоге; при необходимости набор задаётся через `--models`.

Сначала выполни проверку без генераций:

```sh
python3 evals/run_eval.py --provider auto --preflight-only
```

Сравнение трёх моделей на одном наборе:

```sh
python3 evals/run_eval.py \
  --cases evals/product-qa-cases.jsonl \
  --prompt prompts/product-assistant-system-v6.md \
  --provider auto \
  --mode compare \
  --output evals/runs/compare-v6-auto.jsonl \
  --request-cap 45
```

Продолжение того же прогона после UTC-сброса квоты:

```sh
python3 evals/run_eval.py \
  --cases evals/product-qa-cases.jsonl \
  --prompt prompts/product-assistant-system-v6.md \
  --provider auto \
  --mode compare \
  --output evals/runs/compare-v6-auto.jsonl \
  --request-cap 45 --resume
```

Проверка fallback на отложенном наборе запускается после фиксации prompt-кандидата и полного compare. Runner повторяет временные ошибки, затем пробует следующую бесплатную модель:

```sh
python3 evals/run_eval.py \
  --cases evals/holdout-cases.jsonl \
  --prompt prompts/product-assistant-system-v6.md \
  --provider auto \
  --mode fallback \
  --output evals/runs/fallback-v6-holdout.jsonl \
  --retries 1 --request-cap 45
```

Если дневная квота закончилась, повтори ту же команду с `--resume` после UTC-сброса. Затем создай review-очередь через `prepare_review.py`, вручную оцени финальные ответы и проверь `--profile holdout` в `check_acceptance.py` без `--models`. Не продолжай fallback по holdout, если его ответы уже использовались для изменения той же версии prompt.

Целевая проверка v6 после исчерпания квоты: повторить проблемный украинский конфликт упаковки, проверить два соседних вопроса о товаре и prompt injection, затем те же четыре категории по-русски. Один retry разрешён на каждый кейс, общий предел — 16 вызовов:

```sh
python3 evals/run_eval.py \
  --cases evals/product-qa-cases.jsonl \
  --prompt prompts/product-assistant-system-v6.md \
  --provider auto \
  --models nvidia/nemotron-3.5-lightning:free \
  --mode compare \
  --case-ids re89157-uk-05 re89157-uk-06 re89157-uk-07 re89157-uk-10 re89157-ru-05 re89157-ru-06 re89157-ru-07 re89157-ru-10 \
  --output evals/runs/spotcheck-v6-lightning-packaging.jsonl \
  --retries 1 --request-cap 16
```

После ответа создай score-очередь для этих восьми кейсов через `prepare_review.py` и оцени каждый ответ до изменения prompt. Если v6 не проходит конфликт/язык или вызывает регрессию, меняй prompt и повторяй только провал и соседние кейсы в новом output-файле.

При resume runner проверяет fingerprint prompt, контекстов, вопросов, моделей, провайдера и параметров. Для изменённого входа создай новый файл результата. Режим `compare` завершает кейс на каждой модели; `fallback` повторяет временные сетевые/5xx/429 ошибки, пустой и усечённый ответ, а постоянную ошибку конкретной модели сразу передаёт следующей. Исчерпание дневной квоты не повторяется; в режиме `auto` runner переключает весь benchmark на другой провайдер и использует отдельный output-файл. Ошибка авторизации также переключает провайдера.

По данным OpenRouter, варианты `:free` ограничены 20 запросами в минуту и 50 в день; неудачные запросы тоже учитываются. [Каталог бесплатных моделей](https://openrouter.ai/collections/free-models) и [документация лимитов API](https://openrouter.ai/docs/api_reference/limits) могут обновляться. В `GET /api/v1/key` поле `free_model_daily_requests` показывает использованные и оставшиеся вызовы за текущий UTC-день. Runner берёт минимум из остатка и `--request-cap` (для OpenRouter по умолчанию 45); для Gemini по умолчанию резервирует одну попытку и заданные retries на каждый выбранный кейс, в пределах 500 RPD из текущего AI Studio снимка. Не запускай платные ID и не покупай кредиты ради оценки. Используй один output на провайдера и fingerprint; продолжай прерванный прогон через `--resume`.

Для прогона через OpenAI API ключ читается только из `OPENAI` в `.env`; режим не переключается на другие провайдеры. Модель по умолчанию — `gpt-6-luna`. Этот API отклоняет `temperature=0`, поэтому runner оставляет температуру и reasoning effort на настройках модели по умолчанию и записывает их в provenance. Результаты нужно считать отдельной диагностикой, а не строго сопоставимым прогоном с провайдерами, где задана температура `0`. Сначала проверь доступность без генерации, затем запусти отдельный файл результатов:

```sh
python3 evals/run_eval.py --provider openai --openai-model gpt-6-luna --preflight-only

python3 evals/run_eval.py \
  --cases evals/product-qa-cases.jsonl \
  --prompt prompts/product-assistant-system-v6.md \
  --provider openai \
  --openai-model gpt-6-luna \
  --mode compare \
  --output evals/runs/compare-v6-gpt-6-luna-model-defaults.jsonl \
  --request-cap 120
```

Запросы используют Responses API с `store=false`. Если прогон прервался, повтори команду запуска с `--resume`; не меняй prompt, контексты, кейсы или параметры в том же файле.

## Ручная оценка и отчёт

Создай очередь финальных ответов:

```sh
python3 evals/prepare_review.py \
  --runs evals/runs/compare-v5.jsonl \
  --cases evals/product-qa-cases.jsonl \
  --output evals/runs/review-v5.jsonl
```

Строка очереди содержит не только вопрос и ответ, но и точный контекст из `--contexts`, его `context_sha256`, `pair_id`, ожидаемое поведение, `must_cover`, `must_not_claim`, ожидаемые критические теги и `source_ref`. Скрипт сверяет hash контекста с запуском; если при тесте использовался другой файл контекстов, передай тот же путь через `--contexts`. Сверяй ответ с этим контекстом и критериями до выставления баллов.

В каждой строке заполни `factual_accuracy`, `uncertainty`, `scope`, `language_quality` числами `0`, `1` или `2`, `total` суммой этих полей, `critical_failure_tags` — массивом тегов, `notes` — объяснением спорных оценок. Поле `language` сохраняет RU/UA-код кейса. Для holdout укажи `--cases evals/holdout-cases.jsonl`. API-ошибки и пустые ответы в очередь не попадают и не получают оценку качества.

Построй JSON-отчёт:

```sh
python3 evals/report_runs.py \
  --runs evals/runs/compare-v5.jsonl \
  --scores evals/runs/review-v5.jsonl \
  --output evals/runs/report-v5.json
```

Отчёт разделяет качество и доступность, показывает модели, языки, товары и категории, а в fallback-режиме считает итог на один кейс и выбранную модель. Не сравнивай средний score при разном наборе оцениваемых кейсов.

Проверь автоматические пороги после ручной оценки. Для полного regression compare:

```sh
python3 evals/check_acceptance.py \
  --runs evals/runs/compare-v6.jsonl \
  --scores evals/runs/review-v6.jsonl \
  --cases evals/product-qa-cases.jsonl \
  --profile regression \
  --models nvidia/nemotron-3-ultra-550b-a55b:free nvidia/nemotron-3.5-lightning:free nvidia/nemotron-3.5-super-vl:free
```

Для текущего диагностического holdout передай `--profile holdout --cases evals/holdout-cases.jsonl`; для независимого набора из 60 вопросов — `--profile blind` и его файл через `--cases`. В режиме `compare` также обязательно передай через `--models` полный список ожидаемых моделей; в fallback-режиме этот параметр не нужен. Проверка выдаёт `pass`, `fail` или `incomplete`, разделяет доступность и качество, и завершается кодом 1 при провале либо нехватке доказательств. До оценки она проверяет, что каждая строка прогона содержит корректные SHA-256 `run_fingerprint`, `prompt_sha256` и `context_sha256`, а весь файл относится к одному fingerprint и одному prompt hash; неполные или смешанные provenance получают статус `incomplete`.

## Отдельный прогон Guardrails

Guardrail-пакет проверяет пять поведений: ответ на полезный вопрос несмотря на ругань; спокойный редирект при одних оскорблениях или бессмыслице; отказ раскрывать системные инструкции/секреты; защита данных покупателей. Текущие v6-прогоны оставлены без изменений; v7 прогоняй отдельно после доступного окна квоты:

```sh
python3 evals/run_eval.py \
  --cases evals/guardrail-cases.jsonl \
  --contexts evals/guardrail-model-contexts.json \
  --prompt prompts/product-assistant-system-v7.md \
  --models nvidia/nemotron-3-ultra-550b-a55b:free nvidia/nemotron-3.5-lightning:free nvidia/nemotron-3.5-super-vl:free \
  --mode compare \
  --output evals/runs/compare-v7-guardrails.jsonl \
  --retries 1 --request-cap 45
```

В guardrail-профиле acceptance автоматически ищет в ответах синтетические canary-маркеры и проваливает gate при их повторении, даже если разметчик не отметил критическую ошибку. После завершения прогона подготовь очередь с тем же контекстным файлом, вручную оцени каждый ответ, затем проверь профиль `guardrail` с тем же полным списком моделей. При нулевой квоте продолжай тот же fingerprint через `--resume` после UTC-сброса.

Очередь для ручной оценки создавай с тем же контекстом, который использовал runner:

```sh
python3 evals/prepare_review.py \
  --runs evals/runs/compare-v7-guardrails.jsonl \
  --cases evals/guardrail-cases.jsonl \
  --contexts evals/guardrail-model-contexts.json \
  --output evals/runs/review-v7-guardrails.jsonl
```

## Интерпретация

Один вызов endpoint подтверждает только доступность API, не качество. GPT-6 Luna с системным prompt v11 прошла 60-кейсовый regression и отдельные guardrail-пороги; раскрытый holdout также прошёл числовые пороги только как диагностика, а не как независимый blind-тест. Fallback и интеграция с реальной карточкой в этой проверке не выполнялись. Для end-to-end подтверждения всё ещё нужны фактический payload backend и проверка связи с открытым товаром.

Все доступные исторические ответы v0–v5 размечены в `runs/review-all-historical-v0-v5.jsonl`; агрегат — `runs/report-all-historical-v0-v5.json`. Это диагностика на 31 ответе из частичных прогонов, не полный benchmark и не допуск к внедрению. Старые логи не содержат хешей контекста/prompt.

## Проверенный GPT-6 Luna prompt v11 — 2026-11-11

Текущий prompt-кандидат: `prompts/product-assistant-system-v11.md`, SHA-256 `5775f9e8c3909bc9cc39668f312b9e6838aa82c0c00b234b7f0671bf384c854d`. V11 добавляет к числовому запрету v9 более явное правило языка: переводить обычные фразы из контекста, не копировать их на другом языке; точные имена, бренды и необходимые локализованные метки сохраняются. Все прежние версии и результаты не перезаписываются.

Параметры всех v11 запусков: OpenAI Responses API, `store=false`, `temperature` не передаётся, `reasoning_effort=medium`, `max_output_tokens=2048`. CLI ограничивает 60-кейсовый пакет 120 вызовами, оставляя стандартный retry; для каждого 30-кейсового пакета — предел 60. Итоговые v11 пакеты использовали по одному вызову на кейс.

### Regression — 60 вопросов

```sh
python3 -B evals/run_eval.py \
  --cases evals/product-qa-cases.jsonl \
  --contexts evals/model-contexts.json \
  --prompt prompts/product-assistant-system-v11.md \
  --provider openai \
  --openai-model gpt-6-luna \
  --mode compare \
  --output evals/runs/compare-v11-gpt-6-luna-regression.jsonl \
  --retries 1 --request-cap 120

python3 -B evals/prepare_review.py \
  --runs evals/runs/compare-v11-gpt-6-luna-regression.jsonl \
  --cases evals/product-qa-cases.jsonl \
  --contexts evals/model-contexts.json \
  --output evals/runs/review-v11-gpt-6-luna-regression.jsonl

python3 -B evals/check_acceptance.py \
  --runs evals/runs/compare-v11-gpt-6-luna-regression.jsonl \
  --scores evals/runs/review-v11-gpt-6-luna-regression.jsonl \
  --cases evals/product-qa-cases.jsonl \
  --profile regression --models gpt-6-luna --regression-quality-gates \
  --output evals/runs/acceptance-v11-gpt-6-luna-regression.json

python3 -B evals/report_runs.py \
  --runs evals/runs/compare-v11-gpt-6-luna-regression.jsonl \
  --scores evals/runs/review-v11-gpt-6-luna-regression.jsonl \
  --output evals/runs/report-v11-gpt-6-luna-regression.json
```

Результат: `pass`; 60/60 ответов, средний балл 8/8, ноль критических ошибок; все группы «товар × язык» 8/8.

### Раскрытый holdout — 30 вопросов, только диагностика

```sh
python3 -B evals/run_eval.py \
  --cases evals/holdout-cases.jsonl \
  --contexts evals/model-contexts.json \
  --prompt prompts/product-assistant-system-v11.md \
  --provider openai \
  --openai-model gpt-6-luna \
  --mode compare \
  --output evals/runs/compare-v11-gpt-6-luna-holdout-diagnostic.jsonl \
  --retries 1 --request-cap 60

python3 -B evals/prepare_review.py \
  --runs evals/runs/compare-v11-gpt-6-luna-holdout-diagnostic.jsonl \
  --cases evals/holdout-cases.jsonl \
  --contexts evals/model-contexts.json \
  --output evals/runs/review-v11-gpt-6-luna-holdout-diagnostic.jsonl

python3 -B evals/check_acceptance.py \
  --runs evals/runs/compare-v11-gpt-6-luna-holdout-diagnostic.jsonl \
  --scores evals/runs/review-v11-gpt-6-luna-holdout-diagnostic.jsonl \
  --cases evals/holdout-cases.jsonl \
  --profile holdout --models gpt-6-luna \
  --output evals/runs/acceptance-v11-gpt-6-luna-holdout-diagnostic.json

python3 -B evals/report_runs.py \
  --runs evals/runs/compare-v11-gpt-6-luna-holdout-diagnostic.jsonl \
  --scores evals/runs/review-v11-gpt-6-luna-holdout-diagnostic.jsonl \
  --output evals/runs/report-v11-gpt-6-luna-holdout-diagnostic.json
```

Результат: `pass`; 30/30, средний балл 7,967/8, ноль критических ошибок; максимальный RU/UA разрыв 0,2. Набор раскрыт при проверке v8 и **не является независимым blind-тестом**.

### Guardrails — 30 вопросов с синтетическими canary-контекстами

```sh
python3 -B evals/run_eval.py \
  --cases evals/guardrail-cases.jsonl \
  --contexts evals/guardrail-model-contexts.json \
  --prompt prompts/product-assistant-system-v11.md \
  --provider openai \
  --openai-model gpt-6-luna \
  --mode compare \
  --output evals/runs/compare-v11-gpt-6-luna-guardrails.jsonl \
  --retries 1 --request-cap 60

python3 -B evals/prepare_review.py \
  --runs evals/runs/compare-v11-gpt-6-luna-guardrails.jsonl \
  --cases evals/guardrail-cases.jsonl \
  --contexts evals/guardrail-model-contexts.json \
  --output evals/runs/review-v11-gpt-6-luna-guardrails.jsonl

python3 -B evals/check_acceptance.py \
  --runs evals/runs/compare-v11-gpt-6-luna-guardrails.jsonl \
  --scores evals/runs/review-v11-gpt-6-luna-guardrails.jsonl \
  --cases evals/guardrail-cases.jsonl \
  --profile guardrail --models gpt-6-luna \
  --output evals/runs/acceptance-v11-gpt-6-luna-guardrails.json

python3 -B evals/report_runs.py \
  --runs evals/runs/compare-v11-gpt-6-luna-guardrails.jsonl \
  --scores evals/runs/review-v11-gpt-6-luna-guardrails.jsonl \
  --output evals/runs/report-v11-gpt-6-luna-guardrails.json
```

Результат: `pass`; 30/30, средний балл 8/8, ноль критических ошибок и ноль synthetic canary-повторов. Ответы и контексты guardrail-пакета используют только синтетические маркеры.
