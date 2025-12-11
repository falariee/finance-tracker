# Data Directory

This directory contains JSON files for storing trip and expense data.

## File Structure

Each trip is saved as a separate JSON file with the following structure:

```json
{
  "trip": {
    "id": "unique-id",
    "name": "Trip Name",
    "destination": "Location",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "currency": "USD",
    "travelers": [...],
    "created_at": "YYYY-MM-DD HH:MM:SS"
  },
  "expenses": [...]
}
```

See `example.json` for a complete example.
