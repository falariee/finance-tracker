# 📋 Quick Setup Checklist

## Before Deploying to Vercel

- [ ] Create Supabase account at https://supabase.com
- [ ] Create new Supabase project
- [ ] Run the SQL script from DATABASE_SETUP.md in Supabase SQL Editor
- [ ] Copy your Supabase URL and anon key
- [ ] Have your Vercel project URL ready

## In Vercel Dashboard

- [ ] Go to Settings → Environment Variables
- [ ] Add `SUPABASE_URL` = your Supabase project URL
- [ ] Add `SUPABASE_KEY` = your Supabase anon key
- [ ] Add `SECRET_KEY` = any random string (e.g., "trip-tracker-2024-xyz")
- [ ] Click "Redeploy" or push new code to trigger deployment

## Testing After Deployment

### Test 1: Data Persistence
- [ ] Visit your Vercel URL
- [ ] Create a new trip
- [ ] Add 2-3 travelers
- [ ] Add 2-3 expenses
- [ ] Refresh the page
- [ ] ✅ Trip should still be there with all data

### Test 2: Shared Links
- [ ] In your trip, click "Invite Link" button
- [ ] Copy the invite link
- [ ] Open the link in an incognito/private browser window
- [ ] ✅ Trip should load automatically
- [ ] Try adding an expense from the incognito window
- [ ] ✅ It should save and be visible in your original window (after refresh)

### Test 3: Different Browsers/Devices
- [ ] Share link with friend or open on your phone
- [ ] ✅ They should see the same trip
- [ ] ✅ Changes they make should be saved

## If Something Goes Wrong

### Database Warning Shows Up
→ Check that environment variables are correctly set in Vercel
→ Make sure you clicked "Redeploy" after adding them

### Shared Link Shows Empty Page
→ Make sure the trip was saved (add an expense to trigger auto-save)
→ Check Supabase table has data: go to Supabase → Table Editor → trips

### Data Still Lost After Refresh
→ Check browser console for errors (F12)
→ Verify Supabase credentials are correct
→ Make sure RLS policy is enabled (see DATABASE_SETUP.md)

## Next Steps

Once everything is working:
- [ ] Share with your travel group
- [ ] Start tracking real trip expenses
- [ ] Use the currency converter for quick calculations
- [ ] Generate reports to see spending patterns

## Need Help?

1. Check DEPLOYMENT_GUIDE.md for detailed instructions
2. Check DATABASE_SETUP.md for Supabase setup
3. Look at browser console (F12) for error messages
4. Check Vercel deployment logs
5. Verify environment variables are set correctly

---

## 🎉 Success Criteria

Your app is working correctly if:
✅ You can create trips and they persist after refresh
✅ Shared invite links load the trip automatically
✅ Multiple people can access and edit the same trip
✅ Expenses auto-save when added
✅ No "database not configured" warning shows up

---

**Estimated Setup Time:** 10-15 minutes

Good luck! 🚀
