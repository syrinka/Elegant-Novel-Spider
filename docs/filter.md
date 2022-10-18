# 过滤器

过滤器用于筛选书架 (Shelf) 内的小说 (Novel)。
一个过滤器由若干条规则组成。

## 规则

一条规则由四部分组成：

- 筛选属性
- 感叹号 (optional)
- 匹配模式
- 值

筛选属性取下列四个值之一，分别为：

- remote
- title
- author
- intro

加上 `!` 以表示否定规则

比较属性取下列四个值之一，分别为：

- `==` （全等）
- `^=`（以...开头）
- `$=`（以...结尾）
- `*= / =`（包含...）

以下是一些有效的规则表达：

- `remote==abc`     （远程源等于 "abc"）
- `title*=转生  `  （标题中包含 "转生"）
- `author^=miral`（作者名以 "miral" 开头）
- `intro!*=停更`   （介绍中不包含 "停更"）

规则中不能出现空格。

## 使用

使用选项 `-f/--filter` 以输入一条规则，可以输入多条规则。

例如：
```bash
ens local list -f remote=def -f author=somebody
```

使用开关 `--all/--any` 以指定筛选模式，默认模式为 `all`。

## Alias

ens 提供了过滤器的别名表示。

- -R/--remote
- -T/--title
- -A/--author
- -I/--intro

以下的两种表达是等效的：

```bash
-T^=hardguy
-f title^=hardguy
```

另外，若使用别名时不输入匹配模式，则将默认为 `*=` 模式。

即以下的两种表达是等效的：

```bash
-T hardguy
-f title*=hardguy
```
