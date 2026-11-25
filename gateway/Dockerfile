# Estágio 1: Base de produção
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

# Estágio 2: Execução automática dos testes
FROM base AS tester
COPY requirements-dev.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
RUN pytest -v

# Estágio 3: Imagem final limpa (sem pytest e sem pasta tests/)
FROM base AS final
COPY --from=tester /app/app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]