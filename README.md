# Chef's Fridge 🍲

![Chef's Fridge Banner](https://img.shields.io/badge/Chef's%20Fridge-Recipe%20Generator-FF6B6B?style=for-the-badge)

## Overview

Chef's Fridge is an AI-powered recipe generator that turns your leftovers into delicious meals. Simply upload photos of your refrigerator, pantry, or available ingredients, and let the application's AI identify the items and generate customized recipes based on what you have on hand.


## Features

- 📷 **Image Recognition**: Upload photos or take pictures directly through the app to identify ingredients
- 🔍 **AI Ingredient Detection**: Automatically detects food items in your photos
- 👨‍🍳 **Recipe Generation**: Creates customized recipes based on your available ingredients
- 🥗 **Dietary Preferences**: Filter recipes based on dietary requirements (Vegetarian, Vegan, Gluten-Free, etc.)
- 🌍 **Cuisine Options**: Generate recipes from various cuisines (Italian, Mexican, Asian, Indian, etc.)
- 📱 **Mobile-Friendly**: Fully responsive design for use on any device
- 📋 **Save and Download**: Save favorite recipes and download them as PDFs
- ✏️ **Ingredient Management**: Add, edit, or remove ingredients manually

## Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini API (through the `google-genai` SDK) for image recognition and recipe generation. The model is set by `GEMINI_MODEL` and defaults to `gemini-3.5-flash-lite`
- **Image Processing**: PIL (Python Imaging Library)
- **PDF Generation**: FPDF
- **Styling**: Custom CSS

## Installation

### Prerequisites

- Python 3.11+
- Google Gemini API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/hrishikeshkhandade/Chefs-Fridge.git
   cd Chefs-Fridge
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Optional: add `GEMINI_MODEL=some-other-model` to the same file to use a different Gemini model. Google retires models over time, so if requests start failing, try a current one here first.

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Tests

The tests replace the Gemini client with a stand-in, so they need no API key or network:

```bash
pip install pytest
pytest -q
```

## Usage Guide

### Step 1: Upload Images
Upload photos of your fridge or pantry. You can either use existing photos or take new ones with your device's camera.

### Step 2: Identify Ingredients
The AI will analyze your photos and identify ingredients. You can also manually add, edit, or remove ingredients from the list.

### Step 3: Generate Recipes
Customize your recipe preferences:
- Choose dietary restrictions (if any)
- Select a cuisine type
- Specify how many recipes you want

The application will generate custom recipes based on your available ingredients and preferences.

### Step 4: Save and Export
Save your favorite recipes to access later or download them as PDFs to reference while cooking.

## Project Structure

```
chefs-fridge/
├── app.py              # Main application file
├── .env                # Environment variables (not included in repo)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── images/             # Directory for documentation images
```

## How It Works

1. **Image Processing**: When you upload an image, it's processed using PIL and converted to a format suitable for the AI.

2. **Ingredient Detection**: The Google Gemini API analyzes the images to identify food items.

3. **Recipe Generation**: Based on the identified ingredients and your preferences, the app prompts the Gemini model to create custom recipes.

4. **Result Processing**: The application parses the AI-generated text to extract structured recipe data (title, ingredients, instructions) and presents it in a user-friendly format.

## Requirements

The full list of Python package requirements:

```
streamlit>=1.27.0
python-dotenv>=1.0.0
google-genai>=3.3.0
pillow>=9.0.0
fpdf>=1.7.2
```

## Privacy and Data Handling

- Images you upload are processed by Google's Gemini API for ingredient recognition.
- No images or personal data are stored on our servers beyond your current session.
- Saved recipes are stored locally in your browser's session state.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Created by Hrishikesh Khandade as part of academic research
- Google Gemini API for providing the AI capabilities
- Streamlit for the powerful web application framework

## Contact

Hrishikesh Khandade - khandadehrishikesh@gmail.com

Project Link: [https://github.com/hrishikeshkhandade/Chefs-Fridge](https://github.com/hrishikeshkhandade/Chefs-Fridge)

---

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" alt="Made with Python">
  <img src="https://img.shields.io/badge/Powered%20by-Streamlit-FF4B4B.svg" alt="Powered by Streamlit">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-blue.svg" alt="AI: Google Gemini">
</p> 
