from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any

class ErroAplicacao(Exception):
    status_code = 400
    codigo = "ERRO"

    def __init__(
        self,
        mensagem: str,
        *,
        campo: str | None = None,
        codigo: str | None = None,
        detalhes: dict[str, Any] | None = None,
    ):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo
        self.detalhes = detalhes or {}
        if codigo:
            self.codigo = codigo


class NaoAutenticado(ErroAplicacao):
    status_code = 401
    codigo = "NAO_AUTENTICADO"


class AcessoNegado(ErroAplicacao):
    status_code = 403
    codigo = "ACESSO_NEGADO"


class NaoEncontrado(ErroAplicacao):
    status_code = 404
    codigo = "NAO_ENCONTRADO"


class Conflito(ErroAplicacao):
    status_code = 409
    codigo = "CONFLITO"


class RegraViolada(ErroAplicacao):
    status_code = 422  
    codigo = "REGRA_DE_NEGOCIO"


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroAplicacao)
    async def erro_aplicacao(_: Request, exc: ErroAplicacao) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "codigo": exc.codigo,
                "mensagem": exc.mensagem,
                "campo": exc.campo,
                "detalhes": exc.detalhes,
            },
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
        erros = [
            {
                "campo": ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path")),
                "mensagem": e["msg"],
                "tipo": e["type"],
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "VALIDACAO",
                "mensagem": "Há campos inválidos na requisição.",
                "campo": erros[0]["campo"] if erros else None,
                "erros": erros,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def erro_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Erros do próprio FastAPI, como rota inexistente (404) ou método errado (405)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "codigo": "ERRO_HTTP",
                "mensagem": str(exc.detail),
                "campo": None,
                "detalhes": {},
            },
        )