document.addEventListener("DOMContentLoaded", () => {
    // Seleciona os elementos
    const form = document.getElementById("chatForm");
    const inputMensagem = document.querySelector("#inputMensagem");
    const mensagensContainer = document.querySelector(".mensagens .chatbot");
    const darkModeButton = document.getElementById("dark-mode-button");

    // Verificações de segurança para evitar null
    if (!form) {
        console.error("Elemento com ID 'chatForm' não encontrado no HTML.");
        return;
    }
    if (!inputMensagem) {
        console.error("Elemento com ID 'inputMensagem' não encontrado no HTML.");
        return;
    }
    if (!mensagensContainer) {
        console.error("Elemento '.mensagens .chatbot' não encontrado no HTML.");
        return;
    }
    if (!darkModeButton) {
        console.error("Elemento com ID 'dark-mode-button' não encontrado no HTML.");
        return;
    }

    // Ativar modo escuro se já estiver salvo no localStorage
    if (localStorage.getItem("dark-mode") === "enabled") {
        document.body.classList.add("dark-mode");
    }

    // Evento para alternar entre modos claro e escuro
    darkModeButton.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        darkModeButton.classList.toggle("dark");
        localStorage.setItem("dark-mode", document.body.classList.contains("dark-mode") ? "enabled" : "disabled");
    });

    // Adiciona evento de envio ao formulário
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const mensagemTexto = inputMensagem.value.trim();
        if (!mensagemTexto) {
            alert("Digite uma mensagem.");
            return;
        }

        // Exibe a mensagem do usuário
        adicionarMensagem("Você", mensagemTexto);

        // Limpa o campo de entrada e mantém o foco
        inputMensagem.value = "";
        inputMensagem.focus();

        // Envia a mensagem ao backend e obtém a resposta
        await obterRespostaIA(mensagemTexto);
    });

    // Função para adicionar mensagens na div de chat
    function adicionarMensagem(remetente, mensagem) {
        const mensagemDiv = document.createElement("div");
        mensagemDiv.classList.add("row");
        mensagemDiv.innerHTML = `<strong>${remetente}:</strong> ${mensagem}`;
        mensagensContainer.appendChild(mensagemDiv);
        mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
    }

    // Função para enviar mensagem ao backend e tratar a resposta
    async function obterRespostaIA(mensagemTexto) {
        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem: mensagemTexto })
            });

            if (!response.ok) {
                throw new Error("Erro ao obter resposta da IA.");
            }

            // Lê a resposta como texto simples
            const respostaIA = await response.text();
            adicionarMensagem("Megan", respostaIA);
        } catch (error) {
            console.error("Erro:", error);
            adicionarMensagem("Megan", "Erro ao obter resposta da IA.");
        }
    }
});
