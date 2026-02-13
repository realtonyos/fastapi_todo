FROM python:3.11-slim

# 1. Создаём пользователя
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 --no-create-home app

WORKDIR /app

# 2. Копируем и ставим зависимости (от root, но это ок)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем код и меняем владельца
COPY --chown=app:app . .

# 4. Переключаемся на пользователя
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]