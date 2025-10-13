# Imagem oficial do Python
FROM python:3.12-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Dependênciasdo sistema (se necessário)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Arquivos de dependências primeiro (para cache eficiente)
COPY requirements.txt /app/
# Instalação das dependências
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar todo o código da aplicação
COPY . /app

# Expor a porta que o Django irá rodar
EXPOSE 8000

# Variável de ambiente para Django
ENV DJANGO_SETTINGS_MODULE=api.settings

# Comando padrão para rodar o Django para produção
CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
