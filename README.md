<div align="center">

# Elegant Novel Spider

</div>

## ens
Elegant Novel Spider, 简写为 ens, 是一个集合爬取、缓存、输出功能为一体的小说爬虫框架。（应该是框架罢）

ens 提供了一组简洁易用的命令与友好的交互提示，用户无需关注操作细节，只需专注于编写爬虫逻辑，实现几个方法，即可直接对接使用。

ens 会在本地存储爬取的小说数据，这在追更网文时尤其有优势（事实上 ens 就是为了追更而开发的）。同时 ens 会在每次爬取前检查缺漏章节，可以有效应对今日更新明日 `该章节未审核通过` 的问题。

## 使用

如可使用 [Poetry](https://python-poetry.org/)，可使用 `poetry install` 以安装依赖。或 `pip install -r requirements.txt`

依赖安装完成后，将 `.env.example` 文件复制一份，并重命名为 `.env`

此后即可通过 `python -m ens` 或 `ens` (Windows only) 使用 Elegant Novel Spider

进一步用法请参阅 [usage.md](docs/usage.md)