"""
Enhanced Analysis Integration for Trading Bot
Integrates sentiment analysis, volume profile, smart money flow, and economic calendar
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# Import analysis modules with fallback handling
try:
    from forex_factory_api import get_sentiment_analysis, get_economic_events
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("ForexFactory sentiment analysis not available")

try:
    from advanced_volume_analysis import get_volume_profile_analysis
    VOLUME_ANALYSIS_AVAILABLE = True
except ImportError:
    VOLUME_ANALYSIS_AVAILABLE = False
    print("Advanced volume analysis not available")

class EnhancedAnalysisEngine:
    """Enhanced analysis engine that integrates all advanced analysis components"""
    
    def __init__(self):
        # Caching removed for real-time accuracy
        pass
        
    async def get_comprehensive_analysis(self, pair: str, df: pd.DataFrame, 
                                       existing_confidence: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive analysis including sentiment, volume, and calendar data"""
        try:
            analysis_result = existing_confidence.copy()
            
            # Add sentiment analysis
            if SENTIMENT_AVAILABLE:
                sentiment_data = await self._get_sentiment_analysis(pair)
                analysis_result['sentiment_analysis'] = sentiment_data
                
                # Integrate sentiment into confidence
                sentiment_boost = self._calculate_sentiment_boost(sentiment_data, existing_confidence.get('signal', 'NEUTRAL'))
                analysis_result['sentiment_boost'] = sentiment_boost
                analysis_result['confidence'] = min(95, existing_confidence.get('confidence', 55) + sentiment_boost)
            
            # Add volume profile analysis
            if VOLUME_ANALYSIS_AVAILABLE:
                volume_data = await self._get_volume_analysis(pair, df)
                analysis_result['volume_profile'] = volume_data
                
                # Integrate volume analysis into confidence
                volume_boost = self._calculate_volume_boost(volume_data, existing_confidence.get('signal', 'NEUTRAL'))
                analysis_result['volume_boost'] = volume_boost
                analysis_result['confidence'] = min(95, analysis_result.get('confidence', 55) + volume_boost)
            
            # Add economic calendar impact
            if SENTIMENT_AVAILABLE:
                calendar_impact = await self._get_calendar_impact(pair)
                analysis_result['calendar_impact'] = calendar_impact
                
                # Adjust confidence based on upcoming events
                calendar_adjustment = self._calculate_calendar_adjustment(calendar_impact)
                analysis_result['calendar_adjustment'] = calendar_adjustment
                analysis_result['confidence'] = max(45, min(95, analysis_result.get('confidence', 55) + calendar_adjustment))
            
            # Calculate enhanced confluence factors
            enhanced_confluence = self._calculate_enhanced_confluence(analysis_result)
            analysis_result['enhanced_confluence_score'] = enhanced_confluence
            
            # Handle confluence_factors properly - ensure it's treated as a number, not a list
            existing_confluence = existing_confidence.get('confluence_factors', 0)
            if isinstance(existing_confluence, list):
                existing_confluence = len(existing_confluence)  # Convert list to count
            analysis_result['confluence_factors'] = existing_confluence + enhanced_confluence
            
            # Add comprehensive market context
            analysis_result['market_context'] = self._generate_market_context(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return existing_confidence
    
    async def _get_sentiment_analysis(self, pair: str) -> Dict[str, Any]:
        """Get sentiment analysis without caching for real-time accuracy"""
        try:
            sentiment_data = await get_sentiment_analysis(pair)
            return sentiment_data
            
        except Exception as e:
            print(f"Error getting sentiment analysis: {e}")
            return {'sentiment_score': 0, 'sentiment_direction': 'Neutral', 'error': str(e)}
    
    async def _get_volume_analysis(self, pair: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Get volume analysis without caching for real-time accuracy"""
        try:
            volume_data = get_volume_profile_analysis(df)
            return volume_data
            
        except Exception as e:
            print(f"Error getting volume analysis: {e}")
            return {'volume_profile': {'error': str(e)}, 'smart_money_flow': {'error': str(e)}}
    
    async def _get_calendar_impact(self, pair: str) -> Dict[str, Any]:
        """Get economic calendar impact without caching for real-time accuracy"""
        try:
            events = await get_economic_events(days_ahead=3)
            return self._filter_events_for_pair(events, pair)
            
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return {'relevant_events': [], 'impact_score': 0, 'error': str(e)}
    
    def _filter_events_for_pair(self, events: List[Dict], pair: str) -> Dict[str, Any]:
        """Filter calendar events relevant to the currency pair"""
        try:
            base_currency = pair[:3]
            quote_currency = pair[3:6]
            
            relevant_events = []
            high_impact_count = 0
            
            for event in events:
                event_currency = event.get('currency', '')
                if event_currency in [base_currency, quote_currency]:
                    relevant_events.append(event)
                    if event.get('impact') == 'High':
                        high_impact_count += 1
            
            # Calculate impact score
            impact_score = min(5, high_impact_count * 2 + len(relevant_events) * 0.5)
            
            return {
                'relevant_events': relevant_events[:5],  # Top 5 most relevant
                'total_events': len(relevant_events),
                'high_impact_events': high_impact_count,
                'impact_score': impact_score,
                'next_major_event': self._find_next_major_event(relevant_events)
            }
            
        except Exception as e:
            print(f"Error filtering events for pair: {e}")
            return {'relevant_events': [], 'impact_score': 0}
    
    def _find_next_major_event(self, events: List[Dict]) -> Optional[Dict]:
        """Find the next major economic event"""
        try:
            high_impact_events = [e for e in events if e.get('impact') == 'High']
            if not high_impact_events:
                return None
            
            # Sort by timestamp if available
            for event in high_impact_events:
                if event.get('timestamp'):
                    return event
            
            return high_impact_events[0] if high_impact_events else None
            
        except Exception as e:
            print(f"Error finding next major event: {e}")
            return None
    
    def _calculate_sentiment_boost(self, sentiment_data: Dict[str, Any], signal: str) -> float:
        """Calculate confidence boost from sentiment analysis"""
        try:
            sentiment_score = sentiment_data.get('sentiment_score', 0)
            sentiment_direction = sentiment_data.get('sentiment_direction', 'Neutral')
            
            # Base sentiment boost
            base_boost = abs(sentiment_score) * 10  # Convert to 0-10 scale
            
            # Alignment bonus
            alignment_bonus = 0
            if signal == 'BUY' and sentiment_direction == 'Bullish':
                alignment_bonus = 5
            elif signal == 'SELL' and sentiment_direction == 'Bearish':
                alignment_bonus = 5
            elif signal != 'NEUTRAL' and sentiment_direction == 'Neutral':
                alignment_bonus = -2
            elif ((signal == 'BUY' and sentiment_direction == 'Bearish') or 
                  (signal == 'SELL' and sentiment_direction == 'Bullish')):
                alignment_bonus = -5
            
            # Quality factors
            quality_boost = 0
            articles_count = sentiment_data.get('news_articles_analyzed', 0)
            if articles_count > 10:
                quality_boost += 2
            
            high_impact_events = sentiment_data.get('high_impact_events_24h', 0)
            if high_impact_events > 0:
                quality_boost += 3
            
            total_boost = base_boost + alignment_bonus + quality_boost
            return max(-10, min(15, total_boost))  # Cap between -10 and +15
            
        except Exception as e:
            print(f"Error calculating sentiment boost: {e}")
            return 0
    
    def _calculate_volume_boost(self, volume_data: Dict[str, Any], signal: str) -> float:
        """Calculate confidence boost from volume analysis"""
        try:
            smart_money = volume_data.get('smart_money_flow', {})
            volume_profile = volume_data.get('volume_profile', {})
            
            boost = 0
            
            # Smart money flow alignment
            flow_direction = smart_money.get('flow_direction', 'Neutral')
            smart_money_index = smart_money.get('smart_money_index', 0)
            
            if signal == 'BUY' and flow_direction == 'Bullish':
                boost += abs(smart_money_index) * 8
            elif signal == 'SELL' and flow_direction == 'Bearish':
                boost += abs(smart_money_index) * 8
            elif signal != 'NEUTRAL' and flow_direction == 'Neutral':
                boost += 1
            elif ((signal == 'BUY' and flow_direction == 'Bearish') or 
                  (signal == 'SELL' and flow_direction == 'Bullish')):
                boost -= abs(smart_money_index) * 5
            
            # Volume profile quality
            profile_type = volume_profile.get('profile_type', 'Unknown')
            if profile_type in ['Normal', 'P-shaped', 'b-shaped']:
                boost += 2
            elif profile_type == 'D-shaped':
                boost += 1
            
            # High volume nodes near current price
            high_volume_nodes = volume_profile.get('high_volume_nodes', [])
            if len(high_volume_nodes) >= 2:
                boost += 3
            
            return max(-8, min(12, boost))  # Cap between -8 and +12
            
        except Exception as e:
            print(f"Error calculating volume boost: {e}")
            return 0
    
    def _calculate_calendar_adjustment(self, calendar_impact: Dict[str, Any]) -> float:
        """Calculate confidence adjustment based on upcoming economic events"""
        try:
            impact_score = calendar_impact.get('impact_score', 0)
            high_impact_events = calendar_impact.get('high_impact_events', 0)
            
            # Reduce confidence before major events (uncertainty)
            adjustment = 0
            
            if high_impact_events > 0:
                adjustment -= high_impact_events * 3  # -3 per high impact event
            
            if impact_score > 3:
                adjustment -= 5  # Additional penalty for very high impact periods
            elif impact_score > 1:
                adjustment -= 2  # Moderate penalty
            
            # Check timing of next major event
            next_event = calendar_impact.get('next_major_event')
            if next_event and next_event.get('timestamp'):
                try:
                    event_time = next_event['timestamp']
                    if isinstance(event_time, str):
                        event_time = datetime.fromisoformat(event_time)
                    
                    time_to_event = (event_time - datetime.now()).total_seconds() / 3600  # Hours
                    
                    if time_to_event < 2:  # Within 2 hours
                        adjustment -= 8
                    elif time_to_event < 6:  # Within 6 hours
                        adjustment -= 5
                    elif time_to_event < 24:  # Within 24 hours
                        adjustment -= 2
                except:
                    pass
            
            return max(-15, min(5, adjustment))  # Cap between -15 and +5
            
        except Exception as e:
            print(f"Error calculating calendar adjustment: {e}")
            return 0
    
    def _calculate_enhanced_confluence(self, analysis_result: Dict[str, Any]) -> int:
        """Calculate enhanced confluence score from all analysis components"""
        try:
            confluence_count = 0
            
            # Sentiment confluence
            sentiment_boost = analysis_result.get('sentiment_boost', 0)
            if sentiment_boost > 3:
                confluence_count += 2
            elif sentiment_boost > 0:
                confluence_count += 1
            
            # Volume confluence
            volume_boost = analysis_result.get('volume_boost', 0)
            if volume_boost > 5:
                confluence_count += 2
            elif volume_boost > 2:
                confluence_count += 1
            
            # Calendar confluence (stability during low-impact periods)
            calendar_adjustment = analysis_result.get('calendar_adjustment', 0)
            if calendar_adjustment > -2:  # Low negative impact or positive
                confluence_count += 1
            
            # Smart money confluence
            smart_money = analysis_result.get('volume_profile', {}).get('smart_money_flow', {})
            institutional_activity = smart_money.get('flow_direction', 'Neutral')
            if institutional_activity != 'Neutral':
                confluence_count += 1
            
            # Market context confluence
            if analysis_result.get('market_context', {}).get('overall_bias') != 'Mixed':
                confluence_count += 1
            
            return confluence_count
            
        except Exception as e:
            print(f"Error calculating enhanced confluence: {e}")
            return 0
    
    def _generate_market_context(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive market context summary"""
        try:
            context = {
                'overall_bias': 'Neutral',
                'market_regime': 'Normal',
                'key_factors': [],
                'risk_factors': [],
                'opportunities': []
            }
            
            # Determine overall bias
            sentiment_direction = analysis_result.get('sentiment_analysis', {}).get('sentiment_direction', 'Neutral')
            volume_direction = analysis_result.get('volume_profile', {}).get('smart_money_flow', {}).get('flow_direction', 'Neutral')
            
            directions = [sentiment_direction, volume_direction]
            bullish_count = directions.count('Bullish')
            bearish_count = directions.count('Bearish')
            
            if bullish_count > bearish_count:
                context['overall_bias'] = 'Bullish'
            elif bearish_count > bullish_count:
                context['overall_bias'] = 'Bearish'
            else:
                context['overall_bias'] = 'Mixed'
            
            # Determine market regime
            calendar_impact = analysis_result.get('calendar_impact', {})
            high_impact_events = calendar_impact.get('high_impact_events', 0)
            
            if high_impact_events > 1:
                context['market_regime'] = 'High Volatility'
            elif analysis_result.get('volume_boost', 0) > 8:
                context['market_regime'] = 'Institutional Activity'
            elif analysis_result.get('sentiment_boost', 0) > 10:
                context['market_regime'] = 'News Driven'
            else:
                context['market_regime'] = 'Normal'
            
            # Key factors
            if analysis_result.get('sentiment_boost', 0) > 5:
                context['key_factors'].append('Strong news sentiment alignment')
            
            if analysis_result.get('volume_boost', 0) > 5:
                context['key_factors'].append('Smart money flow confirmation')
            
            volume_profile = analysis_result.get('volume_profile', {}).get('volume_profile', {})
            if volume_profile.get('profile_type') in ['P-shaped', 'b-shaped']:
                context['key_factors'].append(f"Strong {volume_profile.get('profile_type')} volume profile")
            
            # Risk factors
            if analysis_result.get('calendar_adjustment', 0) < -5:
                context['risk_factors'].append('Major economic events approaching')
            
            if analysis_result.get('volume_boost', 0) < -3:
                context['risk_factors'].append('Smart money flow divergence')
            
            if analysis_result.get('sentiment_boost', 0) < -3:
                context['risk_factors'].append('Negative sentiment environment')
            
            # Opportunities
            confluence_score = analysis_result.get('enhanced_confluence_score', 0)
            if confluence_score >= 4:
                context['opportunities'].append('High confluence setup')
            
            if context['market_regime'] == 'Institutional Activity':
                context['opportunities'].append('Strong institutional interest')
            
            return context
            
        except Exception as e:
            print(f"Error generating market context: {e}")
            return {'overall_bias': 'Unknown', 'error': str(e)}

# Global enhanced analysis engine
enhanced_engine = EnhancedAnalysisEngine()

async def get_enhanced_confidence_analysis(pair: str, df: pd.DataFrame, 
                                         existing_confidence: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to get enhanced confidence analysis with all advanced features"""
    return await enhanced_engine.get_comprehensive_analysis(pair, df, existing_confidence)

def format_enhanced_analysis_for_discord(analysis: Dict[str, Any]) -> str:
    """Format enhanced analysis data for Discord display"""
    try:
        lines = []
        
        # Market context
        market_context = analysis.get('market_context', {})
        if market_context:
            lines.append(f"🌍 **Market Context:** {market_context.get('overall_bias', 'Unknown')}")
            lines.append(f"📊 **Regime:** {market_context.get('market_regime', 'Normal')}")
        
        # Sentiment analysis
        sentiment = analysis.get('sentiment_analysis', {})
        if sentiment and not sentiment.get('error'):
            direction = sentiment.get('sentiment_direction', 'Neutral')
            emoji = "🟢" if direction == 'Bullish' else "🔴" if direction == 'Bearish' else "🟡"
            lines.append(f"{emoji} **Sentiment:** {direction} ({sentiment.get('sentiment_score', 0):.2f})")
        
        # Smart money flow
        smart_money = analysis.get('volume_profile', {}).get('smart_money_flow', {})
        if smart_money and not smart_money.get('error'):
            flow_direction = smart_money.get('flow_direction', 'Neutral')
            emoji = "💰" if flow_direction != 'Neutral' else "⚖️"
            lines.append(f"{emoji} **Smart Money:** {flow_direction}")
        
        # Volume profile
        volume_profile = analysis.get('volume_profile', {}).get('volume_profile', {})
        if volume_profile and not volume_profile.get('error'):
            profile_type = volume_profile.get('profile_type', 'Unknown')
            lines.append(f"📈 **Volume Profile:** {profile_type}")
        
        # Economic calendar
        calendar = analysis.get('calendar_impact', {})
        if calendar and not calendar.get('error'):
            high_impact = calendar.get('high_impact_events', 0)
            if high_impact > 0:
                lines.append(f"⚠️ **High Impact Events:** {high_impact} in next 24h")
        
        # Enhanced confluence
        confluence = analysis.get('enhanced_confluence_score', 0)
        if confluence > 0:
            lines.append(f"🎯 **Enhanced Confluence:** {confluence} factors")
        
        return "\n".join(lines) if lines else "📊 **Enhanced Analysis:** Not available"
        
    except Exception as e:
        return f"📊 **Enhanced Analysis:** Error - {str(e)}"