// JavaScript da agenda: pede os dados pro flask e joga no tabulator.
// Ainda tô aprendendo — deixei bem direto o passo a passo.

const mensagemEl = document.getElementById("mensagem");
const campoBusca = document.getElementById("campo-busca");
const formBusca = document.getElementById("form-busca");
const btnLimpar = document.getElementById("btn-limpar");

// Cria a tabela vazia, os dados entram depois do fetch
const tabela = new Tabulator("#tabela-agenda", {
  data: [],
  layout: "fitColumns",
  placeholder: "Carregando...",
  columns: [
    { title: "Data", field: "data" },
    { title: "Horário", field: "horario" },
    { title: "Paciente", field: "paciente" },
    { title: "CPF", field: "cpf" },
    { title: "Médico", field: "medico" },
    { title: "Especialidade", field: "especialidade" },
    { title: "Convênio", field: "convenio" },
    { title: "Status", field: "status" },
  ],
});

// Mostra ou limpa o texto embaixo da busca.
// Se ehErro for true, deixa a mensagem vermelha.
function mostrarMensagem(texto, ehErro) {
  mensagemEl.textContent = texto || "";
  if (ehErro) {
    mensagemEl.classList.add("erro");
  } else {
    mensagemEl.classList.remove("erro");
  }
}

// Traduz o código "motivo" que veio do Flask 
// Se não tiver motivo (lista com dados), devolve string vazia.
function mensagemDoMotivo(motivo) {
  if (motivo === "agenda_vazia") {
    return "Não há agendamentos disponíveis.";
  }
  if (motivo === "sem_resultado_busca") {
    return "Nenhum registro foi encontrado.";
  }
  return "";
}

// Pede os agendamentos pro Flask (/api/agendamentos).
// q = texto da busca (pode ser vazio pra trazer a lista toda)
// Depois preenche o Tabulator e atualiza a mensagem na tela
async function carregarAgendamentos(q) {
  // Monta a URL: com ou sem q=
  let url = "/api/agendamentos";
  if (q && q.trim() !== "") {
    url = url + "?q=" + encodeURIComponent(q.trim());
  }

  mostrarMensagem("Carregando...", false);

  try {
    const resp = await fetch(url, {
      headers: { Accept: "application/json" },
    });
    const data = await resp.json();

    // Contrato: success true/false
    if (!data.success) {
      // api_indisponivel, resposta_invalida, etc.
      mostrarMensagem(
        "Não foi possível carregar os agendamentos. Tente novamente.",
        true
      );
      tabela.setData([]);
      tabela.options.placeholder = "Não foi possível carregar os dados.";
      return;
    }

    const lista = data.agendamentos || [];
    tabela.setData(lista);

    const textoMotivo = mensagemDoMotivo(data.motivo);
    if (textoMotivo) {
      mostrarMensagem(textoMotivo, false);
      tabela.options.placeholder = textoMotivo;
    } else {
      mostrarMensagem("", false);
      tabela.options.placeholder = "Sem dados";
    }
  } catch (err) {
    // Erro de rede no próprio navegador, ou JSON quebrado
    console.error(err);
    mostrarMensagem(
      "Não foi possível carregar os agendamentos. Tente novamente.",
      true
    );
    tabela.setData([]);
  }
}

// Quando a página abre, carrega tudo (sem filtro)
carregarAgendamentos("");

// Quando a pessoa clica em "Buscar" (submit do formulário)
formBusca.addEventListener("submit", function (evento) {
  evento.preventDefault(); // não recarrega a página
  carregarAgendamentos(campoBusca.value);
});

// Quando a pessoa clica em "Limpar" zera o campo e recarrega a lista toda
btnLimpar.addEventListener("click", function () {
  campoBusca.value = "";
  carregarAgendamentos("");
});
