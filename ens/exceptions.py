class MaybeIsolated(Exception):
    pass


# Fetch
class FetchError(Exception):
    """@param reason"""


class RequestError(Exception):
    """当网络出现异常，这可能是由于以下原因

    - 连接超时
    - 服务器不可用

    @param reason
    """


class SourceNotFound(Exception):
    """当请求的数据不存在，这可能是由于以下原因
    
    - 小说不存在
    - 小说被删除
    - 章节不存在
    - 章节被删除
    - 章节未审核通过

    当抛出该异常时，将不再重试

    @param reason
    """

# Misc
class ExternalError(Exception):
    """当调用外部程序失败时
    @param ret_code
    """

class FeatureUnsupport(Exception):
    """@param feature"""
