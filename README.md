<div align="center">

<img src="img/logo_nebula_ftp.png" alt="Nebula Local" width="280">

# Nebula Local

Servidor FTP local com armazenamento de arquivos em um canal privado do Telegram e metadados em SQLite.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-local-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Windows-suportado-0078D4?logo=windows)](#instalação-no-windows)

[Instalação](docs/INSTALLATION.md) · [Como usar](docs/USAGE.md) · [Telegram](docs/TELEGRAM_SETUP.md) · [Créditos](CREDITS.md)

</div>

## Sobre o projeto

O Nebula Local disponibiliza uma interface FTP para enviar e recuperar arquivos armazenados como documentos no Telegram. O envio chega primeiro à pasta local `staging` e é processado em segundo plano. Usuários, permissões, diretórios virtuais e referências das partes enviadas ficam no banco local `data/nebula.db`.

Esta edição é uma adaptação do [NebulaFTP original](https://github.com/samucamg/NebulaFTP), criado por [Samuel de Sousa Santos (`@samucamg`)](https://github.com/samucamg). Consulte [Créditos e agradecimentos](CREDITS.md).

## Principais recursos

- Servidor FTP acessível por FileZilla, WinSCP e clientes compatíveis.
- Arquivos armazenados em canal privado do Telegram.
- SQLite local, sem MongoDB ou servidor de banco externo.
- Contas FTP e permissões por diretório.
- Upload em partes e processamento em segundo plano.
- Persistência de metadados e recuperação após reinicialização.
- Scripts `.bat` para instalação, configuração e inicialização no Windows.
- Docker disponível para ambientes Linux com rede do host.

## Arquitetura

```text
Cliente FTP
    │
    ▼
Nebula Local ─────► staging/
    │                  │
    │                  ▼
    │             trabalhadores de upload
    │                  │
    ├── SQLite         └────► canal privado do Telegram
    │   usuários              partes dos arquivos
    │   permissões
    │   metadados
    │
    └── porta FTP 2121
```

## Requisitos

- Windows 10 ou 11.
- Python 3.10 ou superior disponível no `PATH`.
- Conta do Telegram.
- `API_ID` e `API_HASH` obtidos em [my.telegram.org](https://my.telegram.org).
- Bot criado no [@BotFather](https://t.me/BotFather).
- Canal privado com o bot adicionado como administrador.
- Cliente FTP, como FileZilla ou WinSCP.

## Instalação no Windows

Clone o repositório:

```powershell
git clone https://github.com/jeffbart/NebulaLocal.git
cd NebulaLocal
```

Depois execute, nesta ordem:

1. `00_INSTALAR_DEPENDENCIAS.bat`
2. `01_CONFIGURAR_TELEGRAM.bat`
3. `DESCOBRIR_CHAT_ID.bat`, caso ainda não saiba o ID do canal
4. `02_TESTAR_TELEGRAM.bat`
5. `03_CRIAR_BANCO_SQLITE.bat`
6. `04_GERENCIAR_USUARIOS_FTP.bat`
7. `INICIAR_NEBULA.bat`

O procedimento detalhado está em [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Início rápido

Após criar pelo menos um usuário FTP, execute:

```text
INICIAR_NEBULA.bat
```

Conecte o cliente FTP:

```text
Host: 127.0.0.1
Porta: 2121
Protocolo: FTP
Criptografia: FTP simples
Modo de transferência: Passivo
Usuário: conta criada no gerenciador
Senha: senha criada no gerenciador
```

Para instruções de envio, download, encerramento e solução de problemas, consulte [docs/USAGE.md](docs/USAGE.md).

## Configuração

O arquivo `.env` é criado pelo assistente e não deve ser publicado. As principais opções são:

```dotenv
API_ID=12345678
API_HASH=0123456789abcdef0123456789abcdef
BOT_TOKENS=1234567890:token_do_bot
CHAT_ID=-1001234567890

SQLITE_PATH=data/nebula.db
HOST=0.0.0.0
PORT=2121
PASSIVE_PORTS=60000-60100

MAX_WORKERS=4
CHUNK_SIZE_MB=64
MAX_RETRIES=5
MAX_STAGING_AGE=3600
LOG_LEVEL=INFO
```

Nunca publique `.env`, tokens, `API_HASH`, arquivos `.session`, `nebula.db` ou logs. Esses itens já estão cobertos pelo `.gitignore`.

## Dados importantes

| Caminho | Finalidade |
|---|---|
| `data/nebula.db` | Usuários, permissões e metadados |
| `staging/` | Arquivos temporários aguardando upload |
| `Nebula_MonoBot.session` | Sessão do Pyrogram |
| `.env` | Credenciais e configurações |
| `nebula.log` | Registro de execução |

Faça backup de `data/nebula.db` e preserve o canal do Telegram. Sem o banco, o Nebula perde a relação entre os nomes virtuais e os documentos armazenados.

## Segurança e limitações

- FTP simples não criptografa usuário, senha ou conteúdo em trânsito. Use-o apenas no computador local ou em uma rede confiável.
- Para acesso pela internet, prefira VPN; não exponha diretamente a porta FTP.
- O Telegram é um serviço externo sujeito a limites, disponibilidade e termos próprios.
- Não trate esta solução como cópia única de arquivos importantes.
- A senha FTP segue o comportamento do projeto original e é armazenada localmente. Proteja o arquivo SQLite e a conta do Windows.

## Desenvolvimento

Execute a suíte de testes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O schema é criado e atualizado por:

```powershell
.\.venv\Scripts\python.exe setup_database.py
```

## Contribuições

Issues e pull requests são bem-vindos. Antes de enviar uma alteração:

1. Não inclua credenciais, sessões, bancos ou arquivos de staging.
2. Execute todos os testes.
3. Explique o comportamento alterado.
4. Atualize a documentação quando necessário.

## Licença

Distribuído sob a [Licença MIT](LICENSE). Os avisos de autoria e licença do trabalho anterior devem ser preservados em cópias e trabalhos derivados.

## Agradecimentos

Obrigado a **Samuel de Sousa Santos (`@samucamg`)** por criar e compartilhar publicamente o NebulaFTP, que tornou esta adaptação possível. Agradecemos também a RuslanUC, cujo aviso de copyright consta na licença herdada, e aos mantenedores das bibliotecas de código aberto utilizadas pelo projeto.

Leia a atribuição completa em [CREDITS.md](CREDITS.md).
