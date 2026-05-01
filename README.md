# vanishd

Compartilhamento de secrets com links de uso único e criptografia zero-knowledge.

## O que é

vanishd permite enviar senhas, tokens e textos sensíveis de forma segura: o remetente gera um link que só pode ser aberto uma vez. Após a primeira leitura, o conteúdo é deletado permanentemente.

A criptografia acontece inteiramente no navegador (AES-256-GCM via Web Crypto API). O servidor armazena apenas o ciphertext — nunca tem acesso ao conteúdo em plaintext.

## Como funciona

1. Remetente digita o secret no navegador
2. O navegador cifra localmente e envia apenas o ciphertext ao servidor
3. Um link único é gerado — a chave de decifração viaja no fragment da URL (`#`), invisível ao servidor
4. Destinatário abre o link — o navegador decifra localmente e exibe o conteúdo
5. O servidor deleta o registro na primeira leitura — o link nunca funciona duas vezes

Existe também um modo senha: em vez da chave no link, o remetente define uma senha que o destinatário precisa digitar para decifrar.

## Status

Em desenvolvimento. Acompanhe o progresso pelas [milestones](https://github.com/NatanRigailo/vanishd/milestones) e [issues](https://github.com/NatanRigailo/vanishd/issues).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
