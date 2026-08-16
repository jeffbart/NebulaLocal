Exit code: 0
Wall time: 0.3 seconds
Output:
# Mapa mental do Nebula Local

Este mapa resume a arquitetura, os fluxos de dados, a operação e os principais arquivos do projeto.

```mermaid
mindmap
  root((Nebula Local))
    Objetivo
      Servidor FTP local
      Arquivos no Telegram
      Metadados no SQLite
      Acesso local ou por VPN
    Entrada FTP
      Clientes
        FileZilla
        WinSCP
        rclone como unidade S
      Servidor
        ftp/server.py
        pyftpdlib
        Porta 2121
        Portas passivas configuráveis
      Autenticação e permissões
        accounts_manager.py
        SQLiteUserStore
        Permissões por diretório
    Processamento
      main.py
        Orquestra serviços assíncronos
        Monitora espaço em disco
        Restaura uploads pendentes
        Coleta arquivos abandonados
        Produz métricas e logs
      staging
        Recebe arquivos temporários
        Preserva estrutura de pastas
        Libera espaço após upload
      Fila de uploads
        Estados
          staging
          uploading
          completed
          failed
        Vários workers
        Retentativas configuráveis
        Divisão em partes
    Telegram
      Pyrogram e TgCrypto
      Bot MonoBot
      Canal privado
      Arquivos enviados como documentos
      Legendas com metadados
      Comandos
        status
        queue
        resume
        retry
        clean
        help
    Persistência
      SQLite
        data/nebula.db
        database.py
        Migrações de schema
        Usuários
        Arquivos e diretórios virtuais
        IDs das mensagens no Telegram
        Estado dos uploads
      Compatibilidade Motor
        sqlite_backend.py
        Interface assíncrona semelhante ao MongoDB
        motor/motor_asyncio.py
      Backup
        Banco SQLite
        Canal do Telegram
        Arquivo de configuração
    Leitura e download
      Cliente solicita arquivo virtual
      ftp/pathio.py
      Consulta metadados no SQLite
      Recupera partes no Telegram
      Entrega fluxo pelo FTP
    Inicialização
      INICIAR_NEBULA.bat
        Valida .env e Python portátil
        Executa setup_database.py
        Executa run_nebula.py
      run_nebula.py
        Configura console e logs
        Resolve canal do Telegram
        Inicia main.py
      Configuração
        .env
        API_ID e API_HASH
        BOT_TOKENS e CHAT_ID
        HOST e PORT
        Limites de disco e workers
    Administração
      00 Instalar dependências
      01 Configurar Telegram
      02 Testar Telegram
      03 Criar banco SQLite
      04 Gerenciar usuários FTP
      05 Verificar acervo
      verificar_acervo.py
        Gera árvore do acervo em logs
    Distribuição
      Windows
        Python 3.11 portátil
        Scripts BAT
        rclone e WinFsp opcionais
      Docker
        Dockerfile
        docker-compose.yml
        Volumes para data e staging
    Segurança
      Não versionar .env
      Não versionar sessão do Telegram
      Não versionar banco ou staging
      FTP simples somente local ou via VPN
      Proteger credenciais e backups
    Qualidade
      tests
        Banco e migrações
        Integração FTP e SQLite
        Backend de compatibilidade
        Limpeza após upload
        Relatório do acervo
      requirements.txt
        pyftpdlib
        aiofiles
        pyrogram
        tgcrypto
        python-dotenv
        requests
```

## Fluxo principal

```mermaid
flowchart LR
    A[Cliente FTP] -->|envia arquivo| B[Servidor FTP]
    B --> C[staging local]
    C --> D[Fila assíncrona]
    D --> E[Workers de upload]
    E -->|documentos ou partes| F[Canal privado no Telegram]
    B <--> G[(SQLite)]
    D <--> G
    E --> G
    A -->|lista ou baixa| B
    B -->|consulta nomes, partes e IDs| G
    B -->|recupera conteúdo| F
```

## Arquivos centrais

| Área | Arquivos | Responsabilidade |
|---|---|---|
| Aplicação | `main.py`, `run_nebula.py` | Inicialização, filas, workers, bot e tarefas de manutenção |
| FTP | `ftp/server.py`, `ftp/pathio.py`, `ftp/tg.py` | Protocolo FTP e acesso ao conteúdo virtual |
| Persistência | `database.py`, `sqlite_backend.py` | Schema, migrações e camada assíncrona sobre SQLite |
| Administração | `accounts_manager.py`, `configurar_telegram.py`, `verificar_acervo.py` | Usuários, credenciais do Telegram e auditoria do acervo |
| Operação | `*.bat`, `.env`, `requirements.txt` | Instalação, configuração e execução no Windows |
| Contêiner | `Dockerfile`, `docker-compose.yml` | Execução isolada e volumes persistentes |
| Testes | `tests/` | Verificação do banco, FTP, uploads e relatórios |

