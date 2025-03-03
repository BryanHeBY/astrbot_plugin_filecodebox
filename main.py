from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import requests

@register("filecodebox", "BryanHe", "FileCodeBox配套插件", "1.0.0", "https://github.com/BryanHeBY/astrbot_plugin_filecodebox")
class FileCodeBox(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.url = config.get("filecodebox_url")
    
    @filter.command("send")
    async def send(self, event: AstrMessageEvent):
        '''这是发送文件的指令''' 
        message_str = event.message_str # 用户发的纯文本消息字符串
        form_data = {
            "text": message_str,
            "expire_value": 1,
            "expire_style": "day"
        }
        r = requests.post(
            url=f"{self.url}/share/text/",
            data=form_data)
        r_json = r.json()
        if r_json["code"] == 200:
            code = r_json["detail"]["code"]
            yield event.plain_result(f"发送成功，取件码: {code}")
        else :
            yield event.plain_result(f"发送失败，错误码: {r_json['code']}")
        
    @filter.command("receive")
    async def receive(self, event: AstrMessageEvent, code: str):
        '''这是收取文件的指令''' 
        json_data = { "code": code }
        r = requests.post(
            url=f"{self.url}/share/select/",
            json=json_data)
        r_json = r.json()
        if r_json["code"] == 200:
            detail = r_json["detail"]
            if detail["name"] == "Text":
                yield event.plain_result(f"{detail['text']}")
        else :
            yield event.plain_result(f"取件失败，错误码: {r_json['code']}")
