// pede os dados pro flask e joga no tabulator
// Ainda tô aprendendo

const mensagemEl = document.getElementById("mensagem");
const campoBusca = document.getElementById("campo-busca");
const formBusca = document.getElementById("form-busca");
const btnLimpar = document.getElementById("btn-limpar");
const totalAgendamentosEl = document.getElementById("total-agendamentos");
const totalConfirmadosEl = document.getElementById("total-confirmados");

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

// Atualiza os contadores com base na lista que está na tela 
function atualizarResumo(lista) {
  const total = lista.length;
  // Conta só os que tem status "Confirmado" 
  let confirmados = 0;
  for (let i = 0; i < lista.length; i++) {
    const status = (lista[i].status || "").toLowerCase();
    if (status === "confirmado") {
      confirmados = confirmados + 1;
    }
  }
  totalAgendamentosEl.textContent = String(total);
  totalConfirmadosEl.textContent = String(confirmados);
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
      atualizarResumo([]);
      tabela.options.placeholder = "Não foi possível carregar os dados.";
      return;
    }

    const lista = data.agendamentos || [];
    tabela.setData(lista);
    atualizarResumo(lista);

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
    atualizarResumo([]);
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
