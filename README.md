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
- Upload em partes, processamento em segundo plano e liberação progressiva do disco.
- Persistência de cada parte confirmada e retomada segura após interrupção.
- Scripts `.bat` para instalação, configuração e inicialização no Windows.
- Docker disponível para ambientes Linux com rede do host.

## Arquitetura

```text
Cliente FTP
    │
    ▼
Nebula Local ─────► staging/
    │                  │
    │                  ▼  parte confirmada
    │             trabalhadores de upload ──► libera espaço local
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

Para clonar o repositório:

1. Pressione `Windows + R`.
2. Digite `cmd` e pressione `Enter` para abrir o Prompt de Comando.
3. Copie as duas linhas abaixo.
4. Clique com o botão direito dentro da janela do CMD para colar.
5. Pressione `Enter` e aguarde o download terminar.

```bat
git clone https://github.com/jeffbart/NebulaLocal.git
cd NebulaLocal
```

A segunda linha entra na pasta que acabou de ser baixada. Depois disso, abra essa pasta no Explorador de Arquivos para executar os arquivos `.bat` das próximas etapas.

Na pasta `NebulaLocal`, execute os arquivos abaixo nesta ordem. Para executar cada um, dê dois cliques no arquivo, siga as mensagens mostradas na janela e aguarde a conclusão antes de abrir o próximo:

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

## Acesso remoto com Tailscale

Para acessar o FTP fora da rede local, use o Tailscale diretamente entre o computador do Nebula e o dispositivo cliente. Não encaminhe a porta 2121 no roteador e não publique o FTP com Tailscale Funnel.

1. [Instale o Tailscale no Windows](https://tailscale.com/docs/install/windows) do Nebula e entre em sua tailnet.
2. Instale o Tailscale no computador remoto e use a mesma tailnet autorizada.
3. Mantenha `HOST=0.0.0.0` e `PORT=2121` no `.env`.
4. Descubra o endereço do servidor com `tailscale ip -4` ou use seu nome [MagicDNS](https://tailscale.com/docs/features/magicdns).
5. No WinSCP ou FileZilla remoto, informe esse IP/nome, porta `2121`, FTP simples e modo passivo.

O túnel do Tailscale protege o tráfego entre os dispositivos, mas o login e a senha do próprio FTP continuam obrigatórios. Consulte a [configuração detalhada](docs/INSTALLATION.md#acesso-remoto-com-tailscale) e o [guia de uso remoto](docs/USAGE.md#acessar-remotamente-com-tailscale).

## Unidade FTPLOCAL opcional

No Windows, o FTP também pode ser apresentado como a unidade `S:` com o nome `FTPLOCAL`, permitindo usar o Explorador de Arquivos e outros programas locais. Essa opção usa os scripts da pasta `rclone` e não substitui o servidor Nebula, que deve permanecer em execução.

1. Caso o WinFsp ainda não esteja instalado, execute `rclone\winfsp-2.0.23075.msi`. Ele é pré-requisito para o rclone montar uma unidade no Windows.
2. Confirme que `rclone.exe` está dentro da pasta `rclone`.
3. Execute `rclone\01_Rclone config.bat` e crie um remoto FTP chamado `FTPLOCAL`, apontando para `127.0.0.1:2121`.
4. Inicie o Nebula e execute `rclone\02_mount_FTPLOCAL.bat` sem elevar como administrador.

Consulte as instruções completas em [docs/INSTALLATION.md](docs/INSTALLATION.md#unidade-ftplocal-opcional) e [docs/USAGE.md](docs/USAGE.md#usar-como-unidade-do-windows-opcional).

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
MIN_FREE_DISK_GB=20
LOG_LEVEL=INFO
```

`MIN_FREE_DISK_GB` define a reserva mínima do disco que contém `staging/`. Quando o espaço livre fica abaixo desse valor, o Nebula pausa a entrada de dados pelo FTP. Os uploads já enfileirados continuam sendo enviados ao Telegram e liberam espaço progressivamente; ao recuperar a reserva, o recebimento FTP é retomado automaticamente.

## Comandos do bot

Envie estes comandos ao bot do Nebula no Telegram:

- `/queue` — mostra uploads em processamento, aguardando e com falha;
- `/fetch` — envia o relatório completo dos uploads com falha;
- `/clearfailed` — mostra o aviso antes da limpeza;
- `/clearfailed confirmar` — remove todos os uploads com falha e seus arquivos temporários locais;
- `/help` — mostra as instruções dos comandos.

Uploads são divididos e enviados fisicamente do fim para o início, permitindo liberar o disco progressivamente. A numeração exibida na legenda, porém, segue a ordem de envio: a primeira mensagem aparece como `Parte: 01 de NN` e a contagem cresce até `NN de NN`.

Exemplo de legenda:

```text
Worker: W2
Pasta: /Filmes/1960S/
Arquivo: After.the.Fox.1966.1080p.AMZN.WEB-DL.DDP2.0.H.264-GPRS.mkv
Parte: 102 de 117
Enviado: 6.37 GB de 7.31 GB (87.2%)
```

Quando o arquivo é concluído, a legenda da última parte recebe `✅ UPLOAD CONCLUÍDO`, os horários de início e término e a duração total em minutos. O bot também responde à última parte com uma mensagem contendo somente `✅`, exibida pelo Telegram no estilo de emoji grande.

Nunca publique `.env`, tokens, `API_HASH`, arquivos `.session`, `nebula.db` ou logs. Esses itens já estão cobertos pelo `.gitignore`.

## Dados importantes

| Caminho | Finalidade |
|---|---|
| `data/nebula.db` | Usuários, permissões e metadados |
| `staging/` | Arquivos temporários; o espaço é liberado progressivamente durante o upload |
| `Nebula_MonoBot.session` | Sessão do Pyrogram |
| `.env` | Credenciais e configurações |
| `nebula.log` | Registro de execução |
| `05_VERIFICAR_ACERVO.bat` | Gera a árvore do acervo SQLite em `logs/relatorio_acervo_AAAAMMDD_HHMMSS.txt` |

Faça backup de `data/nebula.db` e preserve o canal do Telegram. Sem o banco, o Nebula perde a relação entre os nomes virtuais e os documentos armazenados.

> **Atenção:** os metadados, contas, permissões e credenciais do Nebula são armazenados localmente. Se o computador for formatado ou o disco falhar sem backup, o conteúdo do canal pode continuar no Telegram, mas o Nebula pode perder a relação necessária para listar e baixar os arquivos. Antes de formatar, trocar de computador ou fazer manutenção, siga o procedimento de [backup e restauração](docs/USAGE.md#backup-e-restauração).

## Segurança e limitações

- FTP simples não criptografa usuário, senha ou conteúdo em trânsito. Use-o apenas no computador local ou em uma rede confiável.
- Para acesso pela internet, prefira VPN; não exponha diretamente a porta FTP.
- O Telegram é um serviço externo sujeito a limites, disponibilidade e termos próprios.
- Não trate esta solução como cópia única de arquivos importantes.
- Mantenha uma cópia recente dos dados locais em outro disco, computador ou serviço de backup.
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
