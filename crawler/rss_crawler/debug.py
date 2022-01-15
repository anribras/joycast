from scrapy import cmdline
cmd = "scrapy crawl xima_cates -t jsonlines"
# cmd = "scrapy crawl xima_albums -a url=https://www.ximalaya.com/yinyue/5571971/ "
# cmd = "scrapy crawl xima_targets "
cmdline.execute(cmd.split())
