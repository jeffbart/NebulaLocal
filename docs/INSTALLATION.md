# Instalação do Nebula Local

Este guia prepara o Nebula Local no Windows usando SQLite. MongoDB não é necessário.

## 1. Pré-requisitos

Instale:

- [Git para Windows](https://git-scm.com/download/win), caso use `git clone`.
- Um cliente FTP, como [FileZilla Client](https://filezilla-project.org/) ou [WinSCP](https://winscp.net/).
- Telegram instalado em um telefone ou computador.

Não é necessário instalar Python. O projeto já inclui, na pasta `python/`, um runtime Python 3.11 portátil e isolado de qualquer instalação do sistema — os scripts `.bat` usam sempre esse runtime.

## 2. Baixar o projeto

### Opção A: clonar pelo CMD

1. Pressione `Windows + R`.
2. Digite `cmd` e pressione `Enter` para abrir o Prompt de Comando.
3. Copie as duas linhas abaixo.
4. Clique com o botão direito dentro da janela preta do CMD para colar o comando.
5. Pressione `Enter` e aguarde o download terminar.

```bat
git clone https://github.com/jeffbart/NebulaLocal.git
cd NebulaLocal
```

A primeira linha baixa o projeto. A segunda entra na pasta `NebulaLocal`. Se aparecer a mensagem de que `git` não é reconhecido, instale o Git para Windows indicado nos pré-requisitos e repita o procedimento.

### Opção B: baixar sem usar comandos

1. Abra a [página do NebulaLocal no GitHub](https://github.com/jeffbart/NebulaLocal).
2. Clique no botão verde **Code**.
3. Clique em **Download ZIP**.
4. Quando terminar, clique com o botão direito no ZIP e escolha **Extrair Tudo**.
5. Abra a pasta extraída `NebulaLocal`.

Não execute o projeto de dentro do ZIP sem extraí-lo.

## 3. Instalar as dependências

Dê dois cliques em:

```text
00_INSTALAR_DEPENDENCIAS.bat
```

Esse script confirma o Python portátil incluído (`python\python.exe`) e instala as bibliotecas de `requirements.txt` dentro dele — nenhuma instalação de Python no sistema é necessária, e nenhum Python do sistema é alterado.

Como as dependências já vêm pré-instaladas no repositório, esse passo normalmente é instantâneo e funciona mesmo sem internet. Se o `requirements.txt` for atualizado (por exemplo após um `git pull`) e for preciso baixar algo novo, e o Windows apresentar um problema local de certificado, o instalador tenta novamente usando somente os hosts oficiais do PyPI.

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

O instalador usa uma reserva mínima padrão de 20 GB no disco onde está a pasta `staging`. Confirme que o `.env` contém:

```dotenv
MIN_FREE_DISK_GB=20
```

Quando o espaço livre ficar abaixo desse limite, novas gravações FTP serão pausadas até que os uploads pendentes sejam enviados ao Telegram e removidos progressivamente do disco. A retomada é automática.

## 6. Criar o banco SQLite

Execute:

```text
03_CRIAR_BANCO_SQLITE.bat
```

O resultado esperado é semelhante a:

```text
SQLite pronto: ...\data\nebula.db (schema v2)
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

## Acesso remoto com Tailscale

O Tailscale cria uma rede privada entre dispositivos autorizados, mesmo quando eles estão atrás de roteadores ou mudam de rede. Cada equipamento recebe um IP Tailscale estável e um nome MagicDNS. O Nebula continua fornecendo o serviço FTP; o Tailscale fornece somente a conectividade privada entre as máquinas. Consulte os guias oficiais de [instalação no Windows](https://tailscale.com/docs/install/windows), [conexão entre dispositivos](https://tailscale.com/docs/how-to/connect-to-devices) e [MagicDNS](https://tailscale.com/docs/features/magicdns).

### No computador que executa o Nebula

1. Instale o Tailscale e faça login.
2. Confirme que o computador aparece como conectado na página **Machines** da administração da tailnet.
3. Mantenha estas opções no `.env`:

   ```dotenv
   HOST=0.0.0.0
   PORT=2121
   ```

4. Inicie o Nebula normalmente.
5. Abra o PowerShell e descubra o IPv4 do Tailscale:

   ```powershell
   tailscale ip -4
   ```

6. Se o Firewall do Windows solicitar autorização, permita o Python/Nebula para a interface usada pelo Tailscale. Não crie encaminhamento de porta no roteador.

### No computador remoto

1. Instale o Tailscale e entre na mesma tailnet, ou use uma conta/dispositivo explicitamente autorizado.
2. Confirme a conectividade com o IP ou nome MagicDNS do servidor:

   ```powershell
   tailscale ping NOME-DO-SERVIDOR
   Test-NetConnection NOME-DO-SERVIDOR -Port 2121
   ```

3. Configure o WinSCP ou FileZilla:

   ```text
   Host: NOME-DO-SERVIDOR ou 100.x.y.z
   Porta: 2121
   Protocolo: FTP
   Criptografia: FTP simples
   Modo: Passivo
   Usuário: conta criada no Nebula
   Senha: senha criada no Nebula
   ```

O MagicDNS permite usar o nome da máquina em vez do IP Tailscale. Se não resolver, use temporariamente o endereço `100.x.y.z` mostrado por `tailscale ip -4` e revise o DNS da tailnet.

### Controle de acesso

Na política padrão, dispositivos próprios da mesma tailnet normalmente conseguem se comunicar. Para uma tailnet compartilhada, configure acesso mínimo na página **Access controls**. A documentação atual recomenda [Grants](https://tailscale.com/docs/features/access-control/grants).

FTP passivo usa a conexão de controle na porta 2121 e conexões TCP adicionais para os dados. Se a tailnet possuir regras restritivas, elas precisam permitir essas conexões entre o cliente autorizado e o computador do Nebula. Limite a origem a usuários/dispositivos confiáveis e o destino somente ao servidor; evite uma permissão global para toda a tailnet.

Não use **Tailscale Funnel**, pois ele tornaria o serviço acessível publicamente. Também não é necessário configurar Tailscale Serve: para FTP passivo, conecte o cliente diretamente ao IP Tailscale ou nome MagicDNS do computador.

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

Não encaminhe essas portas no roteador para a internet. Para acesso remoto, siga a seção [Acesso remoto com Tailscale](#acesso-remoto-com-tailscale).

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
