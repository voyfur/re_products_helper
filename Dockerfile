FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt     && addgroup --system --gid 10001 qa     && adduser --system --uid 10001 --ingroup qa --no-create-home qa

COPY app ./app
COPY prompts/product-assistant-system-v12.md ./prompts/product-assistant-system-v12.md
COPY prompts/product-assistant-system-v13.md ./prompts/product-assistant-system-v13.md
COPY prompts/product-assistant-system-v14.md ./prompts/product-assistant-system-v14.md
COPY prompts/product-assistant-system-v15.md ./prompts/product-assistant-system-v15.md
COPY prompts/product-assistant-system-v16.md ./prompts/product-assistant-system-v16.md
COPY prompts/product-assistant-system-v17.md ./prompts/product-assistant-system-v17.md
COPY scripts/backup_journal.py ./scripts/backup_journal.py
RUN chown -R 10001:10001 /app

USER 10001:10001
EXPOSE 8787
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8787", "--no-access-log"]
