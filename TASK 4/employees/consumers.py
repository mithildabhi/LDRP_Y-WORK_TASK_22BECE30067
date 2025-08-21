import json
import datetime
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from motor.motor_asyncio import AsyncIOMotorClient
from django.conf import settings

from .models import Employee

class DepartmentChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get employee_id from query params
        query = parse_qs(self.scope["query_string"].decode())
        employee_id = query.get("employee_id", [None])[0]

        # Find employee and department
        employee = await self._get_employee(employee_id)
        if not employee:
            await self.close()
            return

        self.employee_id = employee.id
        self.employee_name = employee.name
        self.group_name = str(employee.department_id)   # department PK = group name

        # Setup MongoDB connection
        self.mongo = AsyncIOMotorClient(settings.MONGO_URL)
        self.messages = self.mongo[settings.MONGO_DB][settings.MONGO_COLL]

        # Join department group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        self.mongo.close()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        text = data.get("text", "")

        doc = {
            "group": self.group_name,              # partition key
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "text": text,
            "timestamp": datetime.datetime.utcnow(),
        }

        # Save in MongoDB
        await self.messages.insert_one(doc)

        # Broadcast to everyone in this department
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "payload": doc},
        )

    async def chat_message(self, event):
        doc = event["payload"]
        doc["timestamp"] = doc["timestamp"].isoformat()
        await self.send(text_data=json.dumps(doc))

    @database_sync_to_async
    def _get_employee(self, emp_id):
        try:
            return Employee.objects.get(pk=emp_id)
        except Employee.DoesNotExist:
            return None
