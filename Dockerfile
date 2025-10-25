FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements.txt README.md /app/
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir .
COPY src /app/src
COPY configs /app/configs
COPY scripts /app/scripts
CMD ["unreanchor", "--help"]
