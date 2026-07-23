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

A `mock_api` possui modos que facilitam a demonstração do tratamento de falhas. Os comandos abaixo devem ser executados no **PowerShell**, na raiz do projeto.

> Antes de mudar o `MOCK_MODE`, use `docker compose down`. Isso encerra os containers atuais e garante que o novo modo seja aplicado na próxima inicialização.

#### 1. API sem dados (lista vazia)

Encerre os containers, selecione o modo `empty` e inicie novamente:

```powershell
docker compose down
$env:MOCK_MODE="empty"
docker compose up --build
```

Depois:

1. Abra http://localhost:5000;
2. faça login;
3. acesse a agenda.

A API responderá com uma lista vazia (`[]`) e a página deverá mostrar:

```text
Não há agendamentos disponíveis.
```

Esse cenário representa uma API funcionando normalmente, mas sem agendamentos cadastrados.

#### 2. API com resposta inválida

O projeto possui dois modos diferentes para simular uma resposta inválida.

##### JSON válido, mas no formato errado

```powershell
docker compose down
$env:MOCK_MODE="invalid"
docker compose up --build
```

Nesse modo, a API devolve um objeto JSON quando a aplicação esperava uma lista.

##### Corpo que não é um JSON válido

```powershell
docker compose down
$env:MOCK_MODE="malformed"
docker compose up --build
```

Nesse modo, a API devolve um texto que não pode ser convertido para JSON.

Nos dois casos, depois de fazer login e abrir a agenda, deverá aparecer:

```text
Não foi possível carregar os agendamentos. Tente novamente.
```

#### 3. API lenta (timeout)

O modo `slow` faz a API demorar mais do que o tempo máximo configurado no cliente HTTP:

```powershell
docker compose down
$env:MOCK_MODE="slow"
docker compose up --build
```

Ao abrir ou atualizar a agenda, deverá aparecer:

```text
Não foi possível carregar os agendamentos. Tente novamente.
```

#### 4. API offline (fora do ar)

Primeiro, volte ao modo normal e inicie os dois serviços:

```powershell
docker compose down
$env:MOCK_MODE="ok"
docker compose up --build
```

Com o Compose ainda em execução, abra outro terminal na raiz do projeto e pare somente a API:

```powershell
docker compose stop mock_api
```

Depois, atualize a página da agenda com `F5` ou clique em **Buscar**. A aplicação web continuará no ar, mas não conseguirá se comunicar com a API. A página deverá mostrar:

```text
Não foi possível carregar os agendamentos. Tente novamente.
```

Para ligar a API novamente:

```powershell
docker compose start mock_api
```

Atualize a agenda e os dados deverão voltar a aparecer.

#### Voltar ao funcionamento normal

Ao terminar os testes de falha, execute:

```powershell
docker compose down
$env:MOCK_MODE="ok"
docker compose up --build
```

O valor definido com `$env:MOCK_MODE` vale para o terminal atual. Se abrir outro PowerShell, a variável precisará ser definida novamente ou será usado o valor presente no arquivo `.env`.

### Executar sem Docker (opcional)

Dois terminais, com venv e `pip install -r requirements.txt`:

1. `cd mock_api` → `python run.py` (porta 5001)  
2. Na raiz → `python seed.py` → `python run.py` (porta 5000)

### Executar os testes

Na raiz do projeto, crie e ative o ambiente virtual, instale as dependências e execute o Pytest:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -v
```

Resultado verificado:

```text
collected 7 items

tests/test_agendamentos.py::test_api_indisponivel_retorna_502 PASSED
tests/test_agendamentos.py::test_busca_sem_correspondencia PASSED
tests/test_agendamentos.py::test_sem_sessao_api_401 PASSED
tests/test_login.py::test_login_valido_redireciona PASSED
tests/test_login.py::test_login_valido_com_email PASSED
tests/test_login.py::test_login_invalido_permanece_200 PASSED
tests/test_seed.py::test_seed_cria_usuario PASSED

7 passed
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
