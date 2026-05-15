"""
Schemas Pydantic v2 para validação rigorosa das respostas do Sabiá.

Cada chamada retorna JSON bruto -> Pydantic valida -> script aplica regras ->
Excel recebe limpo.

Política de erro: validação inválida deve interromper o fluxo; o caller pode
registrar o erro antes de lançar a exceção.
"""

from __future__ import annotations

import json as _json
from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


# ============================================================
# ENUMS / TIPOS RESTRITOS
# ============================================================

NOTAS_VALIDAS = {0, 40, 80, 120, 160, 200}


class NivelConfianca(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class StatusTema(str, Enum):
    VERIFICADO = "verificado"
    INFERIDO = "inferido"
    AUSENTE = "ausente"


class StatusOCR(str, Enum):
    OK = "ok"
    PARCIAL = "parcial"
    DEGRADADO = "degradado"


class GravidadeDesvio(str, Enum):
    LEVE = "leve"
    MEDIA = "media"
    GRAVE = "grave"


class TipoDesvioC1(str, Enum):
    ORTOGRAFIA = "ortografia"
    ACENTUACAO = "acentuacao"
    PONTUACAO = "pontuacao"
    CONCORDANCIA = "concordancia"
    REGENCIA = "regencia"
    CRASE = "crase"
    PARALELISMO = "paralelismo"
    REGISTRO = "registro"
    VOCABULARIO = "vocabulario"
    SINTAXE = "sintaxe"


class AbordagemTema(str, Enum):
    COMPLETA = "completa"
    TANGENCIAMENTO = "tangenciamento"
    FUGA_TOTAL = "fuga_total"


class ClassificacaoRepertorio(str, Enum):
    PRODUTIVO = "produtivo"
    BOLSO = "bolso"
    NAO_LEGITIMADO = "nao_legitimado"


class ProjetoTexto(str, Enum):
    CONSISTENTE = "consistente"
    COM_INDICIOS = "com_indicios"
    PREVISIVEL = "previsivel"
    AUSENTE = "ausente"


class Autoria(str, Enum):
    CONFIGURA = "configura"
    INDICIOS = "indicios"
    AUSENTE = "ausente"


class ArticulacaoInter(str, Enum):
    PLENA = "plena"
    CONSISTENTE = "consistente"
    MEDIANA = "mediana"
    INSUFICIENTE = "insuficiente"
    PRECARIA = "precaria"
    AUSENTE = "ausente"


class DiversidadeCoesiva(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class TipoInadequacaoCoesiva(str, Enum):
    CONECTOR_SEM_RELACAO = "conector_sem_relacao"
    EMPILHAMENTO = "empilhamento"
    REPETICAO_INADEQUADA = "repeticao_inadequada"
    PARAGRAFO_ISOLADO = "paragrafo_isolado"


# ============================================================
# BASE COMUM
# ============================================================


class RespostaCompetenciaBase(BaseModel):
    """Base para C1-C5: validação da nota oficial."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    competencia: str
    nota: int
    comentario: str = Field(..., min_length=10, max_length=2000)
    sugestao: str = Field(..., min_length=5, max_length=1500)
    nivel_confianca: NivelConfianca

    @field_validator("nota")
    @classmethod
    def nota_deve_estar_na_escala(cls, v: int) -> int:
        if v not in NOTAS_VALIDAS:
            raise ValueError(
                f"Nota {v} fora da escala oficial ENEM. Permitidas: {sorted(NOTAS_VALIDAS)}"
            )
        return v


# ============================================================
# GATE DE ANULAÇÃO
# ============================================================


class DetalhesAnulacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fuga_total_tema: bool = False
    nao_atendimento_tipo_textual: bool = False
    texto_insuficiente: bool = False
    parte_deliberadamente_desconectada: bool = False
    texto_em_lingua_estrangeira: bool = False
    texto_ilegivel: bool = False
    improperios_ou_anulacao_proposital: bool = False


class GateAnulacao(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    anulado: bool
    motivos: list[str] = Field(default_factory=list)
    detalhes: DetalhesAnulacao
    evidencia: Optional[str] = None
    nivel_confianca: NivelConfianca

    @model_validator(mode="after")
    def consistencia_anulado_x_detalhes(self) -> "GateAnulacao":
        algum_true = any(self.detalhes.model_dump().values())
        if self.anulado and not algum_true:
            raise ValueError(
                "anulado=True mas nenhum detalhe específico está True. Inconsistência."
            )
        if not self.anulado and algum_true:
            raise ValueError("Algum detalhe está True mas anulado=False. Inconsistência.")
        if self.anulado and not self.motivos:
            raise ValueError("anulado=True exige lista 'motivos' não vazia.")
        if self.anulado and not self.evidencia:
            raise ValueError("anulado=True exige campo 'evidencia' preenchido.")
        return self


# ============================================================
# C1 - MODALIDADE ESCRITA FORMAL
# ============================================================


class DesvioC1(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tipo: TipoDesvioC1
    trecho: str = Field(..., min_length=1, max_length=300)
    gravidade: GravidadeDesvio


class RespostaC1(RespostaCompetenciaBase):
    competencia: Literal["C1"] = "C1"
    desvios_encontrados: list[DesvioC1] = Field(default_factory=list)
    total_desvios: int = Field(..., ge=0)
    reincidencia: bool
    tipo_reincidente: Optional[TipoDesvioC1] = None

    @model_validator(mode="after")
    def consistencia_desvios(self) -> "RespostaC1":
        if len(self.desvios_encontrados) > self.total_desvios:
            raise ValueError(
                f"desvios_encontrados ({len(self.desvios_encontrados)}) "
                f"maior que total_desvios ({self.total_desvios})."
            )
        if self.reincidencia and self.tipo_reincidente is None:
            raise ValueError("reincidencia=True exige tipo_reincidente.")
        if not self.reincidencia and self.tipo_reincidente is not None:
            raise ValueError("tipo_reincidente preenchido mas reincidencia=False.")
        if self.nota == 200 and self.total_desvios > 2:
            raise ValueError(
                f"Nota 200 incompatível com {self.total_desvios} desvios "
                "(Cartilha: máx 1-2 excepcionalidades)."
            )
        return self


# ============================================================
# C2 - TEMA, TIPO TEXTUAL E REPERTÓRIO
# ============================================================


class Repertorio(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    referencia: str = Field(..., min_length=2, max_length=300)
    classificacao: ClassificacaoRepertorio
    justificativa: str = Field(..., min_length=5, max_length=500)


class RespostaC2(RespostaCompetenciaBase):
    competencia: Literal["C2"] = "C2"
    abordagem_tema: AbordagemTema
    tangenciamento_c2: bool
    alerta_tema: Optional[str] = None
    tipo_textual_adequado: bool
    repertorios_identificados: list[Repertorio] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistencia_c2(self) -> "RespostaC2":
        if self.abordagem_tema == AbordagemTema.FUGA_TOTAL and self.nota != 0:
            raise ValueError("Fuga total ao tema exige nota 0 em C2.")
        if self.abordagem_tema == AbordagemTema.TANGENCIAMENTO and self.nota > 40:
            raise ValueError(
                f"Tangenciamento em C2 exige nota máxima 40 (recebida: {self.nota})."
            )
        deveria_ser_tang = self.abordagem_tema == AbordagemTema.TANGENCIAMENTO
        if self.tangenciamento_c2 != deveria_ser_tang:
            raise ValueError(
                f"Flag tangenciamento_c2 ({self.tangenciamento_c2}) inconsistente "
                f"com abordagem_tema ({self.abordagem_tema})."
            )
        if not self.tipo_textual_adequado and self.nota > 0:
            raise ValueError("Tipo textual inadequado exige nota 0 em C2.")
        if self.nota == 200:
            tem_produtivo = any(
                r.classificacao == ClassificacaoRepertorio.PRODUTIVO
                for r in self.repertorios_identificados
            )
            if not tem_produtivo:
                raise ValueError(
                    "Nota 200 em C2 exige ao menos 1 repertório produtivo articulado."
                )
        return self


# ============================================================
# C3 - PROJETO DE TEXTO E ARGUMENTAÇÃO
# ============================================================


class RespostaC3(RespostaCompetenciaBase):
    competencia: Literal["C3"] = "C3"
    projeto_de_texto: ProjetoTexto
    tese_identificada: Optional[str] = Field(None, max_length=500)
    autoria: Autoria
    teto_por_tangenciamento_aplicado: bool

    @model_validator(mode="after")
    def consistencia_c3(self) -> "RespostaC3":
        if self.teto_por_tangenciamento_aplicado and self.nota > 40:
            raise ValueError(f"Teto por tangenciamento aplicado mas nota = {self.nota} (>40).")
        if self.nota == 200:
            if self.projeto_de_texto != ProjetoTexto.CONSISTENTE:
                raise ValueError("Nota 200 em C3 exige projeto_de_texto = 'consistente'.")
            if self.autoria != Autoria.CONFIGURA:
                raise ValueError("Nota 200 em C3 exige autoria = 'configura'.")
        if self.projeto_de_texto == ProjetoTexto.AUSENTE and self.nota > 40:
            raise ValueError("Projeto de texto ausente exige nota máxima 40 em C3.")
        return self


# ============================================================
# C4 - COESÃO E ARTICULAÇÃO
# ============================================================


class InadequacaoCoesiva(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tipo: TipoInadequacaoCoesiva
    trecho: str = Field(..., min_length=1, max_length=300)
    justificativa: Optional[str] = Field(None, max_length=500)


class RespostaC4(RespostaCompetenciaBase):
    competencia: Literal["C4"] = "C4"
    articulacao_interparagrafo: ArticulacaoInter
    diversidade_coesiva: DiversidadeCoesiva
    inadequacoes_identificadas: list[InadequacaoCoesiva] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistencia_c4(self) -> "RespostaC4":
        if self.nota == 200:
            if self.articulacao_interparagrafo != ArticulacaoInter.PLENA:
                raise ValueError(
                    "Nota 200 em C4 exige articulacao_interparagrafo = 'plena'."
                )
            if self.diversidade_coesiva != DiversidadeCoesiva.ALTA:
                raise ValueError("Nota 200 em C4 exige diversidade_coesiva = 'alta'.")
        if self.articulacao_interparagrafo == ArticulacaoInter.AUSENTE and self.nota > 0:
            raise ValueError("Articulação ausente exige nota 0 em C4.")
        return self


# ============================================================
# C5 - PROPOSTA DE INTERVENÇÃO
# ============================================================


class ElementosProposta(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    agente: Optional[str] = Field(None, max_length=300)
    acao: Optional[str] = Field(None, max_length=500)
    meio: Optional[str] = Field(None, max_length=500)
    efeito: Optional[str] = Field(None, max_length=500)
    detalhamento: Optional[str] = Field(None, max_length=500)


class RespostaC5(RespostaCompetenciaBase):
    competencia: Literal["C5"] = "C5"
    elementos_identificados: ElementosProposta
    total_elementos: int = Field(..., ge=0, le=5)
    articulacao_com_texto: bool
    respeita_direitos_humanos: bool
    teto_por_tangenciamento_aplicado: bool

    @model_validator(mode="after")
    def consistencia_c5(self) -> "RespostaC5":
        elementos_dict = self.elementos_identificados.model_dump()
        count_real = sum(1 for v in elementos_dict.values() if v)
        if count_real != self.total_elementos:
            raise ValueError(
                f"total_elementos ({self.total_elementos}) não bate com "
                f"elementos preenchidos ({count_real})."
            )
        if not self.respeita_direitos_humanos and self.nota > 0:
            raise ValueError("Proposta que fere direitos humanos exige nota 0 em C5.")
        if self.teto_por_tangenciamento_aplicado and self.nota > 40:
            raise ValueError(f"Teto por tangenciamento aplicado mas nota = {self.nota} (>40).")
        if self.nota == 200 and self.total_elementos < 5:
            raise ValueError(
                f"Nota 200 em C5 exige 5 elementos (recebido: {self.total_elementos})."
            )
        if self.nota == 160 and self.total_elementos < 4:
            raise ValueError(
                f"Nota 160 em C5 exige ao menos 4 elementos (recebido: {self.total_elementos})."
            )
        if not self.articulacao_com_texto and self.nota > 80:
            raise ValueError("Proposta sem articulação com texto exige nota máxima 80.")
        return self


# ============================================================
# RESULTADO CONSOLIDADO
# ============================================================


class MetadadosRedacao(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id_redacao: str = Field(..., min_length=1, max_length=100)
    aluno_nome: Optional[str] = None
    aluno_escola: Optional[str] = None
    tema: str = Field(..., min_length=3, max_length=500)
    status_tema: StatusTema
    status_ocr: StatusOCR
    num_linhas: int = Field(..., ge=0, le=50)
    data_correcao: datetime = Field(default_factory=datetime.now)


class ResultadoCorrecao(BaseModel):
    """
    Resultado final após:
    1. Gate de anulação
    2. Avaliação das 5 competências
    3. Aplicação de tetos por tangenciamento
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    metadados: MetadadosRedacao
    anulada: bool
    gate: GateAnulacao
    tangenciamento: bool

    c1: RespostaC1
    c2: RespostaC2
    c3: RespostaC3
    c4: RespostaC4
    c5: RespostaC5

    nota_final: int = Field(..., ge=0, le=1000)
    confianca_geral: NivelConfianca
    alertas: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistencia_final(self) -> "ResultadoCorrecao":
        soma = self.c1.nota + self.c2.nota + self.c3.nota + self.c4.nota + self.c5.nota
        if soma != self.nota_final:
            raise ValueError(
                f"nota_final ({self.nota_final}) != soma das competências ({soma})."
            )
        if self.anulada:
            if any(c.nota != 0 for c in [self.c1, self.c2, self.c3, self.c4, self.c5]):
                raise ValueError("Redação anulada, mas alguma competência tem nota > 0.")
        if self.anulada != self.gate.anulado:
            raise ValueError(
                f"Inconsistência: anulada={self.anulada} mas gate.anulado={self.gate.anulado}."
            )
        if self.tangenciamento:
            if self.c3.nota > 40:
                raise ValueError("Tangenciamento mas C3 > 40.")
            if self.c5.nota > 40:
                raise ValueError("Tangenciamento mas C5 > 40.")
            if not self.c3.teto_por_tangenciamento_aplicado:
                raise ValueError("Tangenciamento detectado mas C3 não marca teto aplicado.")
            if not self.c5.teto_por_tangenciamento_aplicado:
                raise ValueError("Tangenciamento detectado mas C5 não marca teto aplicado.")
        if self.tangenciamento != self.c2.tangenciamento_c2:
            raise ValueError("tangenciamento global inconsistente com c2.tangenciamento_c2.")
        return self

    @property
    def nivel_proficiencia(self) -> str:
        """Classificação ENEM padrão."""
        n = self.nota_final
        if n < 500:
            return "Insuficiente"
        if n < 700:
            return "Regular"
        if n < 850:
            return "Bom"
        return "Excelente"


# ============================================================
# UTILITÁRIOS DE VALIDAÇÃO
# ============================================================


SCHEMA_POR_ETAPA: dict[str, type[BaseModel]] = {
    "gate": GateAnulacao,
    "c1": RespostaC1,
    "c2": RespostaC2,
    "c3": RespostaC3,
    "c4": RespostaC4,
    "c5": RespostaC5,
}


def schema_for_etapa(etapa: str) -> type[BaseModel]:
    etapa_normalizada = etapa.strip().lower()
    try:
        return SCHEMA_POR_ETAPA[etapa_normalizada]
    except KeyError as exc:
        raise ValueError(f"Etapa sem schema Pydantic: {etapa}") from exc


def parse_resposta_sabia(
    json_bruto: str | dict,
    schema: type[BaseModel],
) -> tuple[Optional[BaseModel], Optional[str]]:
    """
    Parsing seguro de resposta do Sabiá.

    Returns:
        (instancia_validada, None) em caso de sucesso
        (None, mensagem_erro_formatada) em caso de falha
    """
    try:
        if isinstance(json_bruto, str):
            dados = _json.loads(json_bruto)
        else:
            dados = json_bruto
        instancia = schema.model_validate(dados)
        return instancia, None
    except _json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"
    except ValidationError as e:
        erros = []
        for err in e.errors():
            campo = ".".join(str(p) for p in err["loc"])
            erros.append(f"{campo}: {err['msg']}")
        return None, " | ".join(erros)
    except Exception as e:
        return None, f"Erro inesperado: {type(e).__name__}: {e}"
