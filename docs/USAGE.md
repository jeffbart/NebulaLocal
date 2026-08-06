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

## Acessar remotamente com Tailscale

Com o Tailscale instalado e conectado nos dois computadores, substitua `127.0.0.1` pelo IP Tailscale ou nome MagicDNS do computador que executa o Nebula:

```text
Host: nebulalocal ou 100.x.y.z
Porta: 2121
Protocolo: FTP
Criptografia: FTP simples
Modo: Passivo
```

Antes de abrir o cliente FTP, valide no computador remoto:

```powershell
tailscale ping nebulalocal
Test-NetConnection nebulalocal -Port 2121
```

Se o ping Tailscale funcionar, mas a porta 2121 falhar:

- confirme que o Nebula está em execução e usa `HOST=0.0.0.0`;
- confira o Firewall do Windows no servidor;
- revise as [regras de acesso da tailnet](https://tailscale.com/docs/features/access-control);
- lembre que o modo passivo também abre conexões TCP de dados além da porta de controle;
- tente o IP `100.x.y.z` se o nome MagicDNS não resolver.

O Tailscale deve ser usado como rede privada direta. Não exponha a porta no roteador e não use Funnel para publicar o FTP na internet. As contas e permissões do Nebula continuam valendo normalmente.

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

Ao reiniciar, o Nebula reconstrói automaticamente a fila em memória usando os registros `staging` e `uploading` do SQLite. Arquivos que já possuam partes confirmadas retomam do ponto persistido; registros cujo arquivo local não exista passam para `failed`.

Todos os arquivos presentes na fila reconstruída ficam protegidos contra o coletor de temporários, mesmo que aguardem por mais tempo que `MAX_STAGING_AGE`.

Cada documento publicado no canal recebe uma legenda com o nome original, a numeração, o tamanho total e o progresso acumulado do upload. Embora o envio físico ocorra do final para o início para liberar espaço progressivamente, a legenda segue a ordem das mensagens: a primeira parte enviada aparece como `Parte: 01`, e a contagem cresce até o total.

Identificadores hexadecimais usados internamente na pasta `staging` são ocultados da legenda. Assim, um nome interno como `7e61363d2ef04b099d4d3034c3d50a4f_filme.mkv` aparece no canal apenas como `filme.mkv`.

O formato da legenda é:

```text
Worker: W2
Pasta: /Filmes/1960S/
Arquivo: After.the.Fox.1966.1080p.AMZN.WEB-DL.DDP2.0.H.264-GPRS.mkv
Parte: 102 de 117
Enviado: 6.37 GB de 7.31 GB (87.2%)
```

Todas as partes identificam o worker responsável (`W1` a `W4`). Após o commit final no SQLite, a legenda da última parte é atualizada com um tique verde, os horários de início e término e a duração total do upload em minutos.

Não apague arquivos manualmente de `staging` enquanto o Nebula estiver processando.

### Reserva de espaço em disco

Por padrão, o Nebula preserva pelo menos 20 GB livres no disco de `staging`. Se o espaço cair abaixo da reserva, o recebimento FTP é pausado, enquanto os arquivos já enfileirados continuam sendo enviados ao Telegram e removidos progressivamente do disco. Assim que houver novamente pelo menos 20 GB livres, o FTP retoma automaticamente.

O limite pode ser alterado no `.env`:

```dotenv
MIN_FREE_DISK_GB=20
```

### Comandos do bot no Telegram

- `/queue` — apaga a mensagem do comando e publica a fila organizada em itens enfileirados, em processamento, aguardando e com falha; itens em processamento incluem o volume já confirmado no Telegram e o tamanho total;
- `/fetch` — envia a relação completa dos uploads com falha;
- `/clearfailed` — exibe o aviso de limpeza, sem remover nada;
- `/clearfailed confirmar` — remove os registros com falha e os respectivos arquivos temporários locais;
- `/help` — mostra essas instruções no Telegram.

Quando todas as tentativas de envio de uma parte falham, o upload recebe o status `failed` e passa a aparecer em `/queue` e `/fetch`.

### Nomes com acentos

O servidor anuncia e utiliza UTF-8 para nomes de arquivos e diretórios. Clientes compatíveis, como WinSCP e FileZilla, devem detectar essa configuração automaticamente. Se um cliente antigo exibir `FÃ¡brica` no lugar de `Fábrica`, force UTF-8 nas configurações de codificação de nomes do cliente e reconecte.

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

## Backup e restauração

> **Risco de perda:** o canal do Telegram armazena as partes dos arquivos, mas o computador armazena o banco que relaciona nomes, pastas e partes. Uma formatação, falha de disco ou crash sem backup pode tornar os arquivos inacessíveis pelo Nebula mesmo que as mensagens ainda existam no canal.

### O que guardar

Encerre o Nebula com `Ctrl+C` e aguarde o desligamento antes de copiar o banco. Faça backup de:

```text
data\nebula.db
.env
Nebula_MonoBot.session
rclone\rclone.conf
```

- `data\nebula.db` é o item principal: contém contas, permissões, diretórios virtuais e a relação entre os arquivos e as mensagens do Telegram.
- `.env` contém a configuração e credenciais do Telegram.
- `Nebula_MonoBot.session` preserva a sessão usada pelo Pyrogram.
- `rclone\rclone.conf` é necessário somente para quem usa a unidade `FTPLOCAL`.
- Se houver transferências pendentes, copie também `staging\`. Prefira concluir os uploads antes do backup ou da troca de computador.

Guarde o backup fora do computador do Nebula, por exemplo em um disco externo desconectado após a cópia, outro computador ou armazenamento confiável. `.env`, `.session` e `rclone.conf` possuem dados sensíveis; proteja o backup com criptografia e não o publique no GitHub.

Faça backups periódicos e sempre antes de:

- formatar ou trocar o computador;
- substituir ou reparar o disco;
- atualizar o sistema ou o projeto;
- alterar em massa arquivos, usuários ou permissões.

### Restaurar em outro computador

1. Instale ou clone o Nebula Local no novo computador.
2. Execute a instalação das dependências, mas não inicie o servidor ainda.
3. Copie `nebula.db` para `data\nebula.db` e restaure `.env` e `Nebula_MonoBot.session` na raiz do projeto.
4. Se usar a unidade local, restaure `rclone.conf` dentro da pasta `rclone` e instale o WinFsp.
5. Restaure `staging\` somente se ela tiver sido incluída no backup.
6. Confirme que o bot ainda participa do mesmo canal privado e execute `02_TESTAR_TELEGRAM.bat`.
7. Inicie o Nebula e teste a listagem e o download de um arquivo antes de descartar o backup antigo.

O backup local não substitui a preservação do canal: banco e mensagens do Telegram são partes complementares da recuperação.

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
