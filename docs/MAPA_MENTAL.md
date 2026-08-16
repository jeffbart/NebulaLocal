# Mapa mental do Nebula Local

O Nebula permite enviar arquivos pelo computador e guardá-los em um canal privado do Telegram.

```mermaid
mindmap
  root((Nebula Local))
    Você envia um arquivo
      Usa FileZilla ou WinSCP
      Escolhe a pasta desejada
      O envio acontece como em um FTP comum
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
    A[Você envia o arquivo] --> B[Nebula recebe]
    B --> C[Arquivo é enviado ao Telegram]
    C --> D[Arquivo fica arquivado no canal privado]
    D --> E[Você pode acessar novamente pelo Nebula]
```

> **Em resumo:** o arquivo enviado ao Nebula é arquivado no canal privado do Telegram. O Nebula mantém as informações necessárias para localizar e recuperar esse arquivo depois.

## O que deve ser protegido

- O canal privado do Telegram, onde os arquivos ficam arquivados.
- O banco local `data/nebula.db`, que funciona como o catálogo dos arquivos.
- O arquivo `.env` e a sessão do bot, que contêm dados de acesso e não devem ser compartilhados.
