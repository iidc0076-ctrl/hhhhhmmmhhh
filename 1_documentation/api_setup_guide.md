# QuantVision API Setup Guide

## API Integration for Real-Time Backtesting

To enable real market data in the QuantVision backtesting system, you need to configure API keys for the following services:

### Required API Services

#### 1. TwelveData (Primary Market Data)
- **Purpose**: Real-time and historical forex data
- **Website**: https://twelvedata.com/
- **Plans**: Free tier available (800 requests/day)
- **Required**: `TWELVEDATA_API_KEY`

#### 2. Polygon.io (Alternative Market Data)
- **Purpose**: High-quality market data backup
- **Website**: https://polygon.io/
- **Plans**: Free tier available (5 calls/minute)
- **Required**: `POLYGON_API_KEY`

#### 3. Finnhub (News and Sentiment Data)
- **Purpose**: Market news and sentiment analysis
- **Website**: https://finnhub.io/
- **Plans**: Free tier available (60 calls/minute)
- **Required**: `FINNHUB_API_KEY`

### Environment Configuration

Create or update your `.env` file with the following API keys:

```env
# Market Data APIs
TWELVEDATA_API_KEY=your_twelvedata_api_key_here
POLYGON_API_KEY=your_polygon_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here

# Optional: Additional Data Sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FXCM_API_KEY=your_fxcm_key_here

# Database Configuration (Already configured)
DATABASE_URL=your_postgresql_url
PGHOST=your_pg_host
PGPORT=your_pg_port
PGUSER=your_pg_user
PGPASSWORD=your_pg_password
PGDATABASE=your_pg_database

# Discord Bot (For notifications)
DISCORD_BOT_TOKEN=your_discord_bot_token
```

### Getting API Keys

#### TwelveData Setup
1. Visit https://twelvedata.com/
2. Sign up for a free account
3. Navigate to API section
4. Copy your API key
5. Add to `.env` as `TWELVEDATA_API_KEY`

#### Polygon.io Setup
1. Visit https://polygon.io/
2. Create free account
3. Go to Dashboard → API Keys
4. Copy your API key
5. Add to `.env` as `POLYGON_API_KEY`

#### Finnhub Setup
1. Visit https://finnhub.io/
2. Register for free account
3. Go to Dashboard
4. Copy API key
5. Add to `.env` as `FINNHUB_API_KEY`

### Testing API Configuration

Run this command to test your API setup:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

apis = ['TWELVEDATA_API_KEY', 'POLYGON_API_KEY', 'FINNHUB_API_KEY']
for api in apis:
    status = '✅ Configured' if os.getenv(api) else '❌ Missing'
    print(f'{api}: {status}')
"
```

### Running Real-Data Backtests

Once APIs are configured, run comprehensive backtests with real data:

```bash
# Run full backtesting suite with real APIs
python run_backtests.py

# Run individual component tests
python module_backtester.py

# Run main comprehensive backtest
python backtester.py
```

### API Rate Limits and Usage

#### TwelveData Free Tier
- 800 requests per day
- Real-time and historical data
- Perfect for backtesting

#### Polygon.io Free Tier
- 5 calls per minute
- 2 years historical data
- Excellent data quality

#### Finnhub Free Tier
- 60 calls per minute
- News and economic data
- Real-time sentiment

### Troubleshooting

#### Common Issues

1. **API Key Not Working**
   - Verify key is correctly copied
   - Check account status on provider website
   - Ensure no extra spaces in `.env` file

2. **Rate Limit Exceeded**
   - Reduce request frequency
   - Consider upgrading to paid plan
   - Implement request caching

3. **Data Quality Issues**
   - Compare data across multiple sources
   - Check data timestamps
   - Verify market hours

#### Error Messages

- `"API key invalid"` → Check key format and account status
- `"Rate limit exceeded"` → Wait or upgrade plan
- `"No data available"` → Check symbol format and market hours

### Production Deployment

For production deployment with real trading:

1. **Upgrade API Plans**: Free tiers for development only
2. **Monitor Usage**: Track API call consumption
3. **Implement Caching**: Reduce redundant API calls
4. **Set Alerts**: Monitor for API failures
5. **Backup Sources**: Configure multiple data providers

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate keys regularly** 
4. **Monitor API usage** for unauthorized access
5. **Use least privilege** access levels

---

*Once configured, the QuantVision system will automatically use real market data for all backtesting and signal generation operations.*