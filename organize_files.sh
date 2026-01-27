#!/bin/bash

# 1_DOCUMENTATION - All analysis, guides, and reports
mv -v COMPREHENSIVE_*.md 1_documentation/ 2>/dev/null || true
mv -v FINAL_*.md 1_documentation/ 2>/dev/null || true
mv -v PHASE_*.md 1_documentation/ 2>/dev/null || true
mv -v PROJECT_*.md 1_documentation/ 2>/dev/null || true
mv -v README_*.md 1_documentation/ 2>/dev/null || true
mv -v SESSION_*.md 1_documentation/ 2>/dev/null || true
mv -v VISUAL_SUMMARY.md 1_documentation/ 2>/dev/null || true
mv -v EXECUTIVE_SUMMARY.md 1_documentation/ 2>/dev/null || true
mv -v QUICK_*.md 1_documentation/ 2>/dev/null || true
mv -v IMPLEMENTATION_CHECKLIST.md 1_documentation/ 2>/dev/null || true
mv -v DEPLOYMENT_CHECKLIST.md 1_documentation/ 2>/dev/null || true
mv -v DOCUMENTATION_INDEX.md 1_documentation/ 2>/dev/null || true
mv -v LOW_PRIORITY_*.md 1_documentation/ 2>/dev/null || true
mv -v OPTION_A_*.md 1_documentation/ 2>/dev/null || true
mv -v api_setup_guide.md 1_documentation/ 2>/dev/null || true
mv -v pricing_documentation.md 1_documentation/ 2>/dev/null || true

# 2_CORE_SYSTEM - Main trading bot and unified systems
mv -v main.py 2_core_system/ 2>/dev/null || true
mv -v unified_confidence_system.py 2_core_system/ 2>/dev/null || true
mv -v trade_manager_system.py 2_core_system/ 2>/dev/null || true
mv -v binary_options_trade_manager.py 2_core_system/ 2>/dev/null || true
mv -v bot_signal_wrapper.py 2_core_system/ 2>/dev/null || true
mv -v phase3_enhanced_signals.py 2_core_system/ 2>/dev/null || true

# 3_SIGNAL_ANALYSIS - Signal generation and analysis modules
mv -v advanced_liquidity_analysis.py 3_signal_analysis/ 2>/dev/null || true
mv -v advanced_signal_integration.py 3_signal_analysis/ 2>/dev/null || true
mv -v advanced_volume_analysis.py 3_signal_analysis/ 2>/dev/null || true
mv -v analysis_integration_pipeline.py 3_signal_analysis/ 2>/dev/null || true
mv -v cross_timeframe_signal_validation.py 3_signal_analysis/ 2>/dev/null || true
mv -v direction_reversal_detection.py 3_signal_analysis/ 2>/dev/null || true
mv -v enhanced_analysis_integration.py 3_signal_analysis/ 2>/dev/null || true
mv -v enhanced_confluence_analyzer.py 3_signal_analysis/ 2>/dev/null || true
mv -v enhanced_embed_creators.py 3_signal_analysis/ 2>/dev/null || true
mv -v enhanced_smc_ict_analysis.py 3_signal_analysis/ 2>/dev/null || true
mv -v false_breakout_strategy.py 3_signal_analysis/ 2>/dev/null || true
mv -v improved_fvg_analysis.py 3_signal_analysis/ 2>/dev/null || true
mv -v market_microstructure_analysis.py 3_signal_analysis/ 2>/dev/null || true
mv -v order_flow_imbalance_detection.py 3_signal_analysis/ 2>/dev/null || true
mv -v ranging_trending_systems.py 3_signal_analysis/ 2>/dev/null || true
mv -v seasonal_cyclical_pattern_recognition.py 3_signal_analysis/ 2>/dev/null || true
mv -v seasonal_pattern_analyzer.py 3_signal_analysis/ 2>/dev/null || true
mv -v signal_decay_detection.py 3_signal_analysis/ 2>/dev/null || true
mv -v breakout_validation_system.py 3_signal_analysis/ 2>/dev/null || true

# 4_BACKTESTING - Backtesting frameworks and validators
mv -v twelvedata_backtester.py 4_backtesting/ 2>/dev/null || true
mv -v walk_forward_backtester.py 4_backtesting/ 2>/dev/null || true
mv -v signal_backtester.py 4_backtesting/ 2>/dev/null || true
mv -v demo_backtester_simple.py 4_backtesting/ 2>/dev/null || true
mv -v validate_*.py 4_backtesting/ 2>/dev/null || true
mv -v professional_validation.py 4_backtesting/ 2>/dev/null || true

