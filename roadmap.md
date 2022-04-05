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

## Todo
- [ ] 分离 config 文件
- [ ] 完善异常提示
  - [ ] 将 fetch 的抓取异常分类
- [ ] local
  - [ ] prune 清理不在目录里的章节数据
  - [ ] remove 删除指定小说 / 无效小说
- [ ] info
  - [ ] merge info
  - [ ] lock info
- [ ] isolated
  - [ ] 禁止孤立小说执行特定命令
  - [ ] 手动标记为孤立小说
  - [ ] 正常小说转化为孤立小说的机制
- [ ] 全文搜索
  - [ ] 显示章节
  - [ ] 显示上下文
- [ ] gui
  - [ ] 移植网页阅读器过来
    - [ ] 目录分页显示
    - [ ] 全文搜索
    - [ ] 书签（待定）
    - [ ] 文本修订
  - [ ] 在 gui 里执行 fetch 命令
