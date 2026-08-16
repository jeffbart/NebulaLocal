# Mapa mental do Nebula Local

O Nebula permite enviar arquivos pelo computador e guardá-los em um canal privado do Telegram.

```mermaid
mindmap
  root((Nebula Local))
    Você envia um arquivo
      Usa FileZilla ou WinSCP
      Ou usa o rclone como uma unidade do Windows
      Escolhe a pasta desejada
      O envio acontece como em um FTP comum
    Unidade do Windows com rclone
      O Nebula aparece como um drive no computador
      Pode ser montado como unidade S
      Você usa o Explorador de Arquivos
      Copiar para o drive envia ao Nebula
      Nebula precisa estar aberto
    O Nebula recebe
      Guarda o arquivo temporariamente no computador
      Organiza o envio
      Mostra o andamento no bot
    O arquivo é arquivado
      Vai para o canal privado do Telegram
      Arquivos grandes podem ser divididos em partes
      O nome e a pasta são preservados
      A cópia temporária é removida depois do envio
    Você acessa quando precisar
      Encontra o arquivo pelo FTP
      O Nebula busca o conteúdo no Telegram
      O download volta para o seu computador
    Para funcionar
      Nebula precisa estar aberto
      Internet precisa estar disponível
      Bot precisa ter acesso ao canal
      Banco de dados local deve ser preservado
```

## Caminho do arquivo

```mermaid
flowchart LR
    A[FileZilla, WinSCP ou drive do rclone] --> B[Você envia o arquivo]
    B --> C[Nebula recebe]
    C --> D[Arquivo é enviado ao Telegram]
    D --> E[Arquivo fica arquivado no canal privado]
    E --> F[Você pode acessar novamente pelo Nebula]
```

> **Em resumo:** o arquivo enviado ao Nebula é arquivado no canal privado do Telegram. O Nebula mantém as informações necessárias para localizar e recuperar esse arquivo depois.

## Usar como um drive com o rclone

O rclone pode apresentar o Nebula como uma unidade do Windows, por exemplo `S:` com o nome `FTPLOCAL`. Assim, você pode abrir o Explorador de Arquivos e copiar, mover ou abrir pastas como faria em outro drive.

Ao copiar um arquivo para essa unidade, o rclone entrega o arquivo ao Nebula. Em seguida, o Nebula o arquiva no canal privado do Telegram. Para acessar a unidade, o Nebula e a montagem do rclone precisam estar em execução.

Para configurar essa opção:

1. Instale o WinFsp usando o instalador incluído na pasta `rclone`.
2. Execute `rclone\01_Rclone config.bat` e configure o acesso chamado `FTPLOCAL`.
3. Inicie o Nebula com `INICIAR_NEBULA.bat`.
4. Execute `rclone\02_mount_FTPLOCAL.bat` para montar a unidade `S:`.

> O drive do rclone é uma forma mais familiar de acessar o Nebula. Os arquivos continuam sendo arquivados no Telegram; eles não ficam armazenados permanentemente na unidade `S:`.

## O que deve ser protegido

- O canal privado do Telegram, onde os arquivos ficam arquivados.
- O banco local `data/nebula.db`, que funciona como o catálogo dos arquivos.
- O arquivo `.env` e a sessão do bot, que contêm dados de acesso e não devem ser compartilhados.

