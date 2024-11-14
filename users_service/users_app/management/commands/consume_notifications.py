from django.core.management.base import BaseCommand
import asyncio

from users_kafka_module.async_kafka_consumer import consume_profile_notifications, consume_post_notifications


class Command(BaseCommand):
    help = "Start profile and post consuming"

    @staticmethod
    async def handle_async(*args, **kwargs):
        task1 = asyncio.create_task(consume_profile_notifications())
        task2 = asyncio.create_task(consume_post_notifications())

        await task1
        await task2

    def handle(self, *args, **kwargs):
        asyncio.run(self.handle_async(*args, **kwargs))
