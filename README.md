# 🦟 Tainan City Dengue Fever Monitoring System

A comprehensive dengue fever monitoring and prediction system for Tainan City, Taiwan, featuring interactive maps, machine learning predictions, and real-time data visualization.

## 📋 Project Description

This project is a sophisticated dengue fever monitoring system that combines web scraping, machine learning, and interactive mapping to provide real-time dengue fever risk assessment for Tainan City. The system features:

- **Interactive Web Interface**: FastAPI-based web application with modern UI
- **Machine Learning Predictions**: Deep learning models for dengue risk prediction
- **Real-time Data Updates**: Automated data collection from government APIs
- **Interactive Maps**: Folium-based visualization with district boundaries
- **Risk Assessment**: Multi-level risk classification (low, medium, high)
- **Data Management**: Comprehensive data processing and storage

The system processes mosquito trap data, weather information, and historical dengue cases to predict outbreak risks across different districts in Tainan City.

## 🚀 How to Run

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for web scraping functionality)
- Required dependencies (see requirements.txt)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DengueFeverProject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**
   - Copy the example configuration file:
     ```bash
     cp config_example.py config.py
     ```
   - Edit `config.py` to match your system requirements

4. **Run the main application**
   ```bash
   python main.py
   ```

5. **Access the web interface**
   - Open your browser and navigate to: `http://localhost:8000`
   - The system will automatically update map data on startup

### Alternative Startup Methods

**For the legacy Node.js system:**
```bash
cd 臺南市校園登革熱預警系統
node server.js
```

**For data updates only:**
```bash
python UpdateData.py
```

### System Components

- **main.py**: FastAPI web server and main application
- **UpdateData.py**: Data collection and update scripts
- **臺南市校園登革熱預警系統/**: Legacy Node.js system with ML models
- **data/**: Data processing and map generation scripts

## 🧪 How to Test

### Running Tests

Since `test_main.py` doesn't exist in the current project structure, here are the recommended testing approaches:

1. **Manual Testing**
   ```bash
   # Start the main application
   python main.py
   
   # In another terminal, test the API endpoints
   curl http://localhost:8000/
   curl http://localhost:8000/api/update-map
   ```

2. **Data Validation Tests**
   ```bash
   # Test data update functionality
   python test.py
   ```

3. **Create a test file** (recommended):
   ```bash
   # Create a simple test file
   cat > test_main.py << 'EOF'
   import requests
   import time
   
   def test_main_app():
       """Test the main FastAPI application"""
       base_url = "http://localhost:8000"
       
       # Test main page
       response = requests.get(base_url)
       assert response.status_code == 200, "Main page should be accessible"
       
       # Test API endpoint
       api_response = requests.get(f"{base_url}/api/update-map")
       assert api_response.status_code == 200, "API should respond successfully"
       
       print("All tests passed!")
   
   if __name__ == "__main__":
       test_main_app()
   EOF
   
   # Run the test
   python test_main.py
   ```

4. **Machine Learning Model Tests**
   ```bash
   cd 臺南市校園登革熱預警系統
   python model_pred.py
   ```

### Testing Checklist

- [ ] Web interface loads correctly
- [ ] Map displays properly
- [ ] Data update functionality works
- [ ] API endpoints respond correctly
- [ ] Machine learning predictions execute
- [ ] File upload functionality (if applicable)

## 📁 Project Structure

```
DengueFeverProject/
├── main.py                          # FastAPI main application
├── test.py                          # Basic data update test
├── UpdateData.py                    # Data collection script
├── requirements.txt                 # Python dependencies
├── config.py                        # Configuration file
├── data/                           # Data processing
│   ├── process_map.py              # Map generation
│   ├── dengue_data.json            # Dengue case data
│   ├── weather_data.json           # Weather information
│   └── district_boundaries.geojson # Geographic boundaries
├── template/                       # Web templates
│   ├── map.html                    # Main map interface
│   └── map_temp.html               # Template file
├── web/                           # Static web assets
│   └── style.css                  # CSS styles
└── 臺南市校園登革熱預警系統/        # Legacy ML system
    ├── server.js                  # Node.js server
    ├── model_pred.py              # ML prediction script
    ├── model_train_const.py       # Model training
    └── data/                      # ML data and models
```

## 🔧 Configuration

Key configuration options in `config.py`:

- **FASTAPI_CONFIG**: Web server settings (host, port, etc.)
- **MAP_CONFIG**: Map display settings (center coordinates, zoom level)
- **DATA_SOURCES**: API endpoints and data sources
- **ML_MODELS**: Machine learning model paths and settings

## 📊 Data Sources

- **Government APIs**: Tainan City dengue case data
- **Weather Data**: Meteorological information for risk assessment
- **Geographic Data**: District boundaries and administrative regions
- **Mosquito Trap Data**: Ovitrap monitoring results

## 🛠️ Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Mapping**: Folium, Leaflet, GeoJSON
- **Data Processing**: Pandas, NumPy, GeoPandas
- **Machine Learning**: Keras, TensorFlow, scikit-learn
- **Web Scraping**: Selenium, Requests

## 📞 Support

For issues or questions:
1. Check the existing Chinese documentation
2. Review the configuration files
3. Verify all dependencies are installed
4. Check system logs for error messages

## 📄 License

This project is part of an academic research initiative for dengue fever monitoring and prediction in Tainan City, Taiwan.# DenGueFeverProject
