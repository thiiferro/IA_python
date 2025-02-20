document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chatForm");
    const inputMensagem = document.getElementById("inputMensagem");
    const mensagensContainer = document.querySelector(".mensagens textarea"); 
    const darkModeButton = document.getElementById("dark-mode-button");

    // Ativar modo escuro se já estiver salvo no localStorage
    if (localStorage.getItem("dark-mode") === "enabled") {
        document.body.classList.add("dark-mode");
    }

    darkModeButton.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");
        localStorage.setItem("dark-mode", document.body.classList.contains("dark-mode") ? "enabled" : "disabled");
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const mensagemTexto = inputMensagem.value.trim();
        if (!mensagemTexto) {
            alert("Digite uma mensagem.");
            return;
        }

        // Exibir mensagem do usuário no chat
        adicionarMensagem("Você", mensagemTexto);
        
        // Limpa o campo de entrada e mantém o foco
        inputMensagem.value = "";
        inputMensagem.focus();

        // Iniciar resposta da IA
        await obterRespostaIA(mensagemTexto);
    });

    function adicionarMensagem(remetente, mensagem) {
        mensagensContainer.value += `${remetente}: ${mensagem}\n`;
        mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
    }

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

            // Lê o corpo da resposta como um stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            // Adiciona "Megan" antes de começar a mostrar a resposta
            adicionarMensagem("Megan", "");

            let bufferResposta = "";  // Para armazenar a resposta parcial
            while (true) {
                const { value, done } = await reader.read();
                if (done) {
                    break;
                }
                const chunk = decoder.decode(value, { stream: true });
                bufferResposta += chunk;
                
                // Atualiza a última linha de "Megan" com o conteúdo parcial
                // 1. Remove a última linha (placeholder vazio da Megan)
                const linhas = mensagensContainer.value.split("\n");
                linhas.pop(); // remove a linha vazia
                
                // 2. Adiciona novamente a linha com o conteúdo parcial
                linhas.push(`Megan: ${bufferResposta}`);

                // 3. Atualiza o textarea
                mensagensContainer.value = linhas.join("\n") + "\n";
                mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
            }

        } catch (error) {
            console.error("Erro:", error);
            adicionarMensagem("Megan", "Erro ao obter resposta da IA.");
        }
    }
});
