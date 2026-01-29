let allStocks = [];
let currentFilter = 'all';

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSummary();
    loadStocks();
    setupEventListeners();
});

function setupEventListeners() {
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            loadStocks(currentFilter);
        });
    });
    
    // Search box
    document.getElementById('search-box').addEventListener('input', function(e) {
        filterStocks(e.target.value);
    });
}

async function loadSummary() {
    try {
        const response = await fetch('/api/sentiment/summary');
        const data = await response.json();
        
        document.getElementById('positive-count').textContent = data.positive;
        document.getElementById('negative-count').textContent = data.negative;
        document.getElementById('neutral-count').textContent = data.neutral;
        document.getElementById('total-count').textContent = data.total;
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

async function loadStocks(filter = 'all') {
    showLoading(true);
    
    try {
        const response = await fetch(`/api/sentiment/stocks?type=${filter}`);
        allStocks = await response.json();
        
        displayStocks(allStocks);
    } catch (error) {
        console.error('Error loading stocks:', error);
        document.getElementById('stocks-list').innerHTML = '<div class="no-data">Error loading data. Please try again.</div>';
    } finally {
        showLoading(false);
    }
}

function displayStocks(stocks) {
    const container = document.getElementById('stocks-list');
    
    if (stocks.length === 0) {
        container.innerHTML = '<div class="no-data">No stocks found with the selected filters.</div>';
        return;
    }
    
    container.innerHTML = stocks.map(stock => `
        <div class="stock-item" onclick="toggleNews('${stock.scrip}')">
            <div class="stock-header">
                <div class="stock-info">
                    <h3>${stock.scrip}</h3>
                    <p>${stock.company}</p>
                </div>
                <span class="sentiment-badge sentiment-${stock.overall_sentiment.toLowerCase()}">
                    ${stock.overall_sentiment}
                </span>
            </div>
            <div class="news-count">
                📰 ${stock.news_count} news article${stock.news_count !== 1 ? 's' : ''} | Click to ${stock.news_count > 0 ? 'view details' : 'expand'}
            </div>
            <div class="news-dropdown" id="news-${stock.scrip}">
                ${displayNews(stock.news)}
            </div>
        </div>
    `).join('');
}

function displayNews(newsItems) {
    if (newsItems.length === 0) {
        return '<div class="no-data">No news articles available.</div>';
    }
    
    return newsItems.map(news => `
        <div class="news-item">
            <div class="news-item-header">
                <div class="news-headline">${news.headline}</div>
            </div>
            <div class="news-meta">
                <span>📅 ${news.Date} ${news.Time}</span>
                <span class="impact-badge impact-${news.impact.toLowerCase()}">${news.impact}</span>
                <span class="severity-badge">${news.severity}</span>
            </div>
            <a href="${news.link}" target="_blank" class="news-link">Read full article →</a>
        </div>
    `).join('');
}

function toggleNews(scrip) {
    const dropdown = document.getElementById(`news-${scrip}`);
    dropdown.classList.toggle('active');
}

function filterStocks(searchTerm) {
    const term = searchTerm.toLowerCase();
    const filtered = allStocks.filter(stock => 
        stock.scrip.toLowerCase().includes(term) || 
        stock.company.toLowerCase().includes(term)
    );
    displayStocks(filtered);
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    const stocksList = document.getElementById('stocks-list');
    
    if (show) {
        loading.classList.add('active');
        stocksList.style.display = 'none';
    } else {
        loading.classList.remove('active');
        stocksList.style.display = 'block';
    }
}

// Auto-refresh every 5 minutes
setInterval(() => {
    loadSummary();
    loadStocks(currentFilter);
}, 300000);
