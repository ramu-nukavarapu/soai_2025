# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy the secrets file from example to actual secrets file
COPY .streamlit/secrets.toml.example .streamlit/secrets.toml

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables for Streamlit secrets (Coolify will inject these)
# Example: STREAMLIT_SECRET_KEY, STREAMLIT_DB_URL, etc.
# You should map these in Coolify to the corresponding secrets in secrets.toml

# Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
