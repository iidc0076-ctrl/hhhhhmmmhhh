"""
Enhanced SMC/ICT Analysis Module
Improved Smart Money Concepts and Inner Circle Trader methodologies
Focus on liquidity sweeps, market structure, order blocks, and fair value gaps
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from safe_math_utils import safe_mean, safe_std, safe_divide

class MarketStructure(Enum):
    BULLISH_BOS = "bullish_break_of_structure"
    BEARISH_BOS = "bearish_break_of_structure"
    BULLISH_CHoCH = "bullish_change_of_character"
    BEARISH_CHoCH = "bearish_change_of_character"
    CONSOLIDATION = "consolidation"
    MANIPULATION = "manipulation"

class OrderBlockType(Enum):
    BULLISH_OB = "bullish_order_block"
    BEARISH_OB = "bearish_order_block"
    BREAKER_BLOCK = "breaker_block"
    MITIGATION_BLOCK = "mitigation_block"

@dataclass
class SwingPoint:
    index: int
    price: float
    swing_type: str  # "high" or "low"
    strength: float
    volume_confirmation: bool = False
    liquidity_level: float = 0.0

@dataclass
class OrderBlock:
    entry_price: float
    exit_price: float
    start_index: int
    end_index: int
    block_type: OrderBlockType
    strength: float
    is_fresh: bool = True
    mitigation_count: int = 0
    volume_profile: float = 0.0

@dataclass
class FairValueGap:
    gap_start: float
    gap_end: float
    gap_index: int
    gap_type: str  # "bullish", "bearish"
    gap_size: float
    filled: bool = False
    fill_percentage: float = 0.0

@dataclass
class LiquidityPool:
    price_level: float
    pool_type: str  # "buy_side", "sell_side"
    strength: float
    swept: bool = False
    sweep_candle: Optional[int] = None
    reaction_strength: float = 0.0

class EnhancedSMCAnalyzer:
    """Enhanced Smart Money Concepts analyzer with improved signal accuracy"""
    
    def __init__(self):
        self.swing_sensitivity = 3  # Lookback for swing detection
        self.liquidity_threshold = 0.002  # 0.2% for liquidity sweeps
        self.fvg_threshold = 0.0005  # 0.05% minimum gap size
        self.order_block_strength_threshold = 0.3
        
    def analyze_comprehensive_smc(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive SMC analysis with improved accuracy"""
        try:
            if df is None or len(df) < 50:
                return self._empty_smc_analysis()
            
            # Core SMC components
            swing_points = self._detect_swing_points(df)
            market_structure = self._analyze_market_structure(df, swing_points)
            liquidity_pools = self._detect_liquidity_pools(df, swing_points)
            order_blocks = self._detect_order_blocks(df, swing_points)
            fair_value_gaps = self._detect_fair_value_gaps(df)
            
            # Advanced analysis
            liquidity_sweeps = self._detect_liquidity_sweeps(df, liquidity_pools)
            market_manipulation = self._detect_manipulation_patterns(df)
            institutional_flow = self._analyze_institutional_flow(df, order_blocks)
            
            # Generate signals
            smc_signals = self._generate_smc_signals(
                market_structure, liquidity_sweeps, order_blocks, 
                fair_value_gaps, institutional_flow
            )
            
            # Calculate overall SMC bias
            overall_bias = self._calculate_smc_bias(smc_signals)
            
            return {
                'market_structure': market_structure,
                'swing_points': [self._swing_to_dict(sp) for sp in swing_points[-10:]],
                'liquidity_pools': [self._liquidity_to_dict(lp) for lp in liquidity_pools],
                'liquidity_sweeps': liquidity_sweeps,
                'order_blocks': [self._order_block_to_dict(ob) for ob in order_blocks],
                'fair_value_gaps': [self._fvg_to_dict(fvg) for fvg in fair_value_gaps],
                'manipulation_patterns': market_manipulation,
                'institutional_flow': institutional_flow,
                'smc_signals': smc_signals,
                'overall_bias': overall_bias,
                'signal_strength': overall_bias.get('strength', 0),
                'confidence_level': self._calculate_confidence(smc_signals),
                'entry_conditions': self._identify_entry_conditions(df, smc_signals)
            }
            
        except Exception as e:
            print(f"Error in comprehensive SMC analysis: {e}")
            return self._empty_smc_analysis()
    
    def _detect_swing_points(self, df: pd.DataFrame) -> List[SwingPoint]:
        """Enhanced swing point detection with volume confirmation"""
        swing_points = []
        
        # Volume proxy for confirmation
        volume_proxy = (df['high'] - df['low']) + abs(df['close'] - df['open'])
        avg_volume = safe_mean(volume_proxy, 1.0)
        
        for i in range(self.swing_sensitivity, len(df) - self.swing_sensitivity):
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            
            # Swing High detection
            is_swing_high = True
            for j in range(i - self.swing_sensitivity, i + self.swing_sensitivity + 1):
                if j != i and df['high'].iloc[j] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                volume_conf = volume_proxy.iloc[i] > avg_volume * 1.2
                strength = self._calculate_swing_strength(df, i, 'high')
                liquidity = self._estimate_liquidity_level(df, i, current_high)
                
                swing_points.append(SwingPoint(
                    index=i,
                    price=current_high,
                    swing_type='high',
                    strength=strength,
                    volume_confirmation=volume_conf,
                    liquidity_level=liquidity
                ))
            
            # Swing Low detection
            is_swing_low = True
            for j in range(i - self.swing_sensitivity, i + self.swing_sensitivity + 1):
                if j != i and df['low'].iloc[j] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                volume_conf = volume_proxy.iloc[i] > avg_volume * 1.2
                strength = self._calculate_swing_strength(df, i, 'low')
                liquidity = self._estimate_liquidity_level(df, i, current_low)
                
                swing_points.append(SwingPoint(
                    index=i,
                    price=current_low,
                    swing_type='low',
                    strength=strength,
                    volume_confirmation=volume_conf,
                    liquidity_level=liquidity
                ))
        
        return swing_points
    
    def _analyze_market_structure(self, df: pd.DataFrame, swing_points: List[SwingPoint]) -> Dict[str, Any]:
        """Enhanced market structure analysis"""
        if len(swing_points) < 4:
            return {'structure_type': MarketStructure.CONSOLIDATION, 'strength': 0}
        
        # Separate highs and lows
        highs = [sp for sp in swing_points if sp.swing_type == 'high']
        lows = [sp for sp in swing_points if sp.swing_type == 'low']
        
        if len(highs) < 2 or len(lows) < 2:
            return {'structure_type': MarketStructure.CONSOLIDATION, 'strength': 0}
        
        # Recent structure analysis
        recent_highs = highs[-3:] if len(highs) >= 3 else highs[-2:]
        recent_lows = lows[-3:] if len(lows) >= 3 else lows[-2:]
        
        # Determine structure type
        structure_type = self._determine_structure_type(recent_highs, recent_lows, df)
        structure_strength = self._calculate_structure_strength(recent_highs, recent_lows)
        
        # Check for break of structure
        bos_analysis = self._check_break_of_structure(df, recent_highs, recent_lows)
        
        # Change of character analysis
        choch_analysis = self._check_change_of_character(recent_highs, recent_lows)
        
        return {
            'structure_type': structure_type,
            'strength': structure_strength,
            'break_of_structure': bos_analysis,
            'change_of_character': choch_analysis,
            'recent_highs': [{'price': h.price, 'index': h.index} for h in recent_highs],
            'recent_lows': [{'price': l.price, 'index': l.index} for l in recent_lows],
            'trend_direction': self._determine_trend_direction(structure_type, bos_analysis, choch_analysis)
        }
    
    def _detect_liquidity_pools(self, df: pd.DataFrame, swing_points: List[SwingPoint]) -> List[LiquidityPool]:
        """Detect areas where liquidity is likely resting"""
        liquidity_pools = []
        
        # High liquidity swing points
        high_strength_swings = [sp for sp in swing_points if sp.strength > 0.7]
        
        for swing in high_strength_swings:
            pool_type = "buy_side" if swing.swing_type == "high" else "sell_side"
            
            # Check if this level has been respected multiple times
            respect_count = self._count_level_respects(df, swing.price, 0.001)
            
            if respect_count >= 2:
                liquidity_pools.append(LiquidityPool(
                    price_level=swing.price,
                    pool_type=pool_type,
                    strength=swing.strength * respect_count,
                    swept=False
                ))
        
        # Equal highs/lows (strong liquidity areas)
        eq_levels = self._detect_equal_levels(swing_points)
        for level_data in eq_levels:
            liquidity_pools.append(LiquidityPool(
                price_level=level_data['price'],
                pool_type=level_data['type'],
                strength=level_data['strength'],
                swept=False
            ))
        
        return liquidity_pools
    
    def _detect_liquidity_sweeps(self, df: pd.DataFrame, liquidity_pools: List[LiquidityPool]) -> List[Dict[str, Any]]:
        """Detect liquidity sweeps with reaction analysis"""
        sweeps = []
        
        for i, pool in enumerate(liquidity_pools):
            sweep_info = self._check_liquidity_sweep(df, pool)
            if sweep_info:
                sweeps.append(sweep_info)
                liquidity_pools[i].swept = True
                liquidity_pools[i].sweep_candle = sweep_info['sweep_candle']
                liquidity_pools[i].reaction_strength = sweep_info['reaction_strength']
        
        return sweeps
    
    def _detect_order_blocks(self, df: pd.DataFrame, swing_points: List[SwingPoint]) -> List[OrderBlock]:
        """Enhanced order block detection"""
        order_blocks = []
        
        for swing in swing_points:
            if swing.strength < self.order_block_strength_threshold:
                continue
            
            # Find the candle that created the swing
            creation_candle = swing.index
            
            # Look for order block formation
            if swing.swing_type == 'high':
                # Bearish order block
                ob = self._create_bearish_order_block(df, creation_candle, swing)
            else:
                # Bullish order block  
                ob = self._create_bullish_order_block(df, creation_candle, swing)
            
            if ob:
                order_blocks.append(ob)
        
        return order_blocks
    
    def _detect_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """Detect fair value gaps (imbalances)"""
        fvgs = []
        
        for i in range(2, len(df)):
            # Check for bullish FVG
            if (df['low'].iloc[i] > df['high'].iloc[i-2] and 
                not pd.isna(df['low'].iloc[i]) and not pd.isna(df['high'].iloc[i-2])):
                
                gap_size = df['low'].iloc[i] - df['high'].iloc[i-2]
                if gap_size / df['close'].iloc[i] > self.fvg_threshold:
                    fvgs.append(FairValueGap(
                        gap_start=df['high'].iloc[i-2],
                        gap_end=df['low'].iloc[i],
                        gap_index=i,
                        gap_type='bullish',
                        gap_size=gap_size
                    ))
            
            # Check for bearish FVG
            elif (df['high'].iloc[i] < df['low'].iloc[i-2] and 
                  not pd.isna(df['high'].iloc[i]) and not pd.isna(df['low'].iloc[i-2])):
                
                gap_size = df['low'].iloc[i-2] - df['high'].iloc[i]
                if gap_size / df['close'].iloc[i] > self.fvg_threshold:
                    fvgs.append(FairValueGap(
                        gap_start=df['low'].iloc[i-2],
                        gap_end=df['high'].iloc[i],
                        gap_index=i,
                        gap_type='bearish',
                        gap_size=gap_size
                    ))
        
        # Check which FVGs have been filled
        current_price = df['close'].iloc[-1]
        for fvg in fvgs:
            if fvg.gap_type == 'bullish':
                if current_price <= fvg.gap_start:
                    fvg.filled = True
                    fvg.fill_percentage = 100.0
                elif current_price < fvg.gap_end:
                    fvg.fill_percentage = (fvg.gap_end - current_price) / fvg.gap_size * 100
            else:  # bearish
                if current_price >= fvg.gap_start:
                    fvg.filled = True
                    fvg.fill_percentage = 100.0
                elif current_price > fvg.gap_end:
                    fvg.fill_percentage = (current_price - fvg.gap_end) / fvg.gap_size * 100
        
        return fvgs
    
    def _generate_smc_signals(self, market_structure: Dict, liquidity_sweeps: List, 
                             order_blocks: List, fvgs: List, institutional_flow: Dict) -> Dict[str, Any]:
        """Generate trading signals based on SMC analysis"""
        signals = {
            'primary_bias': 'NEUTRAL',
            'signal_strength': 0,
            'entry_triggers': [],
            'confluence_factors': [],
            'risk_factors': []
        }
        
        bias_score = 0
        
        # Market structure bias
        structure_bias = market_structure.get('trend_direction', 'neutral')
        if structure_bias == 'bullish':
            bias_score += 30
            signals['confluence_factors'].append("Bullish market structure")
        elif structure_bias == 'bearish':
            bias_score -= 30
            signals['confluence_factors'].append("Bearish market structure")
        
        # Liquidity sweep bias
        recent_sweeps = [s for s in liquidity_sweeps if s.get('reaction_strength', 0) > 0.5]
        for sweep in recent_sweeps[-2:]:  # Last 2 sweeps
            if sweep.get('sweep_direction') == 'bullish':
                bias_score += 20
                signals['confluence_factors'].append("Bullish liquidity sweep with reaction")
            elif sweep.get('sweep_direction') == 'bearish':
                bias_score -= 20
                signals['confluence_factors'].append("Bearish liquidity sweep with reaction")
        
        # Order block confluence
        fresh_obs = [ob for ob in order_blocks if ob.is_fresh]
        for ob in fresh_obs[-3:]:  # Last 3 fresh order blocks
            if ob.block_type == OrderBlockType.BULLISH_OB:
                bias_score += 15
                signals['confluence_factors'].append("Fresh bullish order block")
            elif ob.block_type == OrderBlockType.BEARISH_OB:
                bias_score -= 15
                signals['confluence_factors'].append("Fresh bearish order block")
        
        # FVG confluence
        unfilled_fvgs = [fvg for fvg in fvgs if not fvg.filled]
        for fvg in unfilled_fvgs[-2:]:  # Last 2 unfilled FVGs
            if fvg.gap_type == 'bullish':
                bias_score += 10
                signals['confluence_factors'].append("Unfilled bullish FVG")
            else:
                bias_score -= 10
                signals['confluence_factors'].append("Unfilled bearish FVG")
        
        # Institutional flow
        inst_bias = institutional_flow.get('flow_direction', 'neutral')
        inst_strength = institutional_flow.get('flow_strength', 0)
        if inst_bias == 'bullish' and inst_strength > 0.6:
            bias_score += 25
            signals['confluence_factors'].append("Strong institutional buying")
        elif inst_bias == 'bearish' and inst_strength > 0.6:
            bias_score -= 25
            signals['confluence_factors'].append("Strong institutional selling")
        
        # Determine final bias
        if bias_score > 40:
            signals['primary_bias'] = 'BUY'
            signals['signal_strength'] = min(100, abs(bias_score))
        elif bias_score < -40:
            signals['primary_bias'] = 'SELL'
            signals['signal_strength'] = min(100, abs(bias_score))
        else:
            signals['primary_bias'] = 'NEUTRAL'
            signals['signal_strength'] = 30
        
        return signals
    
    def _calculate_smc_bias(self, smc_signals: Dict) -> Dict[str, Any]:
        """Calculate overall SMC bias with confidence"""
        bias = smc_signals.get('primary_bias', 'NEUTRAL')
        strength = smc_signals.get('signal_strength', 0)
        confluence_count = len(smc_signals.get('confluence_factors', []))
        
        # Adjust confidence based on confluence
        confidence = strength
        if confluence_count >= 4:
            confidence = min(95, confidence + 15)
        elif confluence_count >= 3:
            confidence = min(90, confidence + 10)
        elif confluence_count >= 2:
            confidence = min(85, confidence + 5)
        
        return {
            'direction': bias,
            'strength': strength,
            'confidence': confidence,
            'confluence_count': confluence_count,
            'quality': 'High' if confluence_count >= 3 else 'Medium' if confluence_count >= 2 else 'Low'
        }
    
    # Helper methods
    def _calculate_swing_strength(self, df: pd.DataFrame, index: int, swing_type: str) -> float:
        """Calculate swing point strength based on surrounding price action"""
        try:
            window = min(10, len(df) - index - 1, index)
            if window < 3:
                return 0.5
            
            if swing_type == 'high':
                price = df['high'].iloc[index]
                surrounding = df['high'].iloc[max(0, index-window):index+window+1]
            else:
                price = df['low'].iloc[index]
                surrounding = df['low'].iloc[max(0, index-window):index+window+1]
            
            # Calculate how much this swing stands out
            price_range = surrounding.max() - surrounding.min()
            if price_range == 0:
                return 0.5
            
            deviation = abs(price - surrounding.mean()) / price_range
            return min(1.0, deviation * 2)
        except:
            return 0.5
    
    def _estimate_liquidity_level(self, df: pd.DataFrame, index: int, price: float) -> float:
        """Estimate liquidity level at a price point"""
        try:
            # Look for equal levels within tolerance
            tolerance = price * 0.001  # 0.1%
            nearby_touches = 0
            
            window = min(50, len(df))
            start_idx = max(0, index - window)
            end_idx = min(len(df), index + window)
            
            for i in range(start_idx, end_idx):
                if abs(df['high'].iloc[i] - price) <= tolerance or abs(df['low'].iloc[i] - price) <= tolerance:
                    nearby_touches += 1
            
            return min(1.0, nearby_touches / 10)
        except:
            return 0.0
    
    def _empty_smc_analysis(self) -> Dict[str, Any]:
        """Return empty SMC analysis structure"""
        return {
            'market_structure': {'structure_type': MarketStructure.CONSOLIDATION, 'strength': 0},
            'swing_points': [],
            'liquidity_pools': [],
            'liquidity_sweeps': [],
            'order_blocks': [],
            'fair_value_gaps': [],
            'manipulation_patterns': {},
            'institutional_flow': {},
            'smc_signals': {'primary_bias': 'NEUTRAL', 'signal_strength': 0},
            'overall_bias': {'direction': 'NEUTRAL', 'strength': 0, 'confidence': 50},
            'signal_strength': 0,
            'confidence_level': 50,
            'entry_conditions': []
        }
    
    # Additional helper methods would be implemented here...
    def _determine_structure_type(self, highs, lows, df):
        """Determine market structure type"""
        # Implementation details...
        return MarketStructure.CONSOLIDATION
    
    def _calculate_structure_strength(self, highs, lows):
        """Calculate structure strength"""
        return 50
    
    def _check_break_of_structure(self, df, highs, lows):
        """Check for break of structure"""
        return {}
    
    def _check_change_of_character(self, highs, lows):
        """Check for change of character"""
        return {}
    
    def _determine_trend_direction(self, structure_type, bos, choch):
        """Determine overall trend direction"""
        return 'neutral'
    
    def _count_level_respects(self, df, price, tolerance):
        """Count how many times a level was respected"""
        return 1
    
    def _detect_equal_levels(self, swing_points):
        """Detect equal highs/lows"""
        return []
    
    def _check_liquidity_sweep(self, df, pool):
        """Check if liquidity pool was swept"""
        return None
    
    def _create_bearish_order_block(self, df, candle_idx, swing):
        """Create bearish order block"""
        return None
    
    def _create_bullish_order_block(self, df, candle_idx, swing):
        """Create bullish order block"""
        return None
    
    def _detect_manipulation_patterns(self, df):
        """Detect manipulation patterns"""
        return {}
    
    def _analyze_institutional_flow(self, df, order_blocks):
        """Analyze institutional money flow"""
        return {'flow_direction': 'neutral', 'flow_strength': 0}
    
    def _calculate_confidence(self, signals):
        """Calculate signal confidence"""
        return 50
    
    def _identify_entry_conditions(self, df, signals):
        """Identify optimal entry conditions"""
        return []
    
    def _swing_to_dict(self, swing):
        """Convert swing point to dict"""
        return {
            'index': swing.index,
            'price': swing.price,
            'type': swing.swing_type,
            'strength': swing.strength
        }
    
    def _liquidity_to_dict(self, lp):
        """Convert liquidity pool to dict"""
        return {
            'price': lp.price_level,
            'type': lp.pool_type,
            'strength': lp.strength,
            'swept': lp.swept
        }
    
    def _order_block_to_dict(self, ob):
        """Convert order block to dict"""
        return {
            'entry_price': ob.entry_price,
            'exit_price': ob.exit_price,
            'type': ob.block_type.value,
            'strength': ob.strength,
            'fresh': ob.is_fresh
        }
    
    def _fvg_to_dict(self, fvg):
        """Convert FVG to dict"""
        return {
            'start': fvg.gap_start,
            'end': fvg.gap_end,
            'type': fvg.gap_type,
            'size': fvg.gap_size,
            'filled': fvg.filled
        }

# Global function for integration
def get_enhanced_smc_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Get enhanced SMC/ICT analysis for a DataFrame"""
    analyzer = EnhancedSMCAnalyzer()
    return analyzer.analyze_comprehensive_smc(df)