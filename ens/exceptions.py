class MaybeIsolated(Exception):
    pass

class RequestError(Exception):
    """当网络出现异常，这可能是由于以下原因

    - 连接超时
    - 服务器不可用

    @param reason
    """

# Misc
class ExternalError(Exception):
    """当调用外部程序失败时
    @param ret_code
    """
    def __str__(self) -> str:
        return f'外部程序运行失败，返回值 {self.args[0]}'

class FeatureUnsupport(Exception):
    """@param feature"""
    def __str__(self) -> str:
        return f'该功能不支持或无法运行，请检查 `DO_{self.args[0].upper()}` 配置项'

class Abort(BaseException):
    pass
