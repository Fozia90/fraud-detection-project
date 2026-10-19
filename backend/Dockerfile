FROM python:3.11-slim

# Créer l'utilisateur non-root requis par Hugging Face (UID 1000)
RUN useradd -m -u 1000 user

# Définir le répertoire de travail
WORKDIR /home/user/app

# Copier et installer les dépendances Python
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY --chown=user . .

# Passer à l'utilisateur non-root
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Hugging Face Spaces écoute par défaut sur le port 7860
EXPOSE 7860

# Démarrer l'API FastAPI sur le port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]