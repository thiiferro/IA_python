document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chatForm");
    const inputMensagem = document.getElementById("inputMensagem");
    const inputImagem = document.getElementById("imagem");
    const mensagensContainer = document.querySelector(".mensagens textarea"); 
    const darkModeButton = document.getElementById("dark-mode-button");

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

        // Limpa o input imediatamente após pegar o valor
        inputMensagem.value = "";
        inputMensagem.focus();

        mensagensContainer.value += "Você: " + mensagemTexto + "\n";
        mensagensContainer.scrollTop = mensagensContainer.scrollHeight;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem: mensagemTexto })
            });

            if (!response.ok) {
                throw new Error("Erro ao obter resposta da IA.");
            }

            const data = await response.json();
            const respostaIA = data.resposta || "Não consegui entender sua solicitação.";

            mensagensContainer.value += "Megan: " + respostaIA + "\n";
            mensagensContainer.scrollTop = mensagensContainer.scrollHeight;

        } catch (error) {
            console.error("Erro:", error);
            mensagensContainer.value += "Erro ao obter resposta da IA.\n";
        }
    });
});
