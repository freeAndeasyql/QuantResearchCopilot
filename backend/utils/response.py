# 统一成功响应
# code：业务状态码，这里成功统一使用 200
# message：提示信息
# data：真正返回给前端的数据
def success_response(data=None, message: str = "success"):
    return {
        "code": 200,
        "message": message,
        "data": data,
    }

# 统一错误响应
# code：错误状态码，比如 404、500
# message：错误提示信息
# data：错误时通常返回 None
def error_response(code: int = 500, message: str = "error", data=None):
    return {
        "code": code,
        "message": message,
        "data": data,
    }