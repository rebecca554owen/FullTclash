import asyncio

import aiohttp
import async_timeout
from aiohttp import ClientConnectorError
from loguru import logger


# collector section
async def fetch_tiktok(collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    tiktok解锁测试,检查测速是否被ban
    :param collector:
    :param reconnection:
    :param session:
    :param proxy:
    :return:
    """
    tiktokurl = 'https://www.tiktok.com'
    try:
        conn = session.connector
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession(timeout=10, connector=conn) as session:
                async with session.get(tiktokurl, proxy=proxy, timeout=5) as resp:
                    if resp.status == 200:
                        response_text = await resp.text()
                        region = response_text.find('"region":')
                        if region != -1:
                            region = response_text[region:].split('"')[3]
                            # print("Tiktok Region: ", region)
                            collector.info['tiktok'] = f"解锁({region})"
                        else:
                            # print("Tiktok Region: Not found")
                            collector.info['tiktok'] = "失败"
                    else:
                        collector.info['tiktok'] = "未知"
    except ClientConnectorError as c:
        logger.warning("tiktok请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_tiktok(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
        else:
            collector.info['tiktok'] = "连接错误"
    except asyncio.exceptions.TimeoutError:
        logger.warning("tiktok请求超时，正在重新发送请求......")
        if reconnection != 0:
            await fetch_tiktok(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
        else:
            collector.info['tiktok'] = "超时"


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_tiktok(Collector, session, proxy=proxy))


# cleaner section
def get_tiktok_info(ReCleaner):
    """
    获取tiktok解锁信息
    :return: str: 解锁信息: [解锁、失败、N/A]
    """
    try:
        if 'tiktok' not in ReCleaner.data:
            logger.warning("采集器内无数据")
            return "N/A"
        else:
            # logger.info("tiktok解锁：" + str(ReCleaner.data.get('tiktok', "N/A")))
            return ReCleaner.data.get('tiktok', "N/A")
    except Exception as e:
        logger.error(e)
        return "N/A"


SCRIPT = {
    "MYNAME": "Tiktok",
    "TASK": task,
    "GET": get_tiktok_info
}

if __name__ == "__main__":
    async def demo():
        class FakeColl:
            def __init__(self):
                self.info = {}
                self.data = self.info

        fakecl = FakeColl()
        from aiohttp_socks import ProxyConnector
        # conn = ProxyConnector(host="127.0.0.1", port=11112, limit=0)
        # session = aiohttp.ClientSession(connector=conn)
        session = aiohttp.ClientSession()
        await fetch_tiktok(fakecl, session, proxy=None)
        print(fakecl.info)
        await session.close()


    if __name__ == "__main__":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(demo())
