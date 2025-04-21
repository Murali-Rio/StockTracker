# Stock Tracker Application

A comprehensive stock tracking and analysis application built with Streamlit.

## Features

- Real-time stock data tracking
- Technical analysis with multiple indicators
- Stock comparison tool
- Portfolio management
- News and sentiment analysis

## Deployment Instructions

### Prerequisites
- Python 3.8 or higher
- Git
- Streamlit Cloud account (free)

### Local Development

1. Clone the repository:
```bash
git clone <your-repository-url>
cd StockTracker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run Home.py
```

### Deploying to Streamlit Cloud

1. Push your code to GitHub:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repository
5. Set the main file path to `Home.py`
6. Click "Deploy"

## Project Structure

```
StockTracker/
├── pages/
│   ├── stock_comparison.py
│   ├── technical_analysis.py
│   ├── portfolio.py
│   └── news.py
├── Home.py
├── requirements.txt
└── README.md
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
ALPHA_VANTAGE_API_KEY=your_api_key
NEWS_API_KEY=your_api_key
```

## License

MIT License 