import asyncio

from .utils import Task, Coroutine


class Loop_async():
    """异步循环对象"""

    def __init__(self, interval):
        """初始化并设间隔时间"""

        self.interval = interval
        self.events = []

    def on(self, task, action):
        self.events.append((task, action))

    async def event_response(self, event):
        while True:
            task, action = event
            resp = await task.execute()
            if resp:
                await action.execute()
            await asyncio.sleep(self.interval)

    async def run(self):
        """异步执行所有任务"""

        coroutine = Coroutine()
        coroutine.set_task([self.event_response(event) for event in self.events])
        coroutine.run()
