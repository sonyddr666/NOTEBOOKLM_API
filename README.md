# NotebookLM API & Telegram Bot (v1.1.0)

A comprehensive REST API and Telegram Bot for Google NotebookLM, built on top of [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli).

---

## 🚀 Novidades e Melhorias

- **Comando `/cookies`**: Autentique o bot enviando cookies JSON diretamente pelo Telegram. Chega de sofrer com `nlm login` no servidor!
- **Persistência Docker**: Volumes configurados para manter sua sessão Google ativa mesmo após reiniciar os containers.
- **Correções de Core**: Resolvidos problemas de importação em Pesquisas (`ResearchError`) e Notas (`NoteError`).
- **Configuração Robusta**: Validação de IDs de administradores no `.env` corrigida para suportar múltiplos formatos.

---

## 🛠️ Quick Start (Instalação Rápida)

### 1. Clone o Repositório
```bash
git clone https://github.com/sonyddr666/NOTEBOOKLM_API.git
cd NOTEBOOKLM_API
```

### 2. Configure o Ambiente
Copie o arquivo de exemplo e preencha suas chaves:
```bash
cp .env.example .env
```
Campos obrigatórios no `.env`:
- `TELEGRAM_BOT_TOKEN`: Token do @BotFather.
- `TELEGRAM_ADMIN_USERS`: Seu ID do Telegram (para usar o comando de cookies).
- `API_KEY`: Uma chave secreta para proteger sua API.

### 3. Rodar com Docker (Recomendado)
O Docker garante que todas as dependências (Python 3.11, Playwright, etc) estejam prontas.
```bash
docker-compose up -d --build
```

---

## 🔐 Como Autenticar (Sem Terminal)

Não precisa mais rodar comandos no terminal do servidor para logar no Google:

1. Acesse o [NotebookLM](https://notebooklm.google.com) no seu navegador.
2. Exporte os cookies usando a extensão **EditThisCookie** (formato JSON).
3. No Telegram, envie o comando `/cookies` para o seu bot.
4. **Envie o arquivo .json** que você exportou.
5. O bot salvará os cookies e validará a sessão automaticamente.
6. Use `/auth` para confirmar se está tudo ok.

---

## 🤖 Comandos do Telegram

| Comando | Descrição |
|---------|-------------|
| `/start` | Menu principal |
| `/auth` | Verifica status da conexão Google |
| `/cookies` | (Admin) Envia novos cookies via Telegram |
| `/notebooks` | Lista todos os seus cadernos |
| `/create <nome>` | Cria um novo caderno |
| `/chat <id>` | Inicia chat interativo com o caderno |
| `/audio <id>` | Gera resumo em áudio (Podcast) |
| `/status <id>` | Verifica progresso de geração no Studio |

---

## 🌐 REST API

A API estará disponível em `http://localhost:8000`.
- **Swagger UI**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## 📁 Estrutura do Projeto

```
notebooklm-api/
├── src/
│   ├── api/              # FastAPI (Rotas e Schemas)
│   ├── bot/              # Telegram Bot (Handlers e Teclados)
│   └── core/             # Cliente Wrapper do NotebookLM
├── notebooklm-mcp-cli/   # Biblioteca base (submódulo)
├── docker-compose.yml    # Orquestração com volumes de persistência
└── .env                  # Suas chaves e configurações
```

## 📜 Créditos

- Baseado no [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) de Jacob Ben-David.
- Desenvolvido com **FastAPI** e **python-telegram-bot**.

## ⚖️ Licença

MIT License - Veja o arquivo LICENSE para detalhes.
