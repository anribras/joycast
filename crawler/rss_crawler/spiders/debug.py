from scrapy import cmdline


cmd = """
scrapy crawl ximalaya -a url=https://www.ximalaya.com/ertong/260744/ -o output.json
"""
cmdline.execute(cmd.split())