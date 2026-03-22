# StackRadar

Montei o StackRadar porque precisava de um jeito decente de saber o que o mercado de TI está realmente pedindo. Ficar scrollando vaga por vaga no LinkedIn não escala.

O aplicativo bate na plataforma de vagas do Mercado Livre (no sistema da Eightfold), puxa todas as posições que tenham "software" no título e salva tudo num banco SQLite local. A partir daí, a interface gera um ranking instantâneo das ferramentas e linguagens que mais aparecem na gringa ou aqui, listando coisas como Java, Go ou Python. Tudo envelopado num visual preto sólido.

A aba de Chat transforma os dados numa conversa de fato. Você digita uma pergunta e a ferramenta lê as descrições das vagas locais para tentar achar a resposta. A integração roda em cima do Ollama. Se você configurar a instalação completa com suporte a RAG, ele levanta o ChromaDB com embeddings e faz buscas semânticas profundas. Se a sua máquina ou conexão não colaborarem para baixar GBs de tensores, a instalação padrão ignora o RAG e continua respondendo através de buscas simples por palavras-chave. Funciona dos dois jeitos.

## Como rodar localmente

Eu uso `uv` porque gerenciar `pip` e `.venv` manualmente hoje em dia é perda de tempo.

1. Baixe o código.
2. Na raiz do projeto, instale as dependências:

```bash
uv sync
```

Se quiser a versão completa com RAG semântico, use:

```bash
uv sync --extra rag
```

_(Aviso da trincheira: O pacote do tokenizers costuma quebrar compilações no Python 3.13+ no Windows devido à ausência de rodas binárias. Use o Python 3.12 ou aceite a dor de cabeça do compilador Rust.)_

3. Execute:

```bash
uv run python -m stackradar
```

## Configurar o Chat (Ollama)

O chat consome a API do Ollama na sua própria rede.

1. Instale o aplicativo Ollama no seu sistema.
2. Puxe um modelo bom para código no terminal, recomendo o Qwen (exemplo: `ollama pull qwen2.5:9b`).
3. Abra o StackRadar, vá no Dashboard e clique em **Atualizar vagas**. Isso abastece o banco SQLite na pasta oculta `%USERPROFILE%\.stackradar\vagas.db`.
4. Mude para a aba Chat IA, configure a lateral com o nome do seu modelo e pergunte o que quiser.

## Testes

Tem uma rotina básica de testes para garantir as validações de UI e scraping:

```bash
uv sync --extra dev
uv run pytest tests/
```

O `pyproject.toml` já possui as configurações prontas do PyInstaller. Tem também um script em powershell na raiz para empacotar o executável do Windows injetando o nosso ícone customizado de radar.
