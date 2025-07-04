#!/bin/sh
set -e

mkdir -p /app/.streamlit

cat > /app/.streamlit/secrets.toml <<EOF
CORPUS_API="${CORPUS_API}"
CORPUS_URL="${CORPUS_URL}"
DB_API="${DB_API}"
DB_DEV_URL="${DB_DEV_URL}"
DB_LEAD_URL="${DB_LEAD_URL}"
GITLAB_API="${GITLAB_API}"
GITLAB_URL="${GITLAB_URL}"
EOF

# Run the Streamlit app
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
