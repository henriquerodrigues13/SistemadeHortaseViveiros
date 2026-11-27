# Gestão de Hortas e Viveiros Comunitários

Projeto Integrado I – FASI/UFPA Cametá. O backend usa **FastAPI** com banco **SQLite**, roda direto com Python (sem Docker) e tem dependências e configurações centralizadas no **`pyproject.toml`**. O front fica na pasta `frontend/`, e a equipe de front decide a arquitetura dele (ver `docs/FRONTEND.md`).

## Estrutura de pastas

```
hortas-viveiros/
├── .gitignore                  # inclui .venv/, .env e backend/data/*.db
├── docs/
│   └── FRONTEND.md             # decisões e contrato para a equipe de front
├── frontend/                   # a equipe de front define o conteúdo
└── backend/
    ├── pyproject.toml          # dependências, versão do Python e config. de ferramentas
    ├── .env.example            # variáveis de ambiente (copiar para .env)
    ├── data/                   # arquivo do banco (hortas.db), fora do Git
    ├── app/
    │   ├── main.py             # cria o FastAPI, registra os routers em /api/v1 e liga o agendador
    │   ├── scheduler.py        # APScheduler: e-mail diário e reenvios
    │   ├── core/               # o que todos os módulos usam
    │   │   ├── config.py       # leitura do .env
    │   │   ├── database.py     # conexão com o SQLite e sessão
    │   │   ├── security.py     # hash de senha e token JWT
    │   │   ├── deps.py         # usuário logado e checagem de perfil
    │   │   └── exceptions.py   # erros padrão da API
    │   └── modules/            # um módulo por assunto
    │       ├── auth/           # login e cadastro de administrador
    │       ├── usuarios/       # responsáveis e administradores
    │       ├── especies/       # catálogo global de espécies
    │       ├── hortas/         # hortas e viveiros + regra de acesso
    │       ├── plantios/       # plantio, irrigação e cronograma
    │       │   └── regras.py   # cálculos: colheita prevista, datas de irrigação, atraso
    │       ├── colheitas/
    │       ├── alertas/
    │       ├── viveiro/        # lotes de mudas e doações
    │       ├── educacao/       # ficha da espécie e conteúdo educativo
    │       ├── auditoria/      # registro de quem fez o quê
    │       └── notificacoes/   # resumo diário por e-mail
    │           └── email.py    # envio por SMTP ou no terminal (modo console)
    └── tests/                  # uma pasta de testes por módulo
```

Cada módulo segue o mesmo padrão de três arquivos:

| Arquivo | Papel |
|---|---|
| `router.py` | Rotas (endpoints) do módulo. Só recebe a requisição, chama o service e devolve a resposta. |
| `schemas.py` | Formato dos dados de entrada e saída (Pydantic) e os enums. |
| `service.py` | Regras de negócio. É aqui que os RFs são implementados. |

Os modelos e as migrações do banco ficam a cargo da equipe de modelagem de dados. Quando estiverem prontos, cada módulo ganha um `models.py` e a raiz do backend ganha a pasta `alembic/`.

## O `pyproject.toml`

O projeto não usa `requirements.txt`: tudo fica no `backend/pyproject.toml`.

| Seção | O que guarda |
|---|---|
| `[project]` | Nome, versão, **Python 3.12** (`requires-python`) e as dependências da aplicação: FastAPI, Uvicorn, SQLAlchemy, Pydantic Settings, PyJWT, pwdlib (hash de senha) e APScheduler. |
| `[project.optional-dependencies]` | Grupo `dev`: pytest, httpx (cliente de teste) e ruff. |
| `[tool.pytest.ini_options]` | Pasta de testes e configurações do pytest. |
| `[tool.ruff]` | Regras de estilo e formatação, iguais para toda a equipe. |

Para adicionar uma biblioteca, coloque-a na lista certa do `pyproject.toml` e rode de novo a instalação. Não instale nada solto com `pip install <pacote>`, senão o colega não vai ter a mesma biblioteca.

## Como rodar

Pré-requisito: **Python 3.12**.

1. Entrar na pasta do backend: `cd backend`
2. Criar o ambiente virtual: `python -m venv .venv`
3. Ativar o ambiente:
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
4. Instalar o projeto com as ferramentas de desenvolvimento: `pip install -e ".[dev]"`
5. Copiar `.env.example` para `.env` e ajustar se precisar.
6. Subir a API: `uvicorn app.main:app --reload`
7. Abrir a documentação interativa: `http://localhost:8000/docs`

Outros comandos:

| Para quê | Comando |
|---|---|
| Rodar os testes | `pytest` |
| Checar o estilo | `ruff check .` |
| Formatar o código | `ruff format .` |

### E-mail em desenvolvimento

