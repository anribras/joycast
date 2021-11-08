from scrapy import cmdline
# cmd = "scrapy crawl xima_cates -t jsonlines"
cmd = "scrapy crawl ximalaya -a url=https://www.ximalaya.com/yinyue/5571971/ "
cmdline.execute(cmd.split())
