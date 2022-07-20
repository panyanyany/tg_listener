# 币安链代币价格监控 & Telegram 代币宣传监控统计工具

## 监控TG群组中的代币推荐
```
scripts/mon_tg.py
```
作用：将群组中所有出现的代币都记录起来，整理成一个排行榜，就可以知道哪些币正在宣传，以及哪些币正在变得热门

## 监控币安链所有代币价格
```
scripts/listen_chain.py
```
作用：不断请求节点，拿最新的区块信息，把买入/卖出的操作及对应价格变化记录下来

### Push to multiple remote
https://gist.github.com/rvl/c3f156e117e22a25f242

### E11000 duplicate key error collection
lib 的引擎错了，lib 删掉重新初始化