Com `EMAIL_MODO=console` no `.env` (padrão em desenvolvimento), o resumo diário (RF21) é escrito no terminal em vez de enviado. Em produção, usar `EMAIL_MODO=smtp` e preencher os dados do servidor de e-mail.

## Onde fica cada requisito

| Frente | Requisitos | Módulos |
|---|---|---|
| 1. Cadastros e acesso | RF01, RF07, RF08, RNF03, RNF04 | `especies` |
| | RF02, RNF04 | `hortas` |
| | RF03, RF04, RF05, RNF01, RNF12 | `auth`, `usuarios`, `core/security.py` |
| | RF06 | `core/deps.py` |
| 2. Plantio e irrigação | RF09, RF10, RF13, RF15, RNF08 | `plantios` (`regras.py` + `service.py`) |
| | RF11, RF12, RF14, RNF05, RNF07 | `plantios` |
| | RNF06 | `auditoria` |
| 3. Alertas e colheita | RF16, RF17, RNF10 | `alertas` |
| | RF18, RF19, RF20 | `colheitas` |
| | RF21, RNF09 | `notificacoes` + `scheduler.py` |
| 4. Viveiro e educação | RF22, RF23, RF24, RNF11 | `viveiro` |
| | RF25 | `educacao` |

## Decisões já tomadas

- **Banco:** SQLite, num arquivo só (`backend/data/hortas.db`). Se o projeto crescer, a troca para PostgreSQL muda só a URL de conexão no `.env`, porque o acesso é feito pelo SQLAlchemy.
- **Sem Docker:** o projeto roda direto com Python e um ambiente virtual, para ninguém da equipe travar na instalação.
- **Dependências:** tudo no `pyproject.toml`, sem `requirements.txt`.
- **Agendador dentro da API:** o APScheduler roda no mesmo processo da API, então só um processo escreve no arquivo do banco.
- **Espécies:** catálogo global único. O nome popular não se repete no sistema inteiro (RF07).
- **Responsável × horta:** cada responsável atua em uma horta, e uma horta pode ter vários responsáveis.
- **Irrigação (RF10):** a espécie tem um campo numérico `intervalo_irrigacao_dias`. As irrigações são geradas do dia do plantio até a colheita prevista, nesse intervalo.
- **Acesso por horta:** o Hoot acessa todas as hortas, o administrador só as dele e o responsável só a sua.
- **Rotas:** todas sob o prefixo `/api/v1`. A documentação automática fica em `/docs`.

## Cuidados com o SQLite

- **Chaves estrangeiras:** o SQLite só respeita chaves estrangeiras com `PRAGMA foreign_keys=ON`. Esse comando é ligado em toda conexão, no `core/database.py`. É ele que garante, por exemplo, o RNF04 (não excluir espécie ou horta com plantio vinculado).
- **Busca de espécies (RF08):** o `LIKE` do SQLite não ignora acentos. Para "alface" achar "Alfacê", guardar também uma coluna com o nome normalizado (sem acento e em minúsculas) e buscar nela.
- **Datas:** o SQLite guarda datas como texto. Os cálculos de data ficam no Python (`plantios/regras.py`), não no SQL.

## Pendências

### Do documento de requisitos (seção 7)
- [ ] Validar o estado atual e as limitações L1 a L10 com uma horta ou um viveiro real.
- [ ] Confirmar os valores numéricos dos RNFs, que são estimativas da equipe: tempo de resposta de 3 s (RNF03, RNF05), alerta com 1 dia de antecedência (RF16) e reenvio do e-mail a cada 15 min, até 3 vezes (RNF09). Esses valores ficam no `.env` para poderem mudar sem alterar código.

### Modelagem de dados
- [ ] Criar os modelos (`models.py` de cada módulo) e as migrações com Alembic.
- [ ] Definir o campo "responsável" da horta (RF02): como os responsáveis são cadastrados depois da horta (RF04), confirmar se a horta só lista os responsáveis ligados a ela.
- [ ] Definir as listas fixas (enums): tipos de espécie, necessidade de água e de luz, unidades e destinos da colheita.
- [ ] Definir o formato do conteúdo educativo (RF25): só texto ou também links e imagens.

### Backend
- [ ] Implementar os services de cada módulo (os RFs da tabela acima).
- [ ] Criar a conta do Administrador Hoot automaticamente na primeira execução, com os dados do `.env`.
- [ ] Escolher o servidor de e-mail de produção para o RF21.
- [ ] Escrever os testes de cada regra de negócio.

### Integração com o front
- [ ] Combinar o formato padrão das respostas de erro, com o nome do campo inválido (RNF08).
- [ ] Informar ao backend a porta do front em desenvolvimento, para liberar o CORS.
- [ ] Preencher as decisões técnicas em `docs/FRONTEND.md`.

### Entrega
- [ ] Definir onde o sistema será publicado para a apresentação.
- [ ] Revisar o tratamento de dados pessoais conforme a LGPD (RNF12).
