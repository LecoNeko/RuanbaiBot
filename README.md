# ruanbaibot is on coding, most functions are placed in 'utils.py', it will be moved to the corresponding file in the future
A test bot send Setu, Anime picture search, Group processing, Codeforces Info query and etc. 


Temporary set '!help' under:
----

### Anime

* **Setu**: send a random taged Setu to sender. R18 only can be applied at WHITEGROUPLIST

	* eg:'[bot nickname] + 来张 + (r18) + [tag1 & tag2 | tag3 |tag4]  + 涩图'
	* 软白来张涩图
	* 软白来5张涩图
	* 软白来张白丝&萝莉涩图


* **PictureSearcher**: Searching the most similar 3 anime picture from saucenao and sending them to sender

	* eg: '@bot + a series of ANIME picture'

### CodeForces

Stared with '!cf' to apply the function


* info: query rating, rank, maxRating, maxRank of 'cfId'

	* eg: '!cf info [cfId]'
	* !cf info RBpencil


* rtcg: get last 'cnt' contest rating change of 'cfId'

	* eg:'!cf rtcg [cfId] ([cnt])'
	* !cf rtcg RBpencil 5
	* !cf rtcg RBpencil


* lastsb: last submission statue of 'cfId':

	* eg:'!cf lastsb [cfId]'
	* !cf lastsb RBpencil


* statues: show last 5 submission statue of 'cfId'

	* eg:'!cf statues [cfId]'
	* !cf statues RBpencil

* contest: show coming contests
	* eg:'!cf rect'


感谢
----
[nonebot](https://github.com/nonebot/nonebot)

[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

[cq-picsearcher-bot](https://github.com/Tsuk1ko/cq-picsearcher-bot)
