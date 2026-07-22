# Agenda Médica

Aplicação web de **agenda médica** para o desafio técnico: login com usuário em SQLite, busca de agendamentos via HTTP em uma API simulada e exibição em tabela com Tabulator.

## Tecnologias

- Python 3.11+
- Flask
- SQLite (`sqlite3`)
- requests (cliente HTTP)
- Tabulator (tabela no front)
- Docker + Docker Compose
- pytest

## Como executar com Docker

Pré-requisito: Docker Desktop instalado e em execução.

Na raiz do projeto:

```bash
docker compose up --build
```

Isso sobe **dois serviços**:

| Serviço | URL |
|---------|-----|
| Site (`web`) | http://localhost:5000 |
| API mock (`mock_api`) | http://localhost:5001/agendamentos |

O entrypoint do `web` roda o `seed.py` automaticamente (cria o usuário de teste) e depois inicia o Flask.

Para parar:

```bash
docker compose down
```

## Credenciais de teste

| Campo | Valor |
|-------|--------|
| Usuário | `admin` |
| E-mail | `admin@example.com` |
| Senha | `admin123` |

No login, use **usuário ou e-mail** no mesmo campo + a senha.

(Valores também estão em `.env.example`.)

## Exemplos de uso

1. Abra http://localhost:5000  
2. Entre com `admin` / `admin123` ou o email `admin@example.com`  
3. Na agenda, a tabela carrega os agendamentos da API  
4. Use o campo de busca para filtrar por **paciente**, **CPF** ou **médico**  
5. Clique em **Limpar** para voltar à lista completa  
6. **Sair** encerra a sessão  

### Simular falhas da API

Com o Compose no ar:

```bash
# API fora do ar (ConnectionError real)
docker compose stop mock_api
# Atualize a agenda => mensagem de falha

# Ligar de novo
docker compose start mock_api
```

Outros modos (defina antes do `up` ou no `.env`):

```text
MOCK_MODE=empty      => lista vazia
MOCK_MODE=invalid    => JSON com formato errado
MOCK_MODE=malformed  => corpo que não é JSON
MOCK_MODE=slow       => demora maior que o timeout do client
```

Exemplo no PowerShell:

```powershell
$env:MOCK_MODE="empty"
docker compose up --build
```

### Executar sem Docker (opcional)

Dois terminais, com venv e `pip install -r requirements.txt`:

1. `cd mock_api` → `python run.py` (porta 5001)  
2. Na raiz → `python seed.py` → `python run.py` (porta 5000)

Testes:

```bash
pytest -v
```

## Decisões técnicas

- **Dois containers:** a web e a API mock ficam separadas; a comunicação é HTTP.
- **SQLite só para usuários;** agendamentos vem da API.
- **Sessão Flask nativa** (sem Flask-Login).
- **`sqlite3` puro** (sem ORM) + script `seed.py` na raiz.
- **Uma rota JSON** (`/api/agendamentos?q=`) na carga e na busca; `/agenda` só entrega o HTML.
- **Busca no servidor** (paciente, CPF ou médico). `q` vazio = lista completa (não é erro).
- Mensagens distintas: agenda vazia (`agenda_vazia`) vs busca sem match (`sem_resultado_busca`).
- Item da API com campo obrigatório ausente/`""` => **só aquele item** é descartado.

## Limitações conhecidas

- Não há cadastro de usuários nem CRUD de agendamentos.
- A API de agendamentos é simulada (dados fixos / modos de teste).

## Estrutura (visão geral)

```text
├── app/                 # site Flask
├── mock_api/            # API simulada
├── data/                # SQLite (volume)
├── seed.py
├── run.py
├── docker-compose.yml
├── Dockerfile
└── tests/
```
