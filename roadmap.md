## 功能
- 追踪小说内容
    - 本地存储
    - 增量更新
    - 检查章节删除，merge
    - 忽略指定章节的删除
    - 上锁
- 导出
    - txt
    - epub
    - mobi
    - 自定义参数
- 网页阅读
    - 全局搜索
    - 分页
    - 自选 style
    - web api
- 源
    - 资源文件夹
    - get_index
    - get_metadata
    - get_chap
    - get_origin
- 全局
    - config
    - 数据缓存


## Cli
- fetch
- local
  - list(search)
  - rm
- remote
  - list
  - status
- reader

## 命名
|code|format|
|--|--|
|remote| a-z A-Z 0-9 -_. |
|novel_id| a-z A-Z 0-9 -_. |
|code|$remote ~ $novel_id|

## local 格式
- metadata.yml
- index.yml
- chaps.db

## Index
- name: name
  cids: 
    - cid1
    - cid2
    - cid3
- name: name
  cid
