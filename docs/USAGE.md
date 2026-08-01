# Como usar o Nebula Local

## Iniciar e encerrar

Inicie com:

```text
INICIAR_NEBULA.bat
```

Mantenha a janela aberta. Para encerrar corretamente, pressione `Ctrl+C` e aguarde a mensagem de desligamento.

Evite encerrar à força durante um upload. As partes já confirmadas ficam registradas no SQLite e o restante do arquivo pode permanecer em `staging` para retomada.

## Conectar pelo FileZilla

Na barra de conexão rápida:

```text
Host: 127.0.0.1
Usuário: seu_login
Senha: sua_senha
Porta: 2121
```

Se usar o Gerenciador de Sites:

- Protocolo: **FTP — Protocolo de Transferência de Arquivos**.
- Criptografia: **Usar FTP simples**.
- Tipo de logon: **Normal**.
- Modo de transferência: **Passivo**.

O diretório inicial será `/<seu_login>`.

## Usar como unidade do Windows (opcional)

Depois de concluir a [configuração opcional do rclone](INSTALLATION.md#unidade-ftplocal-opcional), mantenha o Nebula aberto e execute:

```text
rclone\02_mount_FTPLOCAL.bat
```

O Explorador de Arquivos mostrará a unidade `S:` com o nome `FTPLOCAL`. Você poderá copiar, mover, renomear e excluir itens usando programas do próprio computador. As operações continuam passando pelo servidor FTP local e pelo fluxo normal de upload do Nebula.

- Não feche a janela de montagem enquanto estiver usando a unidade.
- Para desmontar com segurança, encerre transferências e pressione `Ctrl+C` nessa janela.
- Execute o script como usuário normal. Uma unidade montada em uma janela elevada pode não aparecer no Explorador executado sem elevação.
- O cache fica em `%LOCALAPPDATA%\NebulaLocal\rclone-cache` e pode chegar ao limite configurado de 100 GB.
- Se o WinFsp ainda não estiver instalado, execute `rclone\winfsp-2.0.23075.msi`; sem esse pré-requisito, o rclone não consegue montar a unidade no Windows.
- Se a unidade não aparecer, confirme também que `S:` está livre e que o remoto se chama exatamente `FTPLOCAL`.

## Enviar arquivos

Arraste arquivos do painel local para o painel remoto do cliente FTP.

O fluxo é:

1. o cliente transfere para a pasta local `staging`;
2. o Nebula registra o arquivo no SQLite;
3. trabalhadores enviam as partes ao canal do Telegram, do final para o início;
4. cada parte confirmada é registrada no SQLite antes de ser removida do disco;
5. o tamanho ocupado em `staging` diminui progressivamente;
6. após a confirmação da última parte, o status muda para concluído e o arquivo temporário é removido.

O envio em ordem inversa não altera o arquivo baixado: os metadados preservam a ordem original das partes. Se o processo for interrompido depois de uma confirmação, o Nebula reutiliza o registro persistido e não depende dos bytes locais que já foram liberados.

Não apague arquivos manualmente de `staging` enquanto o Nebula estiver processando.

## Baixar arquivos

Arraste o arquivo remoto para uma pasta local. O Nebula consulta as partes registradas no SQLite e transmite o conteúdo ao cliente FTP.

Downloads dependem da disponibilidade do Telegram, da conexão e da permanência das mensagens no canal.

## Criar pastas, renomear e excluir

Use os comandos normais do cliente FTP:

- criar diretório;
- renomear;
- excluir arquivo;
- excluir diretório.

Essas operações alteram os metadados virtuais. Excluir um item no FTP não deve ser confundido com administrar manualmente as mensagens do canal.

## Gerenciar usuários

Encerre o servidor antes de editar contas e execute:

```text
04_GERENCIAR_USUARIOS_FTP.bat
```

O gerenciador permite:

- listar usuários;
- criar conta;
- alterar senha;
- visualizar permissões;
- adicionar, editar ou remover permissões;
- excluir usuário.

Os dados ficam em `data\nebula.db`.

## Backup

Com o Nebula encerrado, copie:

```text
data\nebula.db
.env
Nebula_MonoBot.session
```

Armazene o backup de `.env` e `.session` em local protegido, pois são dados sensíveis.

O backup do banco não substitui a preservação do canal: os documentos precisam continuar disponíveis no Telegram.

## Logs

O arquivo principal é:

```text
nebula.log
```

Ao reportar um erro, remova tokens, caminhos pessoais e outros dados sensíveis antes de compartilhar o log.

## Problemas comuns

### Peer id invalid

Confirme que:

- o bot é administrador;
- o `CHAT_ID` começa com `-100`;
- o canal ainda existe;
- o bot consegue publicar.

Execute `02_TESTAR_TELEGRAM.bat`. A inicialização atual registra automaticamente canais privados na sessão do Pyrogram.

### Login FTP recusado

- Confira maiúsculas e minúsculas.
- Execute o gerenciador e confirme que a conta existe.
- Verifique se está usando a porta 2121.

### A porta 2121 já está em uso

Feche outra instância do Nebula. Se precisar alterar a porta, edite:

```dotenv
PORT=2122
```

Depois use a mesma porta no cliente FTP.

### Listagem ou transferência trava

- Use modo passivo.
- Confira o Firewall do Windows.
- Verifique o intervalo `PASSIVE_PORTS`.
- Consulte `nebula.log`.

### Arquivo permanece em staging

- Mantenha o Nebula em execução.
- Confirme a conexão com o Telegram.
- Verifique espaço livre local.
- Consulte erros de upload e tentativas no log.

Durante um upload normal, o tamanho do arquivo em `staging` diminui a cada parte confirmada. Um arquivo que não diminui pode indicar falha no Telegram, no banco ou na permissão de escrita da pasta.

### Banco indisponível

Execute `03_CRIAR_BANCO_SQLITE.bat`. Confirme que a pasta do projeto tem permissão de escrita e que nenhum programa externo bloqueia `data\nebula.db`.

## Uso responsável

Use apenas para conteúdo que você tem autorização para armazenar. Respeite os termos do Telegram e mantenha uma cópia independente de dados importantes.
