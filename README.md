# xiangting project

## crawl rss feeds source
```sh
cd crawler
```
First get all categories:
```
scrapy crawl xima_cates -t jsonlines
```

Then crawl contents into json file in jsons directory.
```
scrapy crawl xima_album -a url=https://www.ximalaya.com/yinyue/19750819/
```
