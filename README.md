# SillyTavernPlugin插件使用教程

> 但是我没学过python，代码大量依赖于AI生成，难免有不合理不正确之处，反正代码和人有一个能跑就行😋

## 插件安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/the-lazy-me/SillyTavernPlugin.git
```

## 插件使用

> 这是插件的流程（可以不看）：
>
> 1. 完成插件安装后，运行`QChatGPT主程序`后，插件会自动生成`data/plugins/SillyTavernPlugin/characters_cards`文件夹，其中有两个子文件夹：`unprocessed`和`processed`
> 2. `unprocessed`中用于存放未经处理的酒馆角色卡，所有将要使用的酒馆角色卡（png文件）放入`unprocessed`文件夹中即可，当插件加载时，`unprocessed`中所有的png文件都会被处理和转换，转换完成的将会移动到`processed`文件夹中
> 3. 插件加载生成的预设将会放入`data/scenario`文件夹中，里面放着所有的预设，每一个`json文件`对应一个预设，预设名就是文件名

1. 把你获取到的酒馆角色卡（png文件）放入`data/plugins/SillyTavernPlugin/characters_cards/unprocessed`文件夹中
2. 重新运行`QChatGPT主程序`后，插件会自动生成对应预设，预设文件在`data/scenario`文件夹中，里面放着所有的预设，每一个`json文件`对应一个预设，预设名就是文件名。
   - 切换方法：`!default set <预设名>`，（将<预设名>整体替换为文件名） 然后再发送`!reset`
   - 例如：在`data/scenario`文件夹中有一个名为`阿Q.json`的文件，当我们要使用`阿Q`这个预设时，以管理员身份向机器人发送`!default set 阿Q`，机器人回复后再发送`!reset`

## 推荐配置

> 由于预设内容的不可控性：
>
> 当预设内含 NSFW 内容时，请注意使用环境！！！

### 配置pipeline.json

将`income-msg-check`和`check-sensitive-words`字段的值设为`false`

### 配置provider.json

将`prompt-mode`字段设为`full-scenario`，`model`字段要特别设置一下，推荐模型如下

一般的预设，使用任意模型均可

如果含有NSFW内容，模型选择：

最好的：claude-3-opus-20240229

一般的：claude-3-sonnet-20240229，gemini-1.5-pro-latest，gemini-1.5-flash-latest
