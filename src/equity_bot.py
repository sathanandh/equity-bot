# .github/workflows/equity-bot.yml
name: 🚀 Equity Bot - Scheduled Analysis

on:
  # 🕐 CRON: Runs at 9 AM and 6 PM UTC daily (adjust as needed)
  schedule:
    - cron: '0 9,18 * * *'
  
  # 🧪 Manual trigger for testing
  workflow_dispatch:
    inputs:
      debug_mode:
        description: 'Enable verbose logging'
        required: false
        default: 'false'
        type: boolean

permissions:
  contents: read

jobs:
  run-equity-bot:
    runs-on: ubuntu-latest
    timeout-minutes: 180
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: 'src/requirements.txt'
      
      - name: 🔧 Install system packages
        run: |
          sudo apt-get update
          sudo apt-get install -y poppler-utils tesseract-ocr
      
      - name: 📦 Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r src/requirements.txt
      
      - name: 🤖 Execute Equity Bot
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          TELEGRAM_STRING_SESSION: ${{ secrets.TELEGRAM_STRING_SESSION }}
          TELEGRAM_API_ID: ${{ secrets.TELEGRAM_API_ID }}
          TELEGRAM_API_HASH: ${{ secrets.TELEGRAM_API_HASH }}
          GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
          DRIVE_FOLDER_ID: ${{ secrets.DRIVE_FOLDER_ID }}
          DEBUG_MODE: ${{ inputs.debug_mode || 'false' }}
        run: |
          echo "🚀 Starting Equity Bot at $(date -u)"
          python src/equity_bot.py
          echo "✅ Bot completed at $(date -u)"
      
      - name: 📤 Upload logs (if failed)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: equity-bot-logs-${{ github.run_number }}
          path: /tmp/equity-bot/
          retention-days: 7