# Guia de Implantação: Backend FastAPI da Matriz de Eisenhower Colaborativa

Este guia fornece instruções detalhadas para implantar o backend FastAPI da sua Matriz de Eisenhower Colaborativa em diferentes plataformas de hospedagem.

## Estrutura do Projeto

O backend está organizado da seguinte forma:

```
eisenhower_collaborative_app/
├── requirements.txt         # Dependências Python
├── src/
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── database.py          # Configuração do banco de dados
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic
│   └── routes.py            # Rotas da API
```

## Requisitos Gerais

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Dependências listadas em `requirements.txt`

## Opção 1: Deploy no Heroku

O Heroku é uma plataforma como serviço (PaaS) que facilita a implantação de aplicações web.

### Pré-requisitos
- Conta no Heroku
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado
- Git instalado

### Passos para Deploy

1. **Preparar o projeto para o Heroku**

   Crie um arquivo `Procfile` na raiz do projeto com o seguinte conteúdo:
   ```
   web: uvicorn src.main:app --host=0.0.0.0 --port=${PORT:-8000}
   ```

   Crie um arquivo `runtime.txt` na raiz do projeto especificando a versão do Python:
   ```
   python-3.9.7
   ```

2. **Inicializar um repositório Git (se ainda não existir)**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Heroku deployment"
   ```

3. **Criar uma aplicação no Heroku**
   ```bash
   heroku login
   heroku create seu-app-name
   ```

4. **Implantar no Heroku**
   ```bash
   git push heroku main
   ```

5. **Verificar logs (se necessário)**
   ```bash
   heroku logs --tail
   ```

6. **Acessar a aplicação**
   ```bash
   heroku open
   ```

   Ou acesse: `https://seu-app-name.herokuapp.com`

## Opção 2: Deploy com Docker

Docker permite empacotar a aplicação e suas dependências em um contêiner isolado.

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) (opcional, mas recomendado)

### Passos para Deploy

1. **Criar um Dockerfile**

   Crie um arquivo `Dockerfile` na raiz do projeto:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Criar um arquivo docker-compose.yml (opcional)**

   ```yaml
   version: '3'
   services:
     api:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - .:/app
   ```

3. **Construir e executar o contêiner**

   Com Docker Compose:
   ```bash
   docker-compose up --build
   ```

   Ou diretamente com Docker:
   ```bash
   docker build -t eisenhower-matrix-api .
   docker run -p 8000:8000 eisenhower-matrix-api
   ```

4. **Acessar a aplicação**

   Acesse: `http://localhost:8000`

## Opção 3: Deploy em VPS (Servidor Virtual Privado)

Esta opção é mais avançada e oferece maior controle sobre o ambiente.

### Pré-requisitos
- Servidor Linux (Ubuntu, Debian, etc.)
- SSH configurado
- Python 3.8+ instalado no servidor
- Nginx ou outro servidor web (opcional, mas recomendado)

### Passos para Deploy

1. **Transferir arquivos para o servidor**

   ```bash
   scp -r eisenhower_collaborative_app/ usuario@seu-servidor:/caminho/para/app
   ```

2. **Conectar ao servidor via SSH**

   ```bash
   ssh usuario@seu-servidor
   ```

3. **Configurar o ambiente**

   ```bash
   cd /caminho/para/app
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configurar Systemd para gerenciar o serviço**

   Crie um arquivo de serviço:
   ```bash
   sudo nano /etc/systemd/system/eisenhower-api.service
   ```

   Adicione o seguinte conteúdo:
   ```
   [Unit]
   Description=Eisenhower Matrix API
   After=network.target

   [Service]
   User=seu-usuario
   WorkingDirectory=/caminho/para/app
   ExecStart=/caminho/para/app/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Iniciar o serviço**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start eisenhower-api
   sudo systemctl enable eisenhower-api
   ```

6. **Configurar Nginx como proxy reverso (opcional, mas recomendado)**

   Instalar Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

   Configurar site:
   ```bash
   sudo nano /etc/nginx/sites-available/eisenhower-api
   ```

   Adicionar configuração:
   ```
   server {
       listen 80;
       server_name seu-dominio.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   Ativar site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/eisenhower-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Configurar HTTPS com Certbot (opcional, mas recomendado)**

   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d seu-dominio.com
   ```

## Opção 4: Deploy no Google Cloud Run

Google Cloud Run é um serviço gerenciado para executar contêineres sem servidor.

### Pré-requisitos
- Conta no Google Cloud Platform
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) instalado
- Docker instalado

### Passos para Deploy

1. **Inicializar o Google Cloud SDK**

   ```bash
   gcloud init
   ```

2. **Criar um Dockerfile** (mesmo do exemplo Docker acima)

3. **Construir e enviar a imagem para o Google Container Registry**

   ```bash
   gcloud builds submit --tag gcr.io/seu-projeto/eisenhower-api
   ```

4. **Implantar no Cloud Run**

   ```bash
   gcloud run deploy eisenhower-api \
     --image gcr.io/seu-projeto/eisenhower-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

5. **Acessar a aplicação**

   O URL será fornecido na saída do comando de implantação.

## Configuração do Frontend

Depois de implantar o backend, você precisará atualizar o frontend para apontar para o novo URL do backend:

1. No arquivo `App.js` do frontend, localize a linha:
   ```javascript
   const API_BASE_URL = "https://8000-io2m3it5cy93w7r303rkl-092dd6d3.manusvm.computer/api/v1";
   ```

2. Substitua pelo URL do seu backend implantado:
   ```javascript
   const API_BASE_URL = "https://seu-backend-implantado.com/api/v1";
   ```

3. Reconstrua e reimplante o frontend.

## Considerações de CORS

Se você estiver hospedando o frontend e o backend em domínios diferentes, certifique-se de que as configurações CORS no arquivo `main.py` incluam o domínio do seu frontend:

```python
origins = [
    "http://localhost:3000",
    "https://seu-frontend.com",  # Adicione o domínio do seu frontend aqui
]
```

## Solução de Problemas

### Erro de Conexão com o Banco de Dados
- Verifique se o arquivo do banco de dados SQLite tem permissões de escrita
- Para ambientes de produção, considere migrar para PostgreSQL ou MySQL

### Erros de CORS
- Verifique se o domínio do frontend está listado nas origens permitidas em `main.py`
- Certifique-se de que o middleware CORS está configurado corretamente

### Erros de Porta em Uso
- Verifique se a porta 8000 (ou a que você configurou) não está sendo usada por outro serviço
- Use uma porta diferente se necessário

## Recursos Adicionais

- [Documentação do FastAPI](https://fastapi.tiangolo.com/)
- [Documentação do Uvicorn](https://www.uvicorn.org/)
- [Documentação do SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentação do Heroku](https://devcenter.heroku.com/)
- [Documentação do Docker](https://docs.docker.com/)
- [Documentação do Google Cloud Run](https://cloud.google.com/run/docs)
