# Como usar o Nebula Local

## Iniciar e encerrar

Inicie com:

```text
INICIAR_NEBULA.bat
```

Mantenha a janela aberta. Para encerrar corretamente, pressione `Ctrl+C` e aguarde a mensagem de desligamento.

Evite encerrar à força durante um upload. O arquivo pode permanecer em `staging` e ser retomado ou detectado na próxima execução.

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

## Enviar arquivos

Arraste arquivos do painel local para o painel remoto do cliente FTP.

O fluxo é:

1. o cliente transfere para a pasta local `staging`;
2. o Nebula registra o arquivo no SQLite;
3. trabalhadores enviam as partes ao canal do Telegram;
4. o status muda para concluído;
5. o arquivo temporário pode ser removido.

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

### Banco indisponível

Execute `03_CRIAR_BANCO_SQLITE.bat`. Confirme que a pasta do projeto tem permissão de escrita e que nenhum programa externo bloqueia `data\nebula.db`.

## Uso responsável

Use apenas para conteúdo que você tem autorização para armazenar. Respeite os termos do Telegram e mantenha uma cópia independente de dados importantes.
