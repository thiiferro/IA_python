README.md
markdown
Copiar
Editar
# ChatBot IA (Ana)

Este é um chatbot simples e interativo, utilizando a tecnologia de IA para conversar com os usuários. A IA é chamada **Ana**, e ela responde de forma amigável no mesmo idioma que o usuário utiliza. O projeto foi desenvolvido com HTML, CSS, JavaScript e Python (Flask) para o backend.

## Funcionalidades

- Interface de chat interativa.
- Respostas automáticas e em tempo real da IA.
- Detecção de idioma para que a IA responda no mesmo idioma que o usuário.
- Layout responsivo e design simples.
- Suporte a rolagem suave para o conteúdo do chat, sem barras de rolagem visíveis.

## Tecnologias Utilizadas

- **Frontend**: HTML, CSS, JavaScript.
- **Backend**: Python (Flask)

## Como Usar

### 1. Clone o Repositório

Primeiro, clone o repositório para o seu computador:

```bash
git clone https://github.com/seu-usuario/chatbot-ia.git
```

### 2. Instalar Dependências
Backend
Instale as dependências do Python para o backend:

```bash
pip install openai
pip install flask
```

Frontend
O frontend está pronto para ser usado. Não há dependências extras no momento para o frontend.


### 3. Rodar o Servidor
Backend (Python Flask)
Para rodar o servidor backend, execute o seguinte comando:

```bash
python app.py
O servidor estará disponível em http://127.0.0.1:5000/.
```

Frontend
Abra o arquivo index.html diretamente no navegador ou configure um servidor local (como o Live Server no VSCode) para ver o frontend em funcionamento.

### 4. Como Funciona
O usuário digita uma mensagem no campo de texto.
O frontend envia a mensagem para o backend através de uma requisição POST.
O backend detecta o idioma da mensagem do usuário e envia uma resposta adequada.
A IA (Ana) responde de forma amigável e no mesmo idioma que o usuário usou.
O chat exibe as mensagens de forma sequencial, uma abaixo da outra, com rolagem suave, sem barras visíveis.
Exemplo de Como a IA Responde
Usuário: Olá!

Ana: Olá! Como posso te ajudar hoje?

Usuário: Can you help me with coding?

Ana: Of course! What programming language are you using?

Personalização
Você pode personalizar a IA de diversas formas:

Texto da IA: Alterando as respostas diretamente no backend.
Design: Ajustando o CSS para personalizar a aparência da interface.
Linguagem: Se desejar, pode integrar a IA com outros serviços de tradução para melhorar as respostas em diferentes idiomas.
Contribuições
Contribuições são bem-vindas! Se você tiver sugestões de melhorias ou correções, fique à vontade para abrir uma issue ou pull request.

Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.


### Passos seguintes:

Para rodar o backend, o Flask deve estar instalado. Se não estiver, basta rodar:

```bash
pip install flask
```
