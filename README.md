# rss-feed-processor

This project implements an agent to read RSS feeds, extract and summarize news grouped by day, and send the output via email in a beautifully designed HTML format.

## Project Structure

```
rss-feed-processor
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── agents
│   │   ├── __init__.py
│   │   ├── rss_reader.py
│   │   └── summarizer.py
│   ├── config
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models
│   │   ├── __init__.py
│   │   └── news_item.py
│   ├── templates
│   │   ├── __init__.py
│   │   ├── email_template.html
│   │   └── prompts.py
│   └── utils
│       ├── __init__.py
│       ├── date_helpers.py
│       └── email_sender.py
├── tests
│   ├── __init__.py
│   ├── test_rss_reader.py
│   └── test_summarizer.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rss-feed-processor.git
   cd rss-feed-processor
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - Copy `.env.example` to `.env`
   - Open `.env` and configure the following settings:
     ```
     # RSS Feed Settings
     RSS_FEEDS=["url1", "url2", "url3"]
     MAX_ITEMS_PER_FEED=10

     # Email Settings
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     EMAIL_USERNAME=your-email@gmail.com
     EMAIL_PASSWORD=your-app-specific-password
     RECIPIENT_EMAIL=recipient@example.com

     # OpenAI Settings (for summarization)
     OPENAI_API_KEY=your-api-key
     ```

## Usage

### Running the Application

1. Start the application:
   ```bash
   python src/main.py
   ```

2. The application will:
   - Fetch articles from configured RSS feeds
   - Group articles by date
   - Generate summaries using AI
   - Create an HTML email with the content
   - Send the email to configured recipients

### Command Line Options

```bash
python src/main.py --days 3  # Process last 3 days of news
python src/main.py --feeds "feed1,feed2"  # Process specific feeds
python src/main.py --dry-run  # Run without sending emails
```

## Development

### Running Tests

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run the test suite:
   ```bash
   pytest tests/
   ```

3. Run tests with coverage:
   ```bash
   pytest --cov=src tests/
   ```

### Code Style

- We follow PEP 8 guidelines
- Use black for code formatting:
  ```bash
  black src/ tests/
  ```

## Troubleshooting

Common issues and solutions:

1. Email sending fails:
   - Verify SMTP settings
   - For Gmail, ensure "Less secure app access" is enabled
   - Check if you're using an app-specific password

2. RSS feed errors:
   - Verify feed URLs are accessible
   - Check internet connection
   - Ensure feed URLs are properly formatted

## Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your fork and submit a pull request

Please ensure your code:
- Includes appropriate tests
- Follows the project's code style
- Updates documentation as needed

## License

This project is licensed under the MIT License. See the LICENSE file for details.