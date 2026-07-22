# Cliente HTTP: o app web chama a mock_api daqui
# também valida se cada agendamento veio com os campos obrigatórios

import logging

import requests

logger = logging.getLogger(__name__)

# Campos exigidos em cada agendamento que a API deve devolver
REQUIRED = (
    "paciente",
    "cpf",
    "medico",
    "especialidade",
    "data",
    "horario",
    "convenio",
    "status",
)


class ApiResult:
    # Resultado simples: deu certo? quais itens? qual erro?
    def __init__(self, ok, items=None, error_code=None):
        self.ok = ok
        self.items = items if items is not None else []
        self.error_code = error_code


def _campo_faltando(valor):
    # None ou string vazia (depois do strip) conta como "não tem"
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip() == "":
        return True
    return False


def sanitize_items(raw):
    
    # se raw não for lista => None
    # se for lista → devolve só os itens completos (os ruins a gente descarta).
    
    if not isinstance(raw, list):
        return None

    validos = []
    for item in raw:
        if not isinstance(item, dict):
            logger.warning("Item descartado: não é um objeto")
            continue

        faltou = False
        for chave in REQUIRED:
            if chave not in item or _campo_faltando(item.get(chave)):
                faltou = True
                break

        if faltou:
            logger.warning("Item descartado: campo obrigatório ausente")
            continue

        # guarda só os campos que precisa
        limpo = {}
        for chave in REQUIRED:
            limpo[chave] = item[chave]
        validos.append(limpo)

    return validos


def fetch_agendamentos(base_url, timeout):
    # chama GET {base_url}/agendamentos e devolve um ApiResult.
    url = base_url.rstrip("/") + "/agendamentos"

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()

        try:
            payload = resp.json()
        except ValueError:
            # Corpo não é JSON (ex: MOCK_MODE=malformed)
            logger.exception("Resposta malformed da API")
            return ApiResult(ok=False, error_code="resposta_invalida")

        items = sanitize_items(payload)
        if items is None:
            # JSON ok, mas não era uma lista (ex.: MOCK_MODE=invalid)
            logger.error("Shape inválido da API")
            return ApiResult(ok=False, error_code="resposta_invalida")

        return ApiResult(ok=True, items=items)

    except (requests.ConnectionError, requests.Timeout) as exc:
        logger.error("API indisponível: %s", exc)
        return ApiResult(ok=False, error_code="api_indisponivel")
    except requests.RequestException as exc:
        logger.error("Falha HTTP na API: %s", exc)
        return ApiResult(ok=False, error_code="api_indisponivel")
