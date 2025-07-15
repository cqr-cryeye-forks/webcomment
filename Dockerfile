FROM python:3.13-slim AS runner
WORKDIR /app
COPY webcomment.py .
ENTRYPOINT ["python3", "webcomment.py"]
