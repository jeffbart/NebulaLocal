# Execução com Docker

O Docker é uma opção avançada, recomendada principalmente para Linux. Esta versão usa SQLite e não cria container MongoDB.

## Requisitos

- Docker Engine e Docker Compose;
- `.env` configurado;
- bot administrador do canal;
- portas FTP disponíveis.

## Preparar

```bash
cp .env.example .env
mkdir -p data staging
```

Preencha o `.env` antes de continuar.

## Construir e iniciar

```bash
docker compose up -d --build
docker compose logs -f app
```

Encerrar:

```bash
docker compose down
```

## Persistência

O compose monta `data`, `staging`, `.env`, `nebula.log` e a sessão do Pyrogram no diretório do projeto.

Faça backup de:

```text
.env
data/nebula.db
Nebula_MonoBot.session
```

## Criar usuário FTP

```bash
docker compose exec app python accounts_manager.py
```

Ou, antes de iniciar:

```bash
docker compose run --rm app python accounts_manager.py
```

## Rede

O compose usa `network_mode: host`, com melhor compatibilidade em Linux. O servidor utiliza a porta `PORT` e o intervalo `PASSIVE_PORTS` definidos no `.env`.

Não exponha FTP simples diretamente à internet. No Docker Desktop, a rede host pode se comportar de modo diferente; no Windows, prefira os scripts descritos em [INSTALLATION.md](INSTALLATION.md).

## Atualizar

```bash
docker compose down
git pull
docker compose up -d --build
```

## Problemas comuns

Se o banco não puder ser criado:

```bash
mkdir -p data
chmod u+rwX data
```

Se a porta estiver ocupada, altere `PORT` ou encerre o serviço conflitante. Para falhas no modo passivo, confira `PASSIVE_PORTS` e o firewall.
