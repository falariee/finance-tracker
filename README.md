# 🌍 Trip Finance Tracker

A web-based application to track and manage expenses during trips with your travel companions. Share trip links, split expenses fairly, and keep everyone on the same page!

## ✨ Features

- 🎯 **Easy Trip Creation** - Set up trips with destinations, dates, and currency
- 👥 **Collaborative** - Share invite links with travel companions (no login required)
- 💰 **Multi-Currency Support** - Track expenses in different currencies with live conversion
- 📊 **Smart Expense Splitting** - Automatically calculate who owes what
- 📈 **Visual Reports** - Category breakdowns, per-person summaries, and more
- 💾 **Persistent Storage** - Data saved to database (survives page refreshes)
- 📤 **Export Options** - Download as Excel or PDF summary
- 🔄 **Real-time Currency Converter** - Built-in converter with saved calculations

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Visit http://localhost:5000
```

### Deploy to Vercel

1. **Set up database** (Required for production):
   - Follow [DATABASE_SETUP.md](DATABASE_SETUP.md)
   - Configure Supabase (free tier)

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Configure Environment Variables** in Vercel:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase anon key
   - `SECRET_KEY` - Any random string

4. **Done!** Share your trip links with friends 🎉

📖 **Full deployment guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🔧 Recent Fixes

### ✅ Fixed: Shared Links Not Working
- Users can now join trips automatically via shared links
- No authentication required
- Works seamlessly across devices and browsers

### ✅ Fixed: Data Lost on Page Refresh
- Integrated Supabase database for persistent storage
- Auto-saves all changes
- Data survives serverless cold starts
- Graceful fallback mode if database not configured

## Project Structure

- `main.py` - Main application entry point
- `models/` - Data models for expenses, trips, travelers
- `services/` - Business logic for expense tracking
- `utils/` - Helper functions and utilities
- `data/` - Local data storage (JSON files)
- `reports/` - Generated reports and exports

## Quick Start

1. Create a new trip
2. Add travelers
3. Start adding expenses
4. View summaries and reports
5. Export data as needed
