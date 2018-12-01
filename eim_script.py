'''
用于响应来自scratch EIM的消息请求
目标是易用性，将Python作为Scratch的扩展
'''

def handle(data,logger):
    '''
    参数
        data: 来自EIM send过来的消息，通常是字符串 也可以是数字、列表或json
        logger: 可帮助用户调试: https://scratch3-adapter-docs.just4fun.site/dev_guide/debug/
    返回值
        返回值将作为EIM接收到的内容
    '''
    logger.info(data)
    if type(data) == str:
        return data + ' from script'

    