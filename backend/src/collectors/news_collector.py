import feedparser
import time
from datetime import datetime
import pandas as pd
from typing import List, Dict
import re

from src.database.operations import db, DatabaseManager
from src.utils.logger import logger

class NewsCollector:
    """新闻情绪采集器"""

    RSS_FEEDS = {
        'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'CoinTelegraph': 'https://cointelegraph.com/rss'
    }

    # 简单的关键词词典
    BULLISH_KEYWORDS = ['partners', 'launch', 'record', 'high', 'surge', 'adoption', 'bull', 'ETF', 'approved']
    BEARISH_KEYWORDS = ['hack', 'scam', 'crash', 'ban', 'lawsuit', 'sec', 'investigation', 'bear', 'drop']

    def __init__(self):
        self.db = db
        logger.info("NewsCollector initialized.")

    def analyze_sentiment(self, text: str) -> float:
        """简单的基于规则的情绪分析 (-1.0 to 1.0)"""
        text_lower = text.lower()
        score = 0
        
        for word in self.BULLISH_KEYWORDS:
            if word in text_lower:
                score += 0.2
                
        for word in self.BEARISH_KEYWORDS:
            if word in text_lower:
                score -= 0.3 # 负面新闻权重稍大
                
        # 归一化到 -1 到 1
        return max(min(score, 1.0), -1.0)

    def fetch_latest_news(self, limit: int = 5) -> List[Dict]:
        """获取最新新闻并分析"""
        all_news = []
        
        for source, url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                logger.info(f"Fetched {len(feed.entries)} entries from {source}")
                
                for entry in feed.entries[:limit]:
                    title = entry.title
                    summary = getattr(entry, 'summary', '')
                    link = entry.link
                    published = getattr(entry, 'published', str(datetime.now()))
                    
                    # 分析情绪
                    sentiment_score = self.analyze_sentiment(title + " " + summary)
                    
                    news_item = {
                        'author': source, # 简化处理，使用来源作为作者
                        'title': title,
                        'content': summary[:200] + "...", # 截断内容
                        'url': link,
                        'sentiment': sentiment_score,
                        'timestamp': published
                        # 这里没存入数据库，实际项目中可以扩展 News 表
                    }
                    
                    # 存入 memory 表作为短期信息? 或者单独的 News 表
                    # 这里演示存入 Memory
                    self.db.log_decision({ # 借用 decision 表记录一下重要新闻，或者直接存 Memory
                        'decision_type': 'NEWS_EVENT',
                        'layer': 'ANALYSIS',
                        'input_data': {'source': source, 'title': title}, 
                        'output_recommendation': {'sentiment': sentiment_score},
                        'confidence': abs(sentiment_score)
                    })
                    
                    all_news.append(news_item)
                    
            except Exception as e:
                logger.error(f"Error fetching news from {source}: {e}")
                
        return all_news

if __name__ == "__main__":
    collector = NewsCollector()
    news = collector.fetch_latest_news()
    for n in news:
        print(f"[{n['author']}] {n['title']} (Sentiment: {n['sentiment']})")
