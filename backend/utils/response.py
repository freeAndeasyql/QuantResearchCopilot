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