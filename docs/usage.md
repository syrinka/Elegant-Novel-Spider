## 环境配置

```bash
pip install -r requirements.txt
```

更推荐使用 `poetry` 进行安装

```
poetry install
```

## 配置文件

将根目录下的 `ens_config.example` 复制一份，命名为 `ens_config`

## 编写远端源

请参考[远端源编写文档](remote-dev.md)

## 基本使用

所有命令都以 `python -m ens` 开头，本文的余下部分将以 `ens` 代替 `python -m ens`。

您可以通过 `alias ens='/bin/env python3 -m ens'` 达到相同的效果。

```bash
ens info -r NOVEL # 获取小说的远端信息

ens fetch -t 5 NOVEL # 以多线程爬取小说
ens fetch --fetch-info NOVEL # 更新小说信息

ens dump -d txt # 以 epub 格式输出小说
```

```bash
ens local list # 列出本地所有缓存小说
ens remote list # 列出所有远端源
```