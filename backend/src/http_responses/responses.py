from enum import IntEnum
from flask import jsonify, Response
from typing import Any


class HttpStatus(IntEnum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


def success(data: Any = None, message: str | None = None) -> tuple[Response, int]:
    if message:
        return jsonify({"message": message, "data": data}), HttpStatus.OK
    return jsonify(data), HttpStatus.OK


def created(data: Any = None, message: str | None = None) -> tuple[Response, int]:
    if message:
        return jsonify({"message": message, "data": data}), HttpStatus.CREATED
    return jsonify(data), HttpStatus.CREATED


def no_content() -> tuple[str, int]:
    return "", HttpStatus.NO_CONTENT


def bad_request(message: str = "Bad request") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.BAD_REQUEST


def unauthorized(message: str = "Unauthorized") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.UNAUTHORIZED


def forbidden(message: str = "Forbidden") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.FORBIDDEN


def not_found(message: str = "Not found") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.NOT_FOUND


def conflict(message: str = "Conflict") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.CONFLICT


def unprocessable_entity(message: str = "Unprocessable entity") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.UNPROCESSABLE_ENTITY


def internal_server_error(message: str = "Internal server error") -> tuple[Response, int]:
    return jsonify({"message": message}), HttpStatus.INTERNAL_SERVER_ERROR

