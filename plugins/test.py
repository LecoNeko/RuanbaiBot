

if __name__ == '__main__':
    import requests
    import random

    CFPROBLEMS = r'https://codeforces.com/api/problemset.problems'
    para = {}
    para['tags'] = 'constructive algorithms'
    res = requests.get(CFPROBLEMS, params=para)
    res = res.json()
    if not res or str(res.get('status')) !='OK':
        print( '查询失败QAQ')
    res = res['result'].get('problems')

    lrange = random.randint(0, len(res)-100)
    rrange = lrange + 3

    anslist = []

    for item in res[lrange:rrange]:
        index = item.get('index', '')
        name = item.get('name', '')
        rating = str(item.get('rating', ''))
        tg = item.get('tags', '')
        ans = index + '、' + name + '\n'
        ans += 'Difficulty：' + rating +'\n'
        ans += "Tags："
        for i in tg:
            ans += str(i)
        anslist.append(ans)
    print(ans)