# 5_CONFIGURATION - Config files and API setup
mv -v api_config.json 5_configuration/ 2>/dev/null || true
mv -v proxies.json 5_configuration/ 2>/dev/null || true
mv -v selected_params.json 5_configuration/ 2>/dev/null || true
mv -v parameter_search*.json 5_configuration/ 2>/dev/null || true
mv -v pyproject.toml 5_configuration/ 2>/dev/null || true
mv -v .env 5_configuration/ 2>/dev/null || true
mv -v .gitignore 5_configuration/ 2>/dev/null || true

# 6_UTILITIES - Helper modules and utilities
mv -v safe_math_utils.py 6_utilities/ 2>/dev/null || true
mv -v improved_trade_calculator.py 6_utilities/ 2>/dev/null || true
mv -v trade_calculator.py 6_utilities/ 2>/dev/null || true
mv -v EnhancedAPIRotation.py 6_utilities/ 2>/dev/null || true
mv -v stealth_api_client.py 6_utilities/ 2>/dev/null || true
mv -v forex_factory_api.py 6_utilities/ 2>/dev/null || true
mv -v alternative_data_source.py 6_utilities/ 2>/dev/null || true
mv -v interaction_timeout_handler.py 6_utilities/ 2>/dev/null || true
mv -v persistent_interactions.py 6_utilities/ 2>/dev/null || true
mv -v processing_efficiency.py 6_utilities/ 2>/dev/null || true
mv -v trade_manager_ui_components.py 6_utilities/ 2>/dev/null || true
mv -v legal_enforcement.py 6_utilities/ 2>/dev/null || true
mv -v test_signal_debug.py 6_utilities/ 2>/dev/null || true

# 7_LEGACY - ML and optimization modules (legacy/experimental)
mv -v binary_options_ml_predictor.py 7_legacy/ 2>/dev/null || true
mv -v ml_ensemble_engine.py 7_legacy/ 2>/dev/null || true
mv -v ml_ensemble_signals.py 7_legacy/ 2>/dev/null || true
mv -v portfolio_optimizer.py 7_legacy/ 2>/dev/null || true
mv -v statistical_robustness_system.py 7_legacy/ 2>/dev/null || true
mv -v winrate_optimization.py 7_legacy/ 2>/dev/null || true
mv -v small_capital_analysis.py 7_legacy/ 2>/dev/null || true
mv -v expand_params_to_all_pairs.py 7_legacy/ 2>/dev/null || true
mv -v parameter_search.py 7_legacy/ 2>/dev/null || true
mv -v run_selected_params.py 7_legacy/ 2>/dev/null || true
mv -v data_downloader.py 7_legacy/ 2>/dev/null || true

# 8_DATA - Data files
mv -v *.csv 8_data/ 2>/dev/null || true
mv -v data_download_summary.json 8_data/ 2>/dev/null || true
mv -v seasonal_analysis_usd_cad.json 8_data/ 2>/dev/null || true

# 9_RESULTS - Backtest results and logs
mv -v backtest_results*.json 9_results/ 2>/dev/null || true
mv -v walk_forward_*.* 9_results/ 2>/dev/null || true
mv -v selected_params_results.json 9_results/ 2>/dev/null || true
mv -v usd_cad_phase3_*.* 9_results/ 2>/dev/null || true
mv -v *.log 9_results/ 2>/dev/null || true
mv -v *.db 9_results/ 2>/dev/null || true
mv -v *.db-shm 9_results/ 2>/dev/null || true
mv -v *.png 9_results/ 2>/dev/null || true

# Move Policy/Legal documents to docs
mv -v TERMS_OF_SERVICE.md 1_documentation/ 2>/dev/null || true
mv -v PRIVACY_POLICY.md 1_documentation/ 2>/dev/null || true
mv -v USER_CONDUCT_POLICY.md 1_documentation/ 2>/dev/null || true
mv -v DISCORD_INTRODUCTION.md 1_documentation/ 2>/dev/null || true
mv -v PREMIUM_VS_FREEMIUM_GUIDE.md 1_documentation/ 2>/dev/null || true

echo "✅ Files organized successfully!"
