```markdown
# 🛍️ E-commerce API

API de e-commerce desenvolvida em **Python**, utilizando **Django** + **Django REST Framework**.  
A aplicação é modularizada em **apps**, cada uma representando uma entidade de domínio (ex.: `users`, `favorites`, `clothes`, etc.).



## 🚀 Stack Tecnológica

- **Backend:** Python 3.13+, Django 5.x, Django REST Framework (DRF)
- **Banco de Dados:** PostgreSQL (via Docker)
- **ORM e utilitários:** sqlparse
- **Configuração:** python-dotenv (.env)
- **Logs:** Loguru
- **Docker:** Docker Compose para subir PostgreSQL
- **Erros:** Classes customizadas de erros globais e HTTP
- **Autenticação:** JWT

---

## 📂 Estrutura do Projeto

```

ecommerce/
│── api/                # Configurações globais do Django
│   ├── settings.py         # Configurações do projeto
│   ├── urls.py             # Rotas globais
│   └── ...
│
│── users/                  # App de Usuários
│   ├── models.py           # Definição da tabela User
│   ├── contracts/          # Interfaces/Contratos
│   ├── infra/              # Implementações de repositórios (DB)
│   ├── services/           # Regras de negócio (UserService)
│   ├── views.py            # Controllers (cadastro, login, etc.)
│   └── serializers.py      # Serialização/validação DRF
│
│── favorites/              # App para itens favoritos
│── clothes/                # App para roupas/itens do e-commerce
│── cart/                   # App para carrinho de compras
│
│── helpers/                   # Código compartilhado
│   ├── errors/             # Erros globais e HTTP customizados
│   ├── loggers/            # Configuração do Loguru
│   ├── helpers/            # Middlewares, utilitários
│   └── 
│
│── manage.py
│── requirements.txt
│── docker-compose.yml
│── .env
└── README.md

````

---

## ⚙️ Instalação e Setup

### 1. Clone o repositório
```bash
git clone https://github.com/seu-repositorio/ecommerce-api.git
cd ecommerce-api
````

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\Activate.ps1      # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=
DJANGO_DEBUG=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_PORT=
POSTGRES_HOST=
ENGINE=
DJANGO_ALLOWED_HOSTS=

EMAIL_BACKEND=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_USE_SSL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

### 5. Suba o banco com Docker

```bash
docker-compose up -d
```

### 6. Rode as migrações e servidor

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🛠️ Principais Apps

### 👤 Users

* Cadastro de usuário
* Login / Logout (futuro com JWT)
* Atualizar dados
* Atualizar senha
* Recuperação de conta
* Confirmação de conta
* Deletar usuário
* Listar todos ou um usuário específico

### ⭐ Favorites

* Adicionar item aos favoritos
* Remover item dos favoritos
* Listar favoritos do usuário

### 👕 Clothes

* Listar roupas/itens disponíveis
* Pesquisa e filtragem
* Detalhes de item

### 🛒 Cart

* Adicionar item ao carrinho
* Remover item do carrinho
* Listar itens do carrinho
* Finalizar compra (checkout)

---

## 🔒 Segurança

* Uso de **serializers DRF** para validação
* **Erros customizados** para não expor detalhes internos
* Proteção contra **SQL Injection** (ORM do Django + validações)
* **Logs estruturados** via Loguru
* Futuro: JWT Authentication + Refresh Token

## 📜 Logs

* Configurados via **Loguru** (`helpers/loggers/logger.py`)
* Logs de erro, info e debug com formatação JSON
* Integração futura com observabilidade (ex.: ELK, Grafana, Sentry)

---

## 🧩 Arquitetura e Princípios

* **SOLID:**

  * **S**: cada classe com uma única responsabilidade
  * **O**: services e repositórios fáceis de estender
  * **L**: contratos/abstrações para repositórios
  * **I**: interfaces específicas (contracts)
  * **D**: serviços dependem de abstrações, não de implementações

* **Architecture:**

  * `services/` → regras de negócio
  * `infra/` → implementação concreta (DB, repositórios)
  * `domain/entities/` → entidades
  * `domain/contracts/` → interfaces (contratos)
  * `views/` → camada de entrega (controllers REST)
  * `helpers/errors` → exceções globais
  * `helpers/loggers` → logging

---

## ✅ Próximos Passos

* [ ] Autenticação com JWT
* [ ] Implementar `favorites`, `clothes`, `cart`
* [ ] Testes unitários
* [ ] CI/CD (GitHub Actions)
* [ ] Documentação com Swagger / DRF Spectacular

---

## 📝 Licença

Este projeto foi criado por Romeu Cajamba.
