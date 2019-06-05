import asyncio
import aiohttp
import aiofiles


class ExecuteError(Exception):
    def __init__(self, message):
        self.message = message

class Task():
    """任务对象"""

    def __init__(self, func, args=(), kw={}):
        """接受函数与参数以初始化对象"""

        self.func = func
        self.args = args
        self.kw = kw

    def run(self):
        """执行函数
        同步函数直接执行并返回结果，异步函数返回该函数
        """

        result = self.func(*self.args, **self.kw)
        return result

    async def execute(self):
        """在异步方法下执行函数（异步同步函数均可）"""

        if not callable(self.func):
            raise ExecuteError('{} is not a function'.format(self.func))
        try:
            await self.func(*self.args)
        except TypeError:
            await asyncio.sleep(0.001)

class Coroutine(object):
    """协程控制器

    用来启动和控制协程
    """
    def __init__(self):
        try:
            import uvloop
        except ImportError:
            print("no install uvloop package")
        else:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        finally:
            self._loop = asyncio.get_event_loop()

    def __del__(self):
        """析构，销毁_loop"""
        self._loop.close()

    def set_task(self, todo):
        """设置协程任务"""
        if isinstance(todo, list):
            self.task = asyncio.wait(todo)
        else:
            self.task = asyncio.ensure_future(todo)

    def run(self):
        """启动协程"""
        self._loop.run_until_complete(self.task)

    def sync(self, todo):
        """放弃异步，以同步方式即时执行单件异步事件"""
        result = self._loop.run_until_complete(asyncio.ensure_future(todo))
        return result
