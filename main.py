from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image, File
import requests
import tempfile

@register("filecodebox", "BryanHe", "FileCodeBox配套插件", "1.0.0", "https://github.com/BryanHeBY/astrbot_plugin_filecodebox")
class FileCodeBox(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.url = config.get("filecodebox_url")
        if self.url[-1] == "/":
            self.url = self.url[:-1]
    
    @filter.command("send")
    async def send(self, event: AstrMessageEvent, text: str|None = None):
        '''这是发送文件的指令''' 
        if text is None:
            yield event.plain_result("请输入要发送的内容")
            return
        form_data = {
            "text": text,
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
            elif detail["name"].endswith(("jpg", "jpeg", "png", "gif")):
                download_url = f"{self.url}{detail['text']}"
                chain = [
                    Image.fromURL(url=download_url)
                ]
                yield event.chain_result(chain)
            else:
                # download_url = f"{self.url}{detail['text']}"
                # r = requests.get(download_url)
                # tmp = tempfile.NamedTemporaryFile(delete=False)
                # try:
                #     tmp.write(r.content)
                #     tmp.flush()
                #     chain = [
                #         File(name=detail['name'], file=tmp.name)
                #     ]
                #     yield event.chain_result(chain)
                # finally:
                #     tmp.close()  # 文件关闭即删除
                yield event.plain_result(f"暂不支持下载文件类型: {detail['name']}")
        else :
            yield event.plain_result(f"取件失败，错误码: {r_json['code']}")
