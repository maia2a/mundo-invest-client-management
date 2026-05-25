# 🏦 Mundo Invest — Client Management API

API backend autônoma que simula o sistema interno do Mundo Invest para **cadastro de clientes** e **integração com Pipefy via GraphQL**. Construída para o teste técnico "Client Management & Pipefy Integration".

> ⚠️ **A aplicação NUNCA se conecta ao Pipefy real.** As mutations GraphQL (`createCard`, `updateCardField`) são montadas seguindo a estrutura oficial da API do Pipefy, persistidas localmente e retornadas no response — o que permite validar a aderência ao schema sem dependências externas.

---

## 📌 Sumário

1. [Descrição](#-descrição)
2. [Decisões Arquiteturais](#-decisões-arquiteturais)
3. [Por que FastAPI?](#-por-que-fastapi)
4. [Execução Local](#-execução-local)
5. [Execução com Docker (PostgreSQL)](#-execução-com-docker-postgresql)
6. [Testes](#-testes)
7. [Exemplos curl](#-exemplos-curl)
8. [Onde estão as mutations do Pipefy?](#-onde-estão-as-mutations-do-pipefy)
9. [Idempotência do webhook](#-idempotência-do-webhook)
10. [Regra de prioridade](#-regra-de-prioridade)
11. [Visão de produção na AWS](#-visão-de-produção-na-aws)

---

## 🎯 Descrição

A API expõe dois fluxos principais:

- **`POST /clientes`** — cadastra um cliente, gera o payload da mutation `createCard` do Pipefy e persiste tudo localmente.
- **`POST /webhooks/pipefy/card-updated`** — simula o webhook recebido quando um card é atualizado no Pipefy, calcula prioridade com base no patrimônio, atualiza o cliente e gera a mutation `updateCardField`.

Endpoints adicionais: `GET /health` e Swagger em `/docs`.

---

## 🏛️ Decisões Arquiteturais

A aplicação segue uma variação enxuta de **Clean Architecture**, com camadas bem delimitadas:

```
src/
├── api/routes/        ← Apenas orquestração HTTP (sem regra de negócio)
├── domain/            ← Regra de negócio pura
│   ├── clients/       ← Entidade, service, repository, schemas
│   └── webhooks/      ← Entidade, service, repository, schemas
├── integrations/
│   └── pipefy/        ← Camada isolada para a integração externa
├── database/          ← Configuração de engine e sessão
├── shared/            ← Logging, erros e respostas padronizadas
└── config.py          ← Settings via pydantic-settings
```

**Por quê?**

- **Separação de responsabilidades**: cada camada tem uma única razão para mudar.
- **Testabilidade**: services dependem de repositórios injetados, permitindo mocks triviais.
- **Swappability**: trocar SQLite por PostgreSQL ou Pipefy mockado por Pipefy real exige mudanças apenas na camada de integração/infra.
- **Clareza na defesa técnica**: em 2 minutos é possível mostrar onde está cada parte do fluxo.

---

## ⚡ Por que FastAPI?

- Tipagem com Pydantic v2 nativa → validação automática dos payloads de entrada.
- OpenAPI/Swagger gerado automaticamente (`/docs`).
- Dependency Injection simplificada para `Session` do SQLAlchemy.
- Alto desempenho assíncrono quando necessário.
- Comunidade ativa e ecossistema maduro para APIs REST modernas.

---

## 💻 Execução Local

### Requisitos

- Python 3.12+
- pip

### Passos (macOS / Linux / WSL)

```bash
# Clonar
git clone https://github.com/maia2a/mundo-invest-client-management.git
cd mundo-invest-client-management

# Virtual env
python -m venv .venv
source .venv/bin/activate        # bash/zsh
# source .venv/bin/activate.fish # fish shell

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
cp .env.example .env

# Rodar
uvicorn src.main:app --reload
```

Aplicação disponível em: http://localhost:8000
Swagger: http://localhost:8000/docs

---

## 🐳 Execução com Docker (PostgreSQL)

```bash
cp .env.example .env
docker compose up --build
```

A API sobe conectada a um PostgreSQL 16 em `localhost:5432`.

---

## 🧪 Testes

A suite possui **~20 casos** cobrindo fluxo feliz, validações, idempotência e regras de prioridade.

```bash
# Executar toda a suíte
pytest -v

# Com cobertura
pytest --cov=src --cov-report=term-missing

# Filtro específico
pytest tests/test_webhook_idempotency.py -v
```

### Cobertura

| Suite | O que testa |
|---|---|
| `test_create_client.py` | Criação de cliente, validação de email, duplicidade, campos obrigatórios |
| `test_process_webhook.py` | Prioridade alta/normal, boundary 200k, cliente inexistente |
| `test_webhook_idempotency.py` | 409 em `event_id` duplicado, independência entre eventos distintos |
| `test_pipefy_mutations.py` | Estrutura das queries GraphQL e montagem de payloads |

---

## 🔌 Exemplos curl

### 1) Criar cliente

```bash
curl -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

### 2) Webhook `card-updated` (prioridade alta)

```bash
curl -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

### 3) Health

```bash
curl http://localhost:8000/health
```

---

## 🔍 Onde estão as mutations do Pipefy?

| Arquivo | Conteúdo |
|---|---|
| `src/integrations/pipefy/mutations.py` | **Queries GraphQL cruas** (`createCard`, `updateCardField`, `updateFieldsValues`) seguindo o schema oficial |
| `src/integrations/pipefy/pipefy_client.py` | **Montagem dos payloads** (variables) — método `build_create_card_payload`, `build_update_card_field_payload`, `build_update_fields_values_payload` |
| `src/integrations/pipefy/schemas.py` | Modelos Pydantic dos inputs do GraphQL |

> As mutations seguem o contrato oficial do Pipefy: `CreateCardInput`, `UpdateCardFieldInput` e `UpdateFieldsValuesInput` com os campos `card_id`, `field_id`, `new_value`, `pipe_id`, `title`, `fields_attributes`.

---

## 🔁 Idempotência do webhook

Implementada em duas camadas complementares:

1. **Constraint única** em `webhook_events.event_id` (no SQLAlchemy: `unique=True`).
2. **Checagem explícita** no `WebhookService.process_card_updated` antes de executar qualquer mutação.

Caso o mesmo `event_id` seja recebido novamente:

```http
HTTP/1.1 409 Conflict
{"detail": "Webhook event already processed"}
```

Nenhum efeito colateral: o cliente não é re-atualizado e o evento não é duplicado.

---

## 📊 Regra de prioridade

Calculada em `WebhookService._compute_prioridade`:

| `valor_patrimonio` | `prioridade` |
|---|---|
| `>= 200.000` | `prioridade_alta` |
| `< 200.000` | `prioridade_normal` |

O valor é armazenado no cliente e enviado ao Pipefy via mutation `updateCardField` no campo `prioridade`.

---

## ☁️ Visão de produção na AWS

Para subir o mesmo fluxo em produção, o desenho recomendado é:

```
Cliente HTTP
     │
     ▼
┌──────────────────┐
│   API Gateway    │  ← throttle, validação básica, OpenAPI
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────┐
│ ECS Fargate (FastAPI) ou Lambda    │
│   - /clientes      (sync)          │
│   - /webhooks      (fast ack)      │
└──────┬─────────────────┬───────────┘
       │                 │
       ▼                 ▼
┌────────────┐    ┌──────────────────────┐
│ RDS PgSQL  │◄───┤ SQS (fila de eventos)│  ← DLQ anexada
└────────────┘    └──────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Pipefy real     │  ← token em Secrets Manager
                 └─────────────────┘

Observabilidade: CloudWatch Logs + Metrics
Segurança: IAM least privilege + VPC + Secrets Manager para PIPEFY_AUTH_TOKEN
```

**Por que essa arquitetura?**

- **SQS + DLQ** absorve picos de webhook e garante retry com backoff — a idempotência por `event_id` já funciona perfeitamente com re-entregas.
- **RDS (ou Aurora)** escala muito melhor que SQLite; migração trivial pois já uso SQLAlchemy.
- **Secrets Manager** rotaciona tokens sem redeploy.
- **API Gateway** fornece throttling e WAF.


## 📄 Licença

MIT — sinta-se livre para usar como base.