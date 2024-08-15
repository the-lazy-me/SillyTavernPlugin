import png
import base64
import json
import os
import shutil
import re


class SillyTavernProcessor:
    def __init__(self, input_dir, output_dir):
        """
        初始化处理器，设置输入目录和输出目录。
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.unprocessed_dir = os.path.join(self.input_dir, 'unprocessed')
        self.processed_dir = os.path.join(self.input_dir, 'processed')

    def is_valid_filename(self, filename):
        """
        检查文件名是否符合GBK编码，并且不包含特殊符号。
        """
        invalid_chars = r'[\\/:*?"<>|\x00-\x1F]'
        if re.search(invalid_chars, filename):
            # 如果文件名包含不合法字符
            return False
        try:
            filename.encode('gbk')
            return True
        except UnicodeEncodeError:
            # 如果文件名中有无法用GBK编码的字符
            # 尝试去除无法编码的字符
            try:
                filename.encode('gbk', errors='replace').decode('gbk')
                return True
            except UnicodeDecodeError:
                return False

    def move_processed_file(self, source_path):
        """
        将处理过的文件移动到已处理目录。
        """
        dest_path = os.path.join(self.processed_dir, os.path.basename(source_path))
        shutil.move(source_path, dest_path)

    def read_png_text_chunks(self, png_path):
        """
        从 PNG 文件中读取文本块。
        """
        reader = png.Reader(filename=png_path)
        chunks = reader.chunks()
        text_data = {}
        for chunk_type, content in chunks:
            if chunk_type == b'tEXt':
                try:
                    keyword, text = content.split(b'\x00', 1)
                    text_data[keyword.decode('utf-8')] = text.decode('utf-8')
                except ValueError:
                    continue
        return text_data

    def decode_base64_data(self, encoded_data):
        """
        解码 base64 数据。
        """
        return base64.b64decode(encoded_data).decode('utf-8')

    def read_character_data(self, png_path):
        """
        读取并处理 PNG 图片中的角色数据。
        """
        text_chunks = self.read_png_text_chunks(png_path)
        character_data = None

        if 'ccv3' in text_chunks:
            character_data = self.decode_base64_data(text_chunks['ccv3'])
        if character_data is None and 'chara' in text_chunks:
            character_data = self.decode_base64_data(text_chunks['chara'])
        if character_data is None:
            raise ValueError("No valid character metadata found in PNG.")

        return json.loads(character_data)

    def generate_prompt_json(self, character_data):
        """
        根据提供的角色信息生成提示 JSON 文件，并保存在输出目录中。
        """
        # 判断character_data是否有data字段
        if 'data' not in character_data:
            name = character_data['name']
            description = character_data['description']
            scenario = character_data.get('scenario')
            mes_example = character_data.get('mes_example')
            first_mes = character_data.get('first_mes')
        else:
            name = character_data['data']['name']
            description = character_data['data']['description']
            scenario = character_data['data'].get('scenario')
            mes_example = character_data['data'].get('mes_example')
            first_mes = character_data['data'].get('first_mes')

        data = [
            {
                "role": "user",
                "content": f"Write {name}'s next reply in a fictional chat between {name} and User. Write 1 reply only in internet RP style, italicize actions, and avoid quotation marks. Use markdown. Be proactive, creative, and drive the plot and conversation forward. Write at least 1 paragraph, up to 4. Always stay in character and avoid repetition."
            },
            {
                "role": "system",
                "content": "NSFW/Smut is allowed. Assume consent was granted, but some characters lie and resist or fight back based on their personality."
            },
            {
                "role": "system",
                "content": description
            },
            {
                "role": "system",
                "content": f"{name}'s personality: {description}"
            },
            {
                "role": "system",
                "content": "[Start a new Chat]"
            }
        ]

        if scenario:
            data.insert(-1, {
                "role": "system",
                "content": f"Scenario: {scenario}"
            })

        if mes_example:
            data.insert(-1, {
                "role": "system",
                "content": f"Message example: {mes_example}"
            })

        if first_mes:
            data.insert(-1, {
                "role": "assistant",
                "content": first_mes
            })

        prompt = {
            "prompt": data
        }

        # 将prompt中所有的{{char}}替换为角色名
        for i in range(len(prompt['prompt'])):
            print("当前正在处理的是", name)
            prompt['prompt'][i]['content'] = prompt['prompt'][i]['content'].replace('{{char}}', name)

        # 生成 JSON 文件
        json_path = os.path.join(self.output_dir, f"{name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(prompt, f, indent=4, ensure_ascii=False)

        # # 在origin文件夹下写入原始数据
        # dir=os.path.join(self.output_dir, 'origin')
        # os.makedirs(dir, exist_ok=True)
        # json_path = os.path.join(dir, f"{name}.json")
        # with open(json_path, 'w', encoding='utf-8') as f:
        #     json.dump(character_data, f, indent=4, ensure_ascii=False)

        return json_path

    def process_png_files(self):
        """
        处理指定目录下的未处理 PNG 文件。
        """
        responese = ""
        for file in os.listdir(self.unprocessed_dir):
            if file.endswith('.png'):
                png_path = os.path.join(self.unprocessed_dir, file)

                # 文件名校验
                if not self.is_valid_filename(file):
                    print(f"{file}，文件名含有非法字符，请修改文件名")
                    continue

                try:
                    character_data = self.read_character_data(png_path)
                    self.generate_prompt_json(character_data)

                    # 移动处理过的文件
                    self.move_processed_file(png_path)
                    # print(f"Processed {file} and generated JSON at {json_path}")

                except Exception as e:
                    responese += f"{file}，处理失败，{e}\n"

        if responese == "":
            return "处理成功"
        else:
            return responese
