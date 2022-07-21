# 币安链代币价格监控 & Telegram 代币宣传监控统计工具

## 功能1：监控TG群组中的代币推荐
```
scripts/mon_tg.py
```
作用：将群组中所有出现的代币都记录起来，整理成一个排行榜，就可以知道哪些币正在宣传，以及哪些币正在变得热门

![](./resources/images/mon_tg.png)

## 功能2：监控币安链所有代币价格，并生成排行榜
```
scripts/listen_chain.py
```
作用：不断请求节点，拿最新的区块信息，把买入/卖出的操作及对应价格变化记录下来
最后根据币价变化，统计成15分钟榜、小时榜、日榜、小时连涨榜、日连涨榜

### 特性：
* 能准确获取每次 swap 的价格、池子变化
* 把以 BNB、ETH、BUSD 等计价统一转换成 USDT
* 自动过滤异常交易
* 异步并发请求接口，避免被节点屏蔽
* 丰富的前端界面，一键跳转到K线和合约检查

### 缺点：
* 不是每笔交易都能捕捉到，主要是因为节点和网络原因


![](./resources/images/tugou.jpg)

## 一些小问题

### Push to multiple remote
https://gist.github.com/rvl/c3f156e117e22a25f242

### E11000 duplicate key error collection
lib 的引擎错了，lib 删掉重新初始化


## 交个朋友
![](./resources/images/wechat.jpeg)
