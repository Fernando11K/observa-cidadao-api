# Observa Cidadão API

API GraphQL do **Observa Cidadão**. Ela reúne dados públicos do **Senado Federal** e do **Tribunal de Contas da União (TCU)** sobre os senadores em exercício e guarda os usuários e os senadores que cada um acompanha.

O componente principal (front-end) está em [vue-observa-cidadao](https://github.com/Fernando11K/vue-observa-cidadao). O `docker-compose.yml` que sobe os dois projetos juntos, e o diagrama de arquitetura, ficam naquele repositório.

## Tecnologias

- Python 3.13 e [uv](https://docs.astral.sh/uv/)
- [FastAPI](https://fastapi.tiangolo.com/) + [Strawberry GraphQL](https://strawberry.rocks/)
- SQLAlchemy assíncrono + SQLite (`aiosqlite`)
- JWT (`pyjwt`) e senhas com Argon2 (`pwdlib`)
- `httpx` para consumir os serviços externos

## Como executar

### Com Docker

```bash
docker build -t observa-cidadao-api .
docker run -d --name observa-api -p 8000:8000 -v dados-api:/app/data observa-cidadao-api
```

A API fica em <http://localhost:8000/graphql>. O volume `dados-api` mantém o banco SQLite quando o container é recriado.

Para subir junto com o front, use o `docker compose` do repositório [vue-observa-cidadao](https://github.com/Fernando11K/vue-observa-cidadao#como-executar).

### Localmente

Pré-requisitos: Python 3.13 e [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync
uv run fastapi dev
```

A API sobe em <http://localhost:8000>. O banco é criado automaticamente em `data/observa_cidadao.db` na primeira execução.

Sem o uv, também funciona com `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev src/observa_cidadao_api/main.py
```

## Documentação da API

Abrindo <http://localhost:8000/graphql> no navegador aparece o **GraphiQL**, que documenta todas as operações, campos e argumentos (botão "Docs") e permite testá-las.

Todas as operações usam o endereço `/graphql`. Consultas (queries) podem ser enviadas por GET ou POST. Alterações (mutations) são enviadas por POST.

| Método REST equivalente | Operação | Autenticação | Descrição |
|---|---|---|---|
| GET | `senadores(uf, partido)` | não | senadores em exercício, em ordem alfabética |
| GET | `senador(codigo)` | não | detalhe, mandatos e dados do TCU de um senador |
| GET | `eu` | sim | usuário autenticado |
| GET | `acompanhamentos` | sim | senadores acompanhados pelo usuário |
| POST | `cadastrarUsuario(nome, email, senha)` | não | cria a conta e devolve o token |
| POST | `login(email, senha)` | não | devolve o token |
| POST | `acompanharSenador(codigoSenador, anotacao)` | sim | passa a acompanhar um senador |
| PUT | `atualizarAcompanhamento(id, anotacao)` | sim | altera a anotação |
| DELETE | `removerAcompanhamento(id)` | sim | deixa de acompanhar |

As operações autenticadas exigem o cabeçalho:

```
Authorization: Bearer <token>
```

### Exemplos

Cadastro (a senha precisa ter de 8 a 128 caracteres):

```graphql
mutation {
  cadastrarUsuario(nome: "Maria", email: "maria@email.com", senha: "senha-segura") {
    token
    usuario { id nome email }
  }
}
```

Login:

```graphql
mutation {
  login(email: "maria@email.com", senha: "senha-segura") {
    token
  }
}
```

Senadores do DF:

```graphql
{
  senadores(uf: "DF") {
    codigo
    nomeParlamentar
    partido
    uf
    fimMandato
  }
}
```

Perfil de um senador, com mandatos e dados do TCU:

```graphql
{
  senador(codigo: 6335) {
    nome
    partidoAtual
    idade
    mandatos { participacao legislaturas { numero dataInicio dataFim } }
    solicitacoesTcu { tipo numero assunto dataAprovacao }
    contasIrregularesTcu { processo acordao dataTransitoEmJulgado }
  }
}
```

Acompanhar, editar e remover (com o token no cabeçalho):

```graphql
mutation { acompanharSenador(codigoSenador: 6335, anotacao: "Acompanhar votações") { id } }
mutation { atualizarAcompanhamento(id: 1, anotacao: "Nova anotação") { id anotacao } }
mutation { removerAcompanhamento(id: 1) }
```

Com `curl`:

```bash
curl -G http://localhost:8000/graphql --data-urlencode 'query={ senadores(uf: "DF") { nomeParlamentar partido } }'

curl http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ acompanhamentos { id codigoSenador anotacao } }"}'
```

Erros de validação (e-mail já cadastrado, senha curta, senador inexistente, acompanhamento duplicado ou não autenticado) voltam no campo `errors` da resposta GraphQL com uma mensagem em português.

## APIs externas

As três são públicas, gratuitas e não exigem cadastro nem chave de acesso.

### Senado Federal - Dados Abertos Legislativos

- **Documentação:** <https://legis.senado.leg.br/dadosabertos/api-docs/swagger-ui/index.html>
- **Licença:** dados abertos de livre utilização, exigindo no máximo a citação da fonte ([Sobre Dados Abertos do Senado](https://www12.senado.leg.br/dados-abertos/sobre)).

| Método | Rota | Uso |
|---|---|---|
| GET | `https://legis.senado.leg.br/dadosabertos/senador/lista/atual?v=4` | senadores em exercício |
| GET | `https://legis.senado.leg.br/dadosabertos/senador/{codigo}?v=6` | detalhe do senador |
| GET | `https://legis.senado.leg.br/dadosabertos/senador/{codigo}/mandatos?v=5` | mandatos do senador |

### TCU - Webservices públicos

- **Documentação:** <https://sites.tcu.gov.br/dados-abertos/webservices-tcu/>
- **Licença:** conteúdo público que pode ser republicado citando a fonte, sem uso comercial ([Termos de Uso do Portal TCU](https://portal.tcu.gov.br/sobre-o-portal/termos-de-uso)).

| Método | Rota | Uso |
|---|---|---|
| GET | `https://contas.tcu.gov.br/ords/api/publica/scn/pedidos_congresso` | solicitações do Congresso ao TCU; a API percorre as páginas e filtra pelo nome parlamentar do autor |
| POST | `https://certidoes.apps.tcu.gov.br/api/publico/responsaveis-contas-irregulares` | responsáveis com contas julgadas irregulares; só são mantidos os registros com nome completo idêntico |

A correspondência com o TCU é feita pelo nome, porque os serviços públicos não expõem o CPF dos senadores. Por isso podem aparecer homônimos, o que é informado na descrição dos campos.

### Cache

As respostas do Senado e do TCU ficam em memória por 12 horas. Isso deixa a navegação rápida e evita sobrecarregar os serviços públicos. Se um serviço externo estiver fora do ar, o campo correspondente volta como `null` e o restante da resposta continua funcionando.

## Configuração

As variáveis são lidas do arquivo `.env` (ou do ambiente):

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | gerada a cada execução | chave de assinatura dos tokens JWT |
| `TOKEN_EXPIRA_EM_MINUTOS` | `60` | validade do token |
| `CORS_ORIGINS` | `["http://localhost:9000","http://localhost:8080"]` | origens liberadas para o front |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/observa_cidadao.db` | banco de dados |

O `.env` está versionado de propósito, para facilitar a execução do projeto acadêmico. Em produção a `SECRET_KEY` deve ficar fora do repositório.

## Banco de dados

| Tabela | Campos |
|---|---|
| `usuarios` | `id`, `nome`, `email` (único), `senha_hash`, `criado_em` |
| `acompanhamentos` | `id`, `usuario_id`, `codigo_senador`, `anotacao` (até 1000 caracteres), `criado_em`, `atualizado_em`; um usuário acompanha cada senador uma única vez |

As tabelas são criadas automaticamente quando a API inicia.

## Estrutura

```
src/observa_cidadao_api/
├── main.py           # aplicação FastAPI, CORS e rota /graphql
├── models.py         # tabelas usuarios e acompanhamentos
├── cache.py          # cache em memória das APIs externas
├── core/             # configuração, conexão com o banco e segurança (JWT, senhas)
├── graphql/          # schema, queries, mutations, permissões e tipos
├── services/         # regras de negócio de usuários e acompanhamentos
├── senado/           # cliente da API de Dados Abertos do Senado
└── tcu/              # clientes dos webservices do TCU
```

## Autor

Fernando Mendonça - [LinkedIn](https://br.linkedin.com/in/fernando11000)
