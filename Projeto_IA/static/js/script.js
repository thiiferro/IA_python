

// document.addEventListener("DOMContentLoaded", function () {
//     const form = document.getElementById("chatForm");
//     const inputMensagem = document.getElementById("inputMensagem");
//     const mensagensContainer = document.querySelector(".mensagens textarea"); 
//     const darkModeButton = document.getElementById("dark-mode-button");

//     // Ativar modo escuro se já estiver salvo no localStorage
//     if (localStorage.getItem("dark-mode") === "enabled") {
//         document.body.classList.add("dark-mode");
//     }

//     darkModeButton.addEventListener("click", function () {
//         document.body.classList.toggle("dark-mode");
//         localStorage.setItem("dark-mode", document.body.classList.contains("dark-mode") ? "enabled" : "disabled");
//     });

//     form.addEventListener("submit", async function (event) {
//         event.preventDefault();

//         const mensagemTexto = inputMensagem.value.trim();
//         if (!mensagemTexto) {
//             alert("Digite uma mensagem.");
//             return;
//         }

//         // Exibir mensagem do usuário no chat
//         adicionarMensagem("Você", mensagemTexto);
        
//         // Limpa o campo de entrada e mantém o foco
//         inputMensagem.value = "";
//         inputMensagem.focus();

//         // Iniciar resposta da IA com animação de bolinhas
//         await obterRespostaIA(mensagemTexto);
//     });

//     function adicionarMensagem(remetente, mensagem) {
//         mensagensContainer.value += `\n${remetente}: ${mensagem}\n`;
//         mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
//     }

//     async function obterRespostaIA(mensagemTexto) {
//         try {
//             const response = await fetch("/chat", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ mensagem: mensagemTexto })
//             });

//             if (!response.ok) {
//                 throw new Error("Erro ao obter resposta da IA.");
//             }

//             // Lê o corpo da resposta como um stream
//             const reader = response.body.getReader();
//             const decoder = new TextDecoder();

//             // Exibir animação de bolinhas enquanto a IA processa
//             let animacaoBolinhas = ["Megan: ", "Megan: .", "Megan: ..", "Megan: ..."];
//             let animacaoIndex = 0;
//             let bufferResposta = "";
//             let animacaoInterval = setInterval(() => {
//                 const linhas = mensagensContainer.value.split("\n");
//                 linhas[linhas.length - 1] = animacaoBolinhas[animacaoIndex % 4];
//                 mensagensContainer.value = linhas.join("\n") + "\n";
//                 mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
//                 animacaoIndex++;
//             }, 500);

//             mensagensContainer.value += "\nMegan: "; 
//             mensagensContainer.scrollTop = mensagensContainer.scrollHeight;

//             while (true) {
//                 const { value, done } = await reader.read();
//                 if (done) {
//                     clearInterval(animacaoInterval);
//                     break;
//                 }
//                 const chunk = decoder.decode(value, { stream: true });
//                 bufferResposta += chunk;
                
//                 const linhas = mensagensContainer.value.split("\n");
//                 linhas[linhas.length - 1] = `Megan: ${bufferResposta}`;
//                 mensagensContainer.value = linhas.join("\n") + "\n";
//                 mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
//             }
//         } catch (error) {
//             console.error("Erro:", error);
//             adicionarMensagem("Megan", "Erro ao obter resposta da IA.");
//         }
//     }
// });

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chatForm");
    const inputMensagem = document.getElementById("inputMensagem");
    const mensagensContainer = document.querySelector(".mensagens textarea"); 
    const darkModeButton = document.getElementById("dark-mode-button");
    const icon = darkModeButton.querySelector("i");

    // Ativar modo escuro se já estiver salvo no localStorage
    if (localStorage.getItem("dark-mode") === "enabled") {
        document.body.classList.add("dark-mode");
        icon.classList.remove("fa-moon-o");
        icon.classList.add("fa-sun-o");
    } else {
        icon.classList.remove("fa-sun-o");
        icon.classList.add("fa-moon-o");
    }

    darkModeButton.addEventListener("click", function () {
        const isDark = document.body.classList.toggle("dark-mode");

        if (isDark) {
            icon.classList.remove("fa-moon-o");
            icon.classList.add("fa-sun-o");
            localStorage.setItem("dark-mode", "enabled");
        } else {
            icon.classList.remove("fa-sun-o");
            icon.classList.add("fa-moon-o");
            localStorage.setItem("dark-mode", "disabled");
        }
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const mensagemTexto = inputMensagem.value.trim();
        if (!mensagemTexto) {
            alert("Digite uma mensagem.");
            return;
        }

        adicionarMensagem("Você", mensagemTexto);
        inputMensagem.value = "";
        inputMensagem.focus();
        await obterRespostaIA(mensagemTexto);
    });

    function adicionarMensagem(remetente, mensagem) {
        mensagensContainer.value += `\n${remetente}: ${mensagem}\n`;
        mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
    }

    async function obterRespostaIA(mensagemTexto) {
        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem: mensagemTexto })
            });

            if (!response.ok) throw new Error("Erro ao obter resposta da IA.");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let animacaoBolinhas = ["Megan: ", "Megan: .", "Megan: ..", "Megan: ..."];
            let animacaoIndex = 0;
            let bufferResposta = "";

            let animacaoInterval = setInterval(() => {
                const linhas = mensagensContainer.value.split("\n");
                linhas[linhas.length - 1] = animacaoBolinhas[animacaoIndex % 4];
                mensagensContainer.value = linhas.join("\n") + "\n";
                mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
                animacaoIndex++;
            }, 500);

            mensagensContainer.value += "\nMegan: "; 
            mensagensContainer.scrollTop = mensagensContainer.scrollHeight;

            while (true) {
                const { value, done } = await reader.read();
                if (done) {
                    clearInterval(animacaoInterval);
                    break;
                }
                const chunk = decoder.decode(value, { stream: true });
                bufferResposta += chunk;
                
                const linhas = mensagensContainer.value.split("\n");
                linhas[linhas.length - 1] = `Megan: ${bufferResposta}`;
                mensagensContainer.value = linhas.join("\n") + "\n";
                mensagensContainer.scrollTop = mensagensContainer.scrollHeight;
            }
        } catch (error) {
            console.error("Erro:", error);
            adicionarMensagem("Megan", "Erro ao obter resposta da IA.");
        }
    }
});
