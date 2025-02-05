document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.querySelector(".chatbot");
    const inputMensagem = document.querySelector(".chat");
    const btnEnviar = document.querySelector(".btn-enviar");

    async function enviarMensagem(event) {
        event.preventDefault();

        let mensagem = inputMensagem.value.trim();
        if (!mensagem) return; // Evita mensagens vazias

        // Exibe a mensagem do usuário
        chatBox.value += `Você: ${mensagem}\n\n`;
        inputMensagem.value = "";

        try {
            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem })
            });

            let data = await response.json();
            console.log("Resposta recebida:", data);  // Depuração para ver no console

            if (data.resposta) {
                chatBox.value += `Megan: ${data.resposta}\n\n`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                chatBox.value += "Erro: Resposta vazia da IA.\n\n";
            }
        } catch (error) {
            console.error("Erro ao enviar mensagem:", error);
            chatBox.value += "Erro ao se comunicar com o servidor.\n\n";
        }
    }

    btnEnviar.addEventListener("click", enviarMensagem);
});
