WikiSearcher 
--
A Google+Wikipedia searcher based on Scrapy

# Requirements

- python2.7+
- scrapy (use `pip install scrapy` to install)

# Run

```
cd <base_dir>
scrapy crawl wiki_searcher -a data_file=<CSV_FILE> -o <OUTPUT_JSON_FILE>
```