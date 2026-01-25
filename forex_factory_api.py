"""
ForexFactory API Integration for Trading Bot
Provides news sentiment, economic calendar, and market analysis data
"""

import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import time

class ForexFactoryAPI:
    """ForexFactory data integration with sentiment analysis and calendar events"""
    
    def __init__(self):
        self.base_url = "https://www.forexfactory.com"
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=30))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_economic_calendar(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get economic calendar events from ForexFactory"""
        try:
            url = f"{self.base_url}/calendar.php"
            
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            params = {
                'day': start_date.strftime('%b%d.%Y'),
                'range': f"{start_date.strftime('%b%d.%Y')}-{end_date.strftime('%b%d.%Y')}"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._parse_calendar_html(html_content)
                else:
                    print(f"ForexFactory calendar request failed: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"Error fetching ForexFactory calendar: {e}")
            return []
    
    def _parse_calendar_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML content to extract calendar events"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            events = []
            
            # Find calendar table
            calendar_table = soup.find('table', class_='calendar__table')
            if not calendar_table:
                return events
            
            current_date = None
            
            for row in calendar_table.find_all('tr', class_='calendar__row'):
                # Check if this row contains date information
                date_cell = row.find('td', class_='calendar__cell--date')
                if date_cell and date_cell.get_text(strip=True):
                    current_date = date_cell.get_text(strip=True)
                    continue
                
                # Extract event data
                time_cell = row.find('td', class_='calendar__cell--time')
                currency_cell = row.find('td', class_='calendar__cell--currency')
                impact_cell = row.find('td', class_='calendar__cell--impact')
                event_cell = row.find('td', class_='calendar__cell--event')
                actual_cell = row.find('td', class_='calendar__cell--actual')
                forecast_cell = row.find('td', class_='calendar__cell--forecast')
                previous_cell = row.find('td', class_='calendar__cell--previous')
                
                if event_cell and currency_cell:
                    # Determine impact level
                    impact_level = 'Low'
                    if impact_cell:
                        impact_icons = impact_cell.find_all('span', class_='calendar__impact-icon')
                        impact_level = ['Low', 'Medium', 'High'][min(len(impact_icons), 3) - 1] if impact_icons else 'Low'
                    
                    event = {
                        'date': current_date,
                        'time': time_cell.get_text(strip=True) if time_cell else '',
                        'currency': currency_cell.get_text(strip=True),
                        'impact': impact_level,
                        'event': event_cell.get_text(strip=True),
                        'actual': actual_cell.get_text(strip=True) if actual_cell else '',
                        'forecast': forecast_cell.get_text(strip=True) if forecast_cell else '',
                        'previous': previous_cell.get_text(strip=True) if previous_cell else '',
                        'timestamp': self._parse_event_datetime(current_date, time_cell.get_text(strip=True) if time_cell else '')
                    }
                    
                    events.append(event)
            
            return events
            
        except Exception as e:
            print(f"Error parsing ForexFactory calendar HTML: {e}")
            return []
    
    def _parse_event_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Parse date and time strings into datetime object"""
        try:
            if not date_str or not time_str:
                return None
            
            # Parse date (format: "Fri Dec 15")
            current_year = datetime.now().year
            date_with_year = f"{date_str} {current_year}"
            
            # Parse time (format: "8:30am" or "All Day")
            if time_str.lower() == 'all day':
                time_str = '00:00'
            else:
                # Convert 12-hour to 24-hour format
                time_str = time_str.replace('am', '').replace('pm', '').strip()
                if 'pm' in time_str.lower() and not time_str.startswith('12'):
                    hour, minute = time_str.split(':')
                    time_str = f"{int(hour) + 12}:{minute}"
            
            full_datetime_str = f"{date_with_year} {time_str}"
            return datetime.strptime(full_datetime_str, "%a %b %d %Y %H:%M")
            
        except Exception as e:
            print(f"Error parsing datetime: {e}")
            return None
    
    async def get_news_sentiment(self, currency_pairs: List[str] = None) -> Dict[str, Any]:
        """Get news and sentiment analysis from ForexFactory"""
        try:
            url = f"{self.base_url}/news.php"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._parse_news_sentiment(html_content, currency_pairs)
                else:
                    print(f"ForexFactory news request failed: {response.status}")
                    return {}
                    
        except Exception as e:
            print(f"Error fetching ForexFactory news: {e}")
            return {}
    
    def _parse_news_sentiment(self, html_content: str, currency_pairs: List[str] = None) -> Dict[str, Any]:
        """Parse news content and analyze sentiment"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find news articles
            news_items = soup.find_all('div', class_='news__item')
            
            sentiment_data = {
                'overall_sentiment': 0,
                'currency_sentiments': {},
                'news_count': len(news_items),
                'articles': []
            }
            
            sentiment_scores = []
            currency_sentiments = {}
            
            for item in news_items[:20]:  # Process top 20 news items
                title_elem = item.find('a', class_='news__title')
                time_elem = item.find('span', class_='news__time')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # Basic sentiment analysis
                    sentiment_score = self._analyze_text_sentiment(title)
                    sentiment_scores.append(sentiment_score)
                    
                    # Extract currency mentions
                    mentioned_currencies = self._extract_currency_mentions(title)
                    
                    article_data = {
                        'title': title,
                        'time': time_elem.get_text(strip=True) if time_elem else '',
                        'sentiment_score': sentiment_score,
                        'mentioned_currencies': mentioned_currencies
                    }
                    
                    sentiment_data['articles'].append(article_data)
                    
                    # Aggregate currency sentiments
                    for currency in mentioned_currencies:
                        if currency not in currency_sentiments:
                            currency_sentiments[currency] = []
                        currency_sentiments[currency].append(sentiment_score)
            
            # Calculate overall sentiment
            if sentiment_scores:
                sentiment_data['overall_sentiment'] = np.mean(sentiment_scores)
            
            # Calculate currency-specific sentiments
            for currency, scores in currency_sentiments.items():
                sentiment_data['currency_sentiments'][currency] = {
                    'sentiment': np.mean(scores),
                    'articles_count': len(scores),
                    'volatility': np.std(scores) if len(scores) > 1 else 0
                }
            
            return sentiment_data
            
        except Exception as e:
            print(f"Error parsing ForexFactory news sentiment: {e}")
            return {}
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """Basic sentiment analysis using keyword matching"""
        # Positive keywords
        positive_words = [
            'bull', 'bullish', 'rise', 'rising', 'up', 'gain', 'gains', 'strong', 'strength',
            'boost', 'positive', 'optimistic', 'recovery', 'growth', 'improve', 'higher',
            'rally', 'surge', 'soar', 'climb', 'advance', 'upbeat', 'confident'
        ]
        
        # Negative keywords  
        negative_words = [
            'bear', 'bearish', 'fall', 'falling', 'down', 'loss', 'losses', 'weak', 'weakness',
            'decline', 'negative', 'pessimistic', 'recession', 'crisis', 'lower', 'drop',
            'plunge', 'crash', 'slump', 'concern', 'worried', 'fear', 'risk'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0  # Neutral
        
        return (positive_count - negative_count) / total_sentiment_words
    
    def _extract_currency_mentions(self, text: str) -> List[str]:
        """Extract currency mentions from text"""
        currencies = [
            'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD',
            'dollar', 'euro', 'pound', 'yen', 'aussie', 'loonie', 'franc', 'kiwi'
        ]
        
        mentioned = []
        text_upper = text.upper()
        
        for currency in currencies:
            if currency.upper() in text_upper:
                # Map common names to currency codes
                currency_map = {
                    'DOLLAR': 'USD', 'EURO': 'EUR', 'POUND': 'GBP', 'YEN': 'JPY',
                    'AUSSIE': 'AUD', 'LOONIE': 'CAD', 'FRANC': 'CHF', 'KIWI': 'NZD'
                }
                currency_code = currency_map.get(currency, currency)
                if currency_code not in mentioned:
                    mentioned.append(currency_code)
        
        return mentioned
    
    async def get_market_sentiment_score(self, currency_pair: str) -> Dict[str, Any]:
        """Get comprehensive market sentiment for a specific currency pair"""
        try:
            # Extract base and quote currencies
            base_currency = currency_pair[:3]
            quote_currency = currency_pair[3:6]
            
            # Get news sentiment
            news_sentiment = await self.get_news_sentiment([base_currency, quote_currency])
            
            # Get economic calendar events
            calendar_events = await self.get_economic_calendar(days_ahead=3)
            
            # Calculate pair-specific sentiment
            base_sentiment = news_sentiment.get('currency_sentiments', {}).get(base_currency, {}).get('sentiment', 0)
            quote_sentiment = news_sentiment.get('currency_sentiments', {}).get(quote_currency, {}).get('sentiment', 0)
            
            # Calculate impact from upcoming events
            event_impact = self._calculate_event_impact(calendar_events, [base_currency, quote_currency])
            
            # Combine sentiments (base positive, quote negative = bullish for pair)
            pair_sentiment = (base_sentiment - quote_sentiment) / 2
            
            return {
                'pair': currency_pair,
                'sentiment_score': pair_sentiment,
                'base_currency_sentiment': base_sentiment,
                'quote_currency_sentiment': quote_sentiment,
                'overall_market_sentiment': news_sentiment.get('overall_sentiment', 0),
                'upcoming_event_impact': event_impact,
                'news_articles_analyzed': news_sentiment.get('news_count', 0),
                'high_impact_events_24h': len([e for e in calendar_events if e.get('impact') == 'High' and self._is_within_24h(e.get('timestamp'))]),
                'sentiment_strength': abs(pair_sentiment),
                'sentiment_direction': 'Bullish' if pair_sentiment > 0.1 else 'Bearish' if pair_sentiment < -0.1 else 'Neutral'
            }
            
        except Exception as e:
            print(f"Error calculating market sentiment for {currency_pair}: {e}")
            return {'pair': currency_pair, 'sentiment_score': 0, 'error': str(e)}
    
    def _calculate_event_impact(self, events: List[Dict], currencies: List[str]) -> Dict[str, Any]:
        """Calculate potential impact from upcoming economic events"""
        try:
            relevant_events = [
                event for event in events 
                if event.get('currency') in currencies and self._is_within_24h(event.get('timestamp'))
            ]
            
            high_impact_count = len([e for e in relevant_events if e.get('impact') == 'High'])
            medium_impact_count = len([e for e in relevant_events if e.get('impact') == 'Medium'])
            
            # Calculate impact score
            impact_score = (high_impact_count * 3 + medium_impact_count * 1.5) / max(len(relevant_events), 1)
            
            return {
                'total_events': len(relevant_events),
                'high_impact_events': high_impact_count,
                'medium_impact_events': medium_impact_count,
                'impact_score': min(impact_score, 5),  # Cap at 5
                'next_major_event': self._find_next_major_event(relevant_events)
            }
            
        except Exception as e:
            print(f"Error calculating event impact: {e}")
            return {'total_events': 0, 'impact_score': 0}
    
    def _find_next_major_event(self, events: List[Dict]) -> Optional[Dict]:
        """Find the next major economic event"""
        try:
            high_impact_events = [e for e in events if e.get('impact') == 'High' and e.get('timestamp')]
            if not high_impact_events:
                return None
            
            # Sort by timestamp
            high_impact_events.sort(key=lambda x: x['timestamp'])
            return high_impact_events[0]
            
        except Exception as e:
            print(f"Error finding next major event: {e}")
            return None
    
    def _is_within_24h(self, timestamp: Optional[datetime]) -> bool:
        """Check if timestamp is within the next 24 hours"""
        if not timestamp:
            return False
        
        now = datetime.now()
        return now <= timestamp <= now + timedelta(hours=24)

# Global instance for use across the application
forex_factory_api = None

async def get_forex_factory_api():
    """Get or create ForexFactory API instance"""
    global forex_factory_api
    if forex_factory_api is None:
        forex_factory_api = ForexFactoryAPI()
    return forex_factory_api

async def get_sentiment_analysis(currency_pair: str) -> Dict[str, Any]:
    """Get sentiment analysis for a currency pair"""
    async with ForexFactoryAPI() as ff_api:
        return await ff_api.get_market_sentiment_score(currency_pair)

async def get_economic_events(days_ahead: int = 3) -> List[Dict[str, Any]]:
    """Get upcoming economic calendar events"""
    async with ForexFactoryAPI() as ff_api:
        return await ff_api.get_economic_calendar(days_ahead)