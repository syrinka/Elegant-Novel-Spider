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


## Todo
- [ ] 分离 config 文件
- [ ] fetch
  - [ ] 多线程爬取
  - [ ] 爬取指定章节
  - [ ] 对失效章节的处理
- [ ] 完善异常提示 (WIP)
  - [ ] 将 fetch 的爬取异常分类
- [ ] local
  - [ ] prune 清理不在目录里的章节数据
  - [x] remove 删除指定小说 / 无效小说
- [ ] isolate
  - [ ] 禁止孤立小说执行特定命令
  - [ ] 手动标记为孤立小说
  - [ ] 正常小说转化为孤立小说的机制
- [ ] 全文搜索
  - [ ] 显示章节位置
  - [ ] 显示上下文
- [ ] gui
  - [ ] 移植网页阅读器过来
    - [ ] 目录分页显示
    - [ ] 全文搜索
    - [ ] 文本修订
    - [x] 日夜模式切换
  - [ ] 在 gui 里执行 fetch 命令
- [x] 优化
  - [x] get_local_shelf 时可能存在的性能问题


## 预设
- 爬取章节时可以判断该章节是否无法爬取
- fetch 在爬取章节前对于其是否无法爬取不知情
- spine 中的每章节都应该在 index 中出现，但反之不一定
- index 的更新应该是增量的，不会覆盖。覆盖 index 应该需要手动执行
- spine 中的章节都应该是可以爬取的，无法爬取才是异常

## Info 包含字段
小说本体部分
- remote
- nid
- title
- author
- intro
- finish

metadata 部分
- star
- isolated
- tags
