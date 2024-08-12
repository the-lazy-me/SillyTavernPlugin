import copy
import os

from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from plugins.SillyTavernPlugin.pkg.processor import SillyTavernProcessor


# 注册插件
@register(name="SillyTavernPlugin", description="SillyTavernPlugin插件，用于将酒馆角色卡转写为QChatGPT人格预设的插件",
          version="1.0",
          author="the-lazy-me")
class SillyTavernPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        super().__init__(host)
        create_data_dir()
        silly_tavern_process()
        pass

    @handler(PromptPreProcessing)
    async def _(self, ctx: EventContext):
        # print(ctx.event.default_prompt)
        prompt = copy.deepcopy(ctx.event.default_prompt)
        type = ctx.event.query.message_event.type
        user_name = ''
        if type == 'FriendMessage':
            user_name = ctx.event.query.message_event.sender.nickname
        elif type == 'GroupMessage':
            user_name = ctx.event.query.message_event.sender.member_name
        prompt = alter_prompt(prompt, user_name)

        ctx.event.default_prompt = prompt

    # 插件卸载时触发
    def __del__(self):
        pass


# 修改提示词中的{{user}}变量
def alter_prompt(prompt: list[llm_entities.Message], user_name: str):
    for i in range(len(prompt)):
        prompt[i].content = prompt[i].content.replace("{{user}}", user_name)
    return prompt


# 创建数据文件夹
def create_data_dir():
    base_path = "data/plugins/SillyTavernPlugin"
    # 在base_path下创建文件夹characters_cards
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(base_path + "/characters_cards", exist_ok=True)
    # 在characters_cards下创建文件夹processed和unprocessed
    os.makedirs(base_path + "/characters_cards/processed", exist_ok=True)
    os.makedirs(base_path + "/characters_cards/unprocessed", exist_ok=True)


# 角色卡处理
def silly_tavern_process():
    stp = SillyTavernProcessor('data/plugins/SillyTavernPlugin/characters_cards',
                               'data/scenario')
    result = stp.process_png_files()
    print("SillyTavernPlugin插件处理完成")
    return result
