import json
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from loguru import logger
from users.helpers.errors.error import AppError

class GlobalExceptionMiddleware(MiddlewareMixin):
    """
    Middleware que intercepta exceções, registra logs e devolve resposta JSON segura.
    Não exibe stacktraces para o cliente — apenas um 'safe_message'.
    """

    def process_exception(self, request, exception):
        # Se for um AppError já conhecido, usamos seus dados
        if isinstance(exception, AppError):
            logger.warning(
                "Handled AppError: {} {} {}",
                exception.code,
                exception.safe_message,
                {"extra": exception.extra, "path": request.path},
            )
            payload = {
                "error": {
                    "code": exception.code,
                    "message": exception.safe_message,
                }
            }
            if exception.extra:
                # inclui extra com cuidado (não colocar dados sensíveis)
                payload["error"]["details"] = exception.extra
            return JsonResponse(payload, status=exception.status_code)

        # Para outros erros, registamos com detalhe e retornamos mensagem genérica
        tb = traceback.format_exc()
        logger.exception("Unhandled exception on request {}: {}", request.path, tb)

        payload = {
            "error": {
                "code": "internal_server_error",
                "message": "Ocorreu um erro interno. A equipa já foi notificada.",
            }
        }
        return JsonResponse(payload, status=500)
