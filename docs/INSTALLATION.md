# Instalação do Nebula Local

Este guia prepara o Nebula Local no Windows usando SQLite. MongoDB não é necessário.

## 1. Pré-requisitos

Instale:

- [Python 3.10 ou superior](https://www.python.org/downloads/).
- [Git para Windows](https://git-scm.com/download/win), caso use `git clone`.
- Um cliente FTP, como [FileZilla Client](https://filezilla-project.org/) ou [WinSCP](https://winscp.net/).
- Telegram instalado em um telefone ou computador.

Durante a instalação do Python, marque **Add Python to PATH**.

Para conferir:

```powershell
python --version
```

## 2. Baixar o projeto

Pelo Git:

```powershell
git clone https://github.com/jeffbart/NebulaLocal.git
cd NebulaLocal
```

Também é possível baixar o ZIP no GitHub, extrair e abrir a pasta.

Não execute o projeto de dentro do ZIP sem extraí-lo.

## 3. Instalar as dependências

Dê dois cliques em:

```text
00_INSTALAR_DEPENDENCIAS.bat
```

Esse script:

1. verifica o Python;
2. cria o ambiente isolado `.venv`;
3. instala as bibliotecas de `requirements.txt`.

Se o Windows apresentar um problema local de certificado, o instalador tenta novamente usando somente os hosts oficiais do PyPI.

## 4. Preparar o Telegram

Você precisa de:

- `API_ID`;
- `API_HASH`;
- token do bot;
- ID de um canal privado.

### Criar API_ID e API_HASH

1. Acesse [my.telegram.org](https://my.telegram.org).
2. Entre com seu número de telefone.
3. Abra **API development tools**.
4. Crie uma aplicação.
5. Copie `api_id` e `api_hash`.

### Criar o bot

1. Abra o [@BotFather](https://t.me/BotFather).
2. Envie `/newbot`.
3. Defina nome e username terminado em `bot`.
4. Guarde o token fornecido.

### Criar o canal

1. Crie um canal privado no Telegram.
2. Adicione o bot como administrador.
3. Permita que ele publique mensagens.
4. Publique uma mensagem nova no canal.

Mais detalhes estão em [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md).

## 5. Executar o assistente do Telegram

Dê dois cliques em:

```text
01_CONFIGURAR_TELEGRAM.bat
```

Informe `API_ID`, `API_HASH`, token e `CHAT_ID`.

Se ainda não souber o `CHAT_ID`:

1. deixe o Nebula desligado;
2. publique uma mensagem nova no canal;
3. execute `DESCOBRIR_CHAT_ID.bat`;
4. informe o token do bot.

Depois confirme a configuração executando:

```text
02_TESTAR_TELEGRAM.bat
```

As credenciais ficam no arquivo local `.env`, ignorado pelo Git.

## 6. Criar o banco SQLite

Execute:

```text
03_CRIAR_BANCO_SQLITE.bat
```

O resultado esperado é semelhante a:

```text
SQLite pronto: ...\data\nebula.db (schema v1)
```

O comando é idempotente: pode ser executado novamente quando houver atualizações de schema.

## 7. Criar uma conta FTP

Execute:

```text
04_GERENCIAR_USUARIOS_FTP.bat
```

No menu:

1. escolha **Add user**;
2. informe um login com letras, números ou `_`;
3. informe uma senha;
4. volte e encerre o gerenciador.

Cada usuário recebe como diretório inicial `/<login>`.

## 8. Iniciar o servidor

Execute:

```text
INICIAR_NEBULA.bat
```

Na primeira execução, o bot pode publicar silenciosamente:

```text
Nebula Local conectado ao canal.
```

Quando estiver pronto, a janela informará que o FTP está rodando na porta 2121. Não feche essa janela enquanto estiver usando o servidor.

## 9. Conectar

Use estas configurações no cliente FTP:

```text
Host: 127.0.0.1
Porta: 2121
Protocolo: FTP
Criptografia: FTP simples
Modo: Passivo
```

Use o login e a senha criados no gerenciador.

## Unidade FTPLOCAL opcional

Se preferir acessar o Nebula pelo Explorador de Arquivos, você pode montar o FTP local como a unidade `S:` chamada `FTPLOCAL`. O FileZilla e o WinSCP continuam sendo opções; esta etapa não é obrigatória.

### Pré-requisitos

1. Verifique se o WinFsp já está instalado no Windows.
2. Se ainda não estiver, execute `rclone\winfsp-2.0.23075.msi` e conclua a instalação. O WinFsp é pré-requisito obrigatório para o `rclone mount` criar uma unidade no Windows.
3. Confirme que `rclone.exe` está na mesma pasta dos arquivos `.bat`.

O projeto inclui o executável do rclone e o instalador WinFsp usado por esta versão. O arquivo `rclone.conf` local não é enviado ao Git; preserve-o em local seguro, pois ele contém os dados de acesso ao FTP.

Se preferir obter versões mais recentes diretamente dos projetos oficiais, consulte [WinFsp](https://winfsp.dev/) e [rclone para Windows](https://rclone.org/downloads/).

### Configurar o remoto

Execute:

```text
rclone\01_Rclone config.bat
```

No assistente do rclone:

1. escolha `n` para criar um remoto;
2. use exatamente o nome `FTPLOCAL`;
3. selecione o tipo `ftp`;
4. informe o host `127.0.0.1` e a porta `2121`;
5. informe o usuário e a senha FTP criados no Nebula;
6. mantenha FTP simples, sem TLS, para a conexão estritamente local;
7. salve e encerre o assistente.

### Montar a unidade

Com o Nebula em execução, abra normalmente, sem **Executar como administrador**:

```text
rclone\02_mount_FTPLOCAL.bat
```

O script procura `rclone.exe` e `rclone.conf` na própria pasta, monta `S:` com o nome `FTPLOCAL` e guarda cache e logs em `%LOCALAPPDATA%\NebulaLocal\rclone-cache`. Mantenha a janela aberta; pressione `Ctrl+C` para desmontar.

Se a montagem informar que WinFsp ou FUSE não está disponível, encerre o script, execute `rclone\winfsp-2.0.23075.msi` e tente novamente depois de concluir a instalação.

Se `S:` já estiver ocupada, edite a variável `MOUNT_DRIVE` no início de `02_mount_FTPLOCAL.bat` e escolha outra letra livre.

## 10. Firewall e rede local

Para uso somente no mesmo computador, normalmente nenhuma regra adicional é necessária.

Para outro equipamento da rede:

1. descubra o IPv4 do computador com `ipconfig`;
2. conecte usando esse IP;
3. permita o Python ou a porta 2121 no Firewall do Windows quando solicitado;
4. mantenha a rede marcada como privada;
5. libere também o intervalo passivo configurado, se necessário.

Não encaminhe essas portas no roteador para a internet. Use uma VPN se precisar de acesso remoto.

## Atualização

Antes de atualizar, encerre o Nebula com `Ctrl+C` e faça backup de:

```text
.env
data\nebula.db
Nebula_MonoBot.session
rclone\rclone.conf
```

Se existirem uploads pendentes, copie também `staging\`. Guarde esse backup fora do computador; uma cópia no mesmo disco não protege contra formatação ou falha física. Consulte o procedimento completo de [backup e restauração](USAGE.md#backup-e-restauração).

Depois:

```powershell
git pull
```

Execute novamente:

```text
00_INSTALAR_DEPENDENCIAS.bat
03_CRIAR_BANCO_SQLITE.bat
```

## Desinstalação

Encerre o programa e remova a pasta do projeto. Antes disso, faça o [backup completo](USAGE.md#backup-e-restauração). Apagar a pasta ou formatar o computador sem preservar o banco pode eliminar o acesso organizado aos arquivos mantidos no Telegram.

Revogue o token pelo BotFather caso não pretenda mais usar o bot.

## Próximo passo

Leia [Como usar o Nebula Local](USAGE.md).
