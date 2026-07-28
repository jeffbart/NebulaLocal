# Créditos e agradecimentos

## Projeto original

O Nebula Local é um trabalho derivado do **NebulaFTP**, criado e publicado por:

**Samuel de Sousa Santos (`@samucamg`)**

- GitHub: [github.com/samucamg](https://github.com/samucamg)
- Projeto original: [github.com/samucamg/NebulaFTP](https://github.com/samucamg/NebulaFTP)

Nosso sincero agradecimento a Samuel por idealizar o uso do Telegram como backend para uma interface FTP, desenvolver o projeto e disponibilizá-lo publicamente. Esta edição local existe graças ao ponto de partida criado por ele.

## Trabalho anterior e licença

O arquivo `LICENSE` herdado contém o aviso:

```text
Copyright (c) 2021-present RuslanUC
```

Esse aviso é preservado conforme os termos da Licença MIT. A presença dessa atribuição indica código ou trabalho anterior incorporado à base da qual o NebulaFTP derivou.

## Nebula Local

Esta adaptação acrescenta, entre outras mudanças:

- persistência local em SQLite;
- remoção da dependência operacional do MongoDB;
- assistentes e scripts para instalação no Windows;
- descoberta e validação do canal do Telegram;
- compatibilidade de inicialização e encerramento no Windows;
- testes do schema, backend e autenticação FTP;
- documentação específica para instalação e uso local.

As modificações não implicam endosso do autor original.

## Projetos de código aberto

Obrigado às comunidades responsáveis por:

- Python;
- SQLite;
- Pyrogram;
- TgCrypto;
- aiofiles;
- python-dotenv;
- Requests;
- pyftpdlib.

## Como preservar os créditos

Ao redistribuir ou criar outro trabalho derivado:

1. mantenha o arquivo `LICENSE`;
2. preserve os avisos de copyright existentes;
3. mantenha referência ao repositório original do NebulaFTP;
4. descreva claramente suas próprias modificações.

## Agradecimento

Obrigado a todas as pessoas que testam, relatam problemas, sugerem melhorias e contribuem com software livre. Projetos assim só evoluem porque conhecimento e trabalho são compartilhados.
