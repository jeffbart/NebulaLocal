# Configuração do Telegram

O Nebula Local usa duas interfaces do Telegram:

- **Bot API**, autenticada pelo token criado no BotFather;
- **MTProto**, autenticado por `API_ID` e `API_HASH`.

Por isso, apenas o token do bot não é suficiente.

## 1. Obter API_ID e API_HASH

1. Acesse [my.telegram.org](https://my.telegram.org).
2. Informe o telefone vinculado à sua conta.
3. Digite o código recebido no aplicativo Telegram.
4. Abra **API development tools**.
5. Crie uma aplicação com plataforma `Desktop` ou `Other`.
6. Guarde `api_id` e `api_hash`.

Não publique o `API_HASH`.

## 2. Criar o bot

1. Abra o perfil oficial [@BotFather](https://t.me/BotFather).
2. Envie `/newbot`.
3. Escolha um nome e um username terminado em `bot`.
4. Guarde o token fornecido.

Quem possuir o token poderá controlar o bot. Se ele vazar, revogue-o pelo BotFather e gere outro.

## 3. Criar o canal

1. Crie um canal privado.
2. Adicione o bot como administrador.
3. Permita que ele publique mensagens.
4. Publique uma mensagem nova depois de adicioná-lo.

Não use o canal para conversas. Ele funcionará como armazenamento dos documentos.

## 4. Configurar automaticamente

Execute:

```text
01_CONFIGURAR_TELEGRAM.bat
```

O assistente valida as credenciais e grava os valores no `.env`.

## 5. Descobrir o CHAT_ID

Se você não souber o ID:

1. mantenha o Nebula desligado;
2. publique uma mensagem nova no canal;
3. execute `DESCOBRIR_CHAT_ID.bat`;
4. informe o token.

O resultado possui este formato:

```dotenv
CHAT_ID=-1001234567890
```

O prefixo `-100` faz parte do ID.

## 6. Testar

Execute:

```text
02_TESTAR_TELEGRAM.bat
```

O resultado esperado confirma o bot, o título e o ID do canal.

## Canal privado e Pyrogram

Na primeira inicialização, o Bot API pode reconhecer o canal antes da sessão MTProto. O inicializador resolve isso publicando silenciosamente:

```text
Nebula Local conectado ao canal.
```

Esse evento registra o canal privado na sessão do Pyrogram.

## Problemas comuns

### Token recusado

- Copie novamente o token do BotFather.
- Não inclua espaços ou aspas.
- Gere outro token se o atual foi revogado.

### Canal não acessível

- Adicione o bot como administrador.
- Permita publicação de mensagens.
- Confirme que o canal ainda existe.

### Nenhum canal encontrado

- Publique uma mensagem depois de adicionar o bot.
- Deixe o servidor desligado durante a descoberta.
- Execute novamente `DESCOBRIR_CHAT_ID.bat`.

### Peer id invalid

- Execute `02_TESTAR_TELEGRAM.bat`.
- Confirme que o `CHAT_ID` começa com `-100`.
- Inicie pela versão atual de `INICIAR_NEBULA.bat`.

## Segurança

Nunca publique `.env`, `API_HASH`, `BOT_TOKENS` ou `Nebula_MonoBot.session`.
