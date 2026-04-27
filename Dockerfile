FROM python:3.11-slim-bookworm

# Install uv via pip
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy only dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install all dependencies into the system python (not a venv)
# --system flag tells uv to install into the system Python, avoiding venv path issues
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code
COPY . .

EXPOSE 7536

# Run the application using the system Python (which now has all packages)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7536"]
