import streamlit as st
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv
import google.generativeai as genai
import hashlib
from fpdf import FPDF
import re
import uuid

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("API key not found in .env file! Please add GEMINI_API_KEY.")

# Set up Google Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )

# Set page config
st.set_page_config(page_title="Chef's Fridge", layout="wide", page_icon="🍲", initial_sidebar_state="collapsed")

# Custom CSS for mobile-friendly design
st.markdown("""
    <style>
    /* Mobile-first base styles */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --accent-color: #FFE66D;
        --background-color: #f9f9f9;
        --card-bg: #ffffff;
        --text-color: #333333;
        --border-radius: 12px;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
        --neutral-color: #9E9E9E;
    }
    
    /* Base text sizing for mobile */
    html {
        font-size: 16px;
    }
    
    /* Stack elements vertically on mobile */
    .mobile-stack {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    /* Larger touch targets */
    button, [role="button"] {
        min-height: 3rem !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--background-color);
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: var(--border-radius);
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
    }
    
    /* Card component */
    .card {
        background-color: var(--card-bg);
        padding: 1rem;
        border-radius: var(--border-radius);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Full-width elements on mobile */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        
        .stButton > button {
            width: 100% !important;
        }
        
        /* Hide desktop-only elements */
        .desktop-only {
            display: none;
        }
        
        /* Adjust font sizes */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        /* Simplify card padding */
        .card {
            padding: 1rem;
        }
    }
    
    /* Desktop-specific adjustments */
    @media (min-width: 769px) {
        .mobile-only {
            display: none;
        }
        
        /* Limit max width for readability */
        .main-content {
            max-width: 800px;
            margin: 0 auto;
        }
    }
    
    /* Enhanced image grid */
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Improved input fields */
    .stTextInput input {
        padding: 1rem !important;
        border-radius: var(--border-radius) !important;
    }
    
    /* Better ingredient list */
    .ingredient-item {
        padding: 1rem;
        margin: 0.5rem 0;
        background: var(--card-bg);
        border-radius: var(--border-radius);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 3px solid var(--primary-color);
    }
    
    /* Simplified navigation */
    .nav-pills {
        display: flex;
        gap: 0.5rem;
        overflow-x: auto;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    
    .nav-pill {
        flex: 0 0 auto;
        background-color: #e9e9e9;
        color: #666;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin-right: 0.5rem;
        font-size: 0.9rem;
        white-space: nowrap;
    }
    
    .nav-pill.active {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
        font-weight: bold;
        color: var(--primary-color);
    }
    
    /* Recipe step styling */
    .step-card {
        background-color: var(--card-bg);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 0.8rem;
        border-left: 3px solid var(--primary-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .step-number {
        display: inline-block;
        background-color: var(--primary-color);
        color: white;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        border-radius: 50%;
        margin-right: 10px;
        font-weight: bold;
    }
    
    .ingredient-list-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .ingredient-bullet {
        color: var(--primary-color);
        margin-right: 10px;
        font-size: 1.2rem;
    }
    
    /* Download button */
    .download-btn {
        display: inline-block;
        background-color: var(--secondary-color);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        text-decoration: none;
        font-weight: bold;
        margin-top: 1rem;
        text-align: center;
    }
    
    /* Tab styling improvements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        background-color: #f0f0f0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Footer styling */
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        font-size: 0.8rem;
        color: #666;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def image_to_bytes(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return buffered.getvalue()

def image_hash(image):
    return hashlib.md5(image_to_bytes(image)).hexdigest()

def is_duplicate(new_image, existing_images):
    new_hash = image_hash(new_image)
    return any(image_hash(img) == new_hash for img in existing_images)

@st.cache_data
def identify_items(_images):
    if not GEMINI_API_KEY:
        st.error("Cannot identify items: API key missing.")
        return []
    all_items = []
    for image in _images:
        base64_image = base64.b64encode(image_to_bytes(image)).decode('utf-8')
        try:
            response = model.generate_content([
                "List all food items in this fridge image in a comma-separated format. Be specific and concise.",
                {"mime_type": "image/jpeg", "data": base64_image}
            ])
            items = response.text.split(',')
            all_items.extend([item.strip() for item in items if item.strip()])
        except Exception as e:
            st.error(f"Error identifying items: {str(e)}")
            return []
    return list(set(all_items))

def clean_text(text):
    """Clean recipe text by removing asterisks, bullet points, etc."""
    # Remove markdown formatting like **bold** or *italic*
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Remove # headers
    text = re.sub(r'^#+ ', '', text, flags=re.MULTILINE)
    
    # Clean bullet points and other markers
    text = re.sub(r'^\s*[•\-*]\s+', '', text, flags=re.MULTILINE)
    
    # Clean numbered steps but preserve the number for parsing
    # This preserves the numbers for parsing but we'll handle display separately
    
    return text

def generate_recipe(items, diet_preference, cuisine_preference):
    if not GEMINI_API_KEY:
        return "API key missing. Please configure it to generate recipes."
    try:
        diet_instruction = f"The recipe should be {diet_preference.lower()}." if diet_preference != "None" else ""
        cuisine_instruction = f"The recipe should be {cuisine_preference} cuisine." if cuisine_preference != "Any" else ""
        prompt = f"""Create a recipe using these ingredients: {', '.join(items)}. {diet_instruction} {cuisine_instruction} 
        
        IMPORTANT: Format your response using plain text only, with NO bullet points, NO asterisks, and NO special formatting.
        
        Structure your response as follows:
        
        [Recipe Title]
        
        INGREDIENTS:
        Ingredient 1 with quantity
        Ingredient 2 with quantity
        ...
        
        INSTRUCTIONS:
        1. First step
        2. Second step
        ...
        
        For steps, use only numbers followed by a period, never bullet points or asterisks.
        For ingredients, list each on its own line without bullet points or numbers.
        """
        
        response = model.generate_content(prompt)
        recipe_text = response.text
        
        # Clean up formatting
        recipe_text = clean_text(recipe_text)
        
        return recipe_text
    except Exception as e:
        st.error(f"Error generating recipe: {str(e)}")
        return "Unable to generate recipe."

def generate_multiple_recipes(items, diet_preference, cuisine_preference, num_recipes):
    """Generate multiple recipes with a simplified progress indicator"""
    results = []
    
    # Show a text status instead of using the progress bar
    status_text = st.empty()
    
    for i in range(num_recipes):
        status_text.text(f"Generating recipe {i+1} of {num_recipes}...")
        recipe = generate_recipe(items, diet_preference, cuisine_preference)
        results.append(recipe)
        
    status_text.empty()
    return results

def get_pdf_download_link(recipes, filename="recipes"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add author information to the first page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Chef's Fridge", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Created by Hrishikesh Khandade", ln=True, align="C")
    pdf.cell(0, 10, "Contact: khandadehrishikesh@gmail.com", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "This project was developed as part of academic research", ln=True, align="C")
    pdf.ln(10)
    
    for i, recipe in enumerate(recipes, 1):
        pdf.add_page()
        
        # Clean recipe text
        recipe = clean_text(recipe)
        
        # Extract title
        title_match = re.search(r'^(.+?)(?:\n|$)', recipe)
        title = title_match.group(1) if title_match else f"Recipe {i}"
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 15, txt=title, ln=True, align="C")
        
        # Add content with better formatting
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=recipe.replace(title, "").strip())
        
    # Add footer with author information on each page
    pdf.set_auto_page_break(False)
    for page in range(1, pdf.page_no() + 1):
        pdf.page = page
        pdf.set_y(-15)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Created by Hrishikesh Khandade | Page {page}", 0, 0, 'C')
    
    pdf_output = pdf.output(dest="S").encode("latin-1", errors="ignore")
    b64 = base64.b64encode(pdf_output).decode()
    
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf" class="download-btn">Download PDF</a>'

def parse_recipe_steps(recipe_text):
    """Extract steps from recipe text"""
    steps = []
    lines = recipe_text.split('\n')
    in_instructions = False
    
    # First pass: look for instructions section
    for line in lines:
        if re.search(r'(instructions|directions|steps|method)', line.lower()):
            in_instructions = True
            continue
            
        if in_instructions and line.strip():
            # Clean any remaining bullet points at the beginning of the step
            # but preserve numbered steps for proper ordering
            step = line.strip()
            # Remove the number prefix for display
            step = re.sub(r'^\s*\d+\.\s+', '', step)
            # Remove any bullet points
            step = re.sub(r'^\s*[•\-*]\s+', '', step)
            if step:
                steps.append(step)
    
    # If no steps found through instructions marker, try to extract numbered steps directly
    if not steps:
        numbered_steps = re.findall(r'^\s*(\d+)\.\s+(.*?)$', recipe_text, re.MULTILINE)
        if numbered_steps:
            # Sort by the actual number to ensure correct order
            sorted_steps = sorted(numbered_steps, key=lambda x: int(x[0]))
            steps = [re.sub(r'^\s*[•\-*]\s+', '', step[1]) for step in sorted_steps]
    
    return steps

def parse_recipe_ingredients(recipe_text):
    """Extract ingredients from recipe text"""
    lines = recipe_text.split('\n')
    ingredients = []
    in_ingredients = False
    
    # Look for the ingredients section
    for line in lines:
        # Check if this line indicates start of ingredients section
        if re.search(r'ingredients', line.lower()):
            in_ingredients = True
            continue
        
        # Check if this line indicates end of ingredients section (start of instructions)
        if in_ingredients and re.search(r'(instructions|directions|steps|method)', line.lower()):
            in_ingredients = False
            continue
            
        # Add ingredient if we're in the ingredients section
        if in_ingredients and line.strip():
            # Clean up any bullet points or asterisks
            cleaned = re.sub(r'^\s*[-•*]\s*', '', line.strip())
            ingredients.append(cleaned)
    
    # If we couldn't find a proper ingredients section, try an alternative approach
    if not ingredients:
        # Look for a blank line after the title, then take lines until we hit instructions
        blank_line_found = False
        for i, line in enumerate(lines):
            if i > 0 and not line.strip():
                blank_line_found = True
                continue
                
            if blank_line_found:
                if re.search(r'(instructions|directions|steps|method)', line.lower()):
                    break
                if line.strip() and not re.match(r'^\d+\.', line.strip()):
                    cleaned = re.sub(r'^\s*[-•*]\s*', '', line.strip())
                    ingredients.append(cleaned)
    
    return ingredients

# Initialize session state
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'
    if 'images' not in st.session_state:
        st.session_state.images = []
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = []
    if 'recipes' not in st.session_state:
        st.session_state.recipes = []
    if 'saved_recipes' not in st.session_state:
        st.session_state.saved_recipes = []
    if 'new_ingredient' not in st.session_state:
        st.session_state.new_ingredient = ""
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = {}
    if 'viewing_recipe' not in st.session_state:
        st.session_state.viewing_recipe = None
    if 'edit_index' not in st.session_state:
        st.session_state.edit_index = None

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# Navigation display
def show_navigation():
    steps = ['Home', 'Upload Images', 'Identify Ingredients', 'Generate Recipe']
    current_idx = 0
    
    if st.session_state.page in steps:
        current_idx = steps.index(st.session_state.page)
    
    st.markdown('<div class="nav-pills">', unsafe_allow_html=True)
    for i, step in enumerate(steps):
        active_class = "active" if i == current_idx else ""
        st.markdown(
            f'<div class="nav-pill {active_class}" onclick="window.location.href=\'#{step}\'">{step}</div>', 
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# Page functions
def home_page():
    st.title("Chef's Fridge")
    st.markdown("<p>Turn your leftovers into delicious meals</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p>Upload photos of your fridge or pantry and get personalized recipes in seconds!</p>
        <ol>
            <li>📷 Take a photo of your fridge</li>
            <li>🔍 Our AI identifies ingredients</li>
            <li>👨‍🍳 Get customized recipes</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button('Get Started', use_container_width=True):
        st.session_state.page = 'Upload Images'
        st.rerun()
    
    # Saved recipes
    if st.session_state.saved_recipes:
        st.markdown("### Your Saved Recipes")
        for recipe in st.session_state.saved_recipes:
            st.markdown(f"""
            <div class="card">
                <h3>{recipe['title']}</h3>
                <p>Cuisine: {recipe['cuisine']}</p>
                <div style="display: flex; justify-content: flex-end;">
                    <button onclick="alert('View Recipe')" style="background: var(--primary-color); color: white; border: none; border-radius: 4px; padding: 0.3rem 0.6rem; cursor: pointer;">View</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Recipe", key=f"view_{recipe['id']}"):
                st.session_state.viewing_recipe = recipe
                st.session_state.page = "View Recipe"
                st.rerun()
    
    # Add footer with author information
    st.markdown("""
    <div class="footer">
        <p>Chef's Fridge - Created by Hrishikesh Khandade</p>
        <p>Contact: khandadehrishikesh@gmail.com</p>
        <p>This project was developed as part of academic research</p>
    </div>
    """, unsafe_allow_html=True)

def upload_images_page():
    st.title("📷 Upload Images")
    
    # Progress indicator
    st.markdown(f'<div class="step-indicator">Step 1 of 3</div>', unsafe_allow_html=True)
    
    # Mobile-friendly upload options
    upload_method = st.radio("Choose upload method:", 
                           ["Upload existing photos", "Take a new photo"],
                           horizontal=True,
                           label_visibility="collapsed")
    
    if upload_method == "Upload existing photos":
        uploaded_files = st.file_uploader("Select fridge photos", 
                                        type=["jpg", "jpeg", "png"],
                                        accept_multiple_files=True,
                                        label_visibility="collapsed")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                new_image = Image.open(uploaded_file)
                if not is_duplicate(new_image, st.session_state.images):
                    st.session_state.images.append(new_image)
                    st.success(f"Added {uploaded_file.name}")
                else:
                    st.info(f"Skipped duplicate image: {uploaded_file.name}")
    else:
        camera_image = st.camera_input("Take a photo of your fridge", 
                                     label_visibility="collapsed")
        if camera_image:
            new_image = Image.open(camera_image)
            if not is_duplicate(new_image, st.session_state.images):
                st.session_state.images.append(new_image)
                st.success("Photo added!")
            else:
                st.info("This photo appears to be a duplicate")

    # Image grid preview
    if st.session_state.images:
        st.subheader("Your Photos")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.images):
            with cols[i % 3]:
                st.image(img, use_container_width=True)
                if st.button("❌", key=f"remove_{i}", 
                            help="Remove this photo"):
                    st.session_state.images.pop(i)
                    st.rerun()

        st.markdown("---")
        st.button("Continue to Ingredients →", 
                 type="primary", 
                 use_container_width=True,
                 on_click=lambda: set_page("Identify Ingredients"))
    else:
        st.markdown("""
        <div class="card">
            <p style="text-align:center">📸 Tips for best results:</p>
            <ol>
                <li>Take photos in good lighting</li>
                <li>Capture entire shelves</li>
                <li>Get close for small items</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Add footer with author information
    st.markdown("""
    <div class="footer">
        <p>Chef's Fridge - Created by Hrishikesh Khandade</p>
        <p>Contact: khandadehrishikesh@gmail.com</p>
        <p>This project was developed as part of academic research</p>
    </div>
    """, unsafe_allow_html=True)

def identify_ingredients_page():
    st.title("🍎 Ingredients")
    
    # Progress indicator
    st.markdown(f'<div class="step-indicator">Step 2 of 3</div>', 
               unsafe_allow_html=True)

    if not st.session_state.images:
        st.warning("No images found. Please upload some images first.")
        if st.button("Back to Upload"):
            st.session_state.page = 'Upload Images'
            st.rerun()
        return

    # Automatic detection on first load
    if not st.session_state.ingredients and st.session_state.images:
        if st.button("✨ Identify Ingredients", use_container_width=True):
            with st.spinner("🧠 Scanning your photos for ingredients..."):
                ingredients = identify_items(st.session_state.images)
                st.session_state.ingredients = [re.sub(r'^\s*[-•*]\s*', '', item) for item in ingredients]

    # Manual add section
    with st.expander("➕ Add Ingredients", expanded=True):
        new_ing = st.text_input("Add ingredients (comma separated)",
                               key="new_ingredient",
                               placeholder="e.g. chicken, tomatoes, cheese",
                               label_visibility="collapsed")
        if new_ing:
            ingredients = [i.strip() for i in new_ing.split(",") if i.strip()]
            st.session_state.ingredients.extend(ingredients)
            st.session_state.ingredients = list(set(st.session_state.ingredients))
            st.session_state.new_ingredient = ""

    # Editable ingredient list
    if st.session_state.ingredients:
        st.subheader(f"Found {len(st.session_state.ingredients)} ingredients")
        for i, ing in enumerate(st.session_state.ingredients):
            cols = st.columns([3,1,1])
            with cols[0]:
                st.markdown(f"<div class='ingredient-item'>{ing}</div>", 
                           unsafe_allow_html=True)
            with cols[1]:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_mode[f"ingredient_{i}"] = True
                    st.rerun()
            with cols[2]:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.ingredients.pop(i)
                    st.rerun()
            
            # Edit mode for this ingredient
            if st.session_state.edit_mode.get(f"ingredient_{i}", False):
                edit_cols = st.columns([3,1,1])
                with edit_cols[0]:
                    new_value = st.text_input(
                        "Edit ingredient",
                        value=ing,
                        key=f"edit_ingredient_{i}",
                        label_visibility="collapsed"
                    )
                with edit_cols[1]:
                    if st.button("Cancel", key=f"cancel_{i}"):
                        st.session_state.edit_mode[f"ingredient_{i}"] = False
                        st.rerun()
                with edit_cols[2]:
                    if st.button("Save", key=f"save_{i}"):
                        if new_value.strip():
                            st.session_state.ingredients[i] = new_value
                        st.session_state.edit_mode[f"ingredient_{i}"] = False
                        st.rerun()

    # Navigation footer
    st.markdown("---")
    cols = st.columns(2)
    with cols[0]:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "Upload Images"
            st.rerun()
    with cols[1]:
        if st.button("Create Recipes →", type="primary", use_container_width=True):
            st.session_state.page = "Generate Recipe"
            st.rerun()
    
    # Add footer with author information
    st.markdown("""
    <div class="footer">
        <p>Chef's Fridge - Created by Hrishikesh Khandade</p>
        <p>Contact: khandadehrishikesh@gmail.com</p>
        <p>This project was developed as part of academic research</p>
    </div>
    """, unsafe_allow_html=True)

def generate_recipe_page():
    st.title("👨‍🍳 Generate Recipes")
    
    # Progress indicator
    st.markdown(f'<div class="step-indicator">Step 3 of 3</div>', 
               unsafe_allow_html=True)
    
    if not st.session_state.ingredients:
        st.warning("No ingredients found. Please identify ingredients first.")
        if st.button("Back to Ingredients"):
            st.session_state.page = "Identify Ingredients"
            st.rerun()
        return
    
    # Display current ingredients in compact form
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("Using these ingredients:")
    
    # More compact ingredient display
    ingredients_text = ", ".join(st.session_state.ingredients)
    st.markdown(f"<p>{ingredients_text}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recipe preferences - simplified layout
    st.subheader("Customize Your Recipe")
    
    diet_preference = st.selectbox(
        "Dietary Preference",
        ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Low-Carb"]
    )
    
    cuisine_preference = st.selectbox(
        "Cuisine Type",
        ["Any", "Italian", "Mexican", "Asian", "Indian", "Mediterranean", "American", "French"]
    )
    
    num_recipes = st.radio("Number of Recipes", [1, 2, 3], horizontal=True)
    
    # Generate button
    if st.button("Generate Recipes", use_container_width=True):
        with st.spinner("Creating your recipes..."):
            st.session_state.recipes = generate_multiple_recipes(
                st.session_state.ingredients, 
                diet_preference, 
                cuisine_preference, 
                int(num_recipes)
            )
    
    # Display generated recipes
    if st.session_state.recipes:
        st.subheader("Your Recipes")
        
        for i, recipe in enumerate(st.session_state.recipes):
            # Clean recipe text
            recipe = clean_text(recipe)
            
            # Extract title
            title_match = re.search(r'^(.+?)(?:\n|$)', recipe)
            title = title_match.group(1) if title_match else f"Recipe {i+1}"
            
            # Recipe card with expandable sections
            with st.expander(title, expanded=True):
                # Simple tabs
                tabs = st.tabs(["Overview", "Ingredients", "Steps"])
                
                with tabs[0]:
                    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
                    
                    if diet_preference != "None":
                        st.markdown(f"**Diet:** {diet_preference}")
                    st.markdown(f"**Cuisine:** {cuisine_preference if cuisine_preference != 'Any' else 'Mixed'}")
                    
                    # Save recipe button
                    if st.button("Save Recipe", key=f"save_{i}"):
                        recipe_id = str(uuid.uuid4())
                        st.session_state.saved_recipes.append({
                            "id": recipe_id,
                            "title": title,
                            "content": recipe,
                            "ingredients": st.session_state.ingredients.copy(),
                            "diet": diet_preference,
                            "cuisine": cuisine_preference
                        })
                        st.success(f"Saved: {title}")
                
                with tabs[1]:
                    # Extract ingredients
                    ingredients = parse_recipe_ingredients(recipe)
                    
                    if ingredients:
                        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                        for ingredient in ingredients:
                            # Clean any bullet points in the ingredient
                            clean_ingredient = re.sub(r'^\s*[•\-*]\s+', '', ingredient)
                            st.markdown(f"""
                            <div class="ingredient-list-item">
                                <span class="ingredient-bullet">•</span>
                                <span>{clean_ingredient}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        # Fallback
                        st.markdown(recipe.split("\n\n")[0] if "\n\n" in recipe else recipe)
                
                with tabs[2]:
                    # Extract steps
                    steps = parse_recipe_steps(recipe)
                    
                    if steps:
                        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                        for j, step in enumerate(steps, 1):
                            # Ensure no bullet points in the step text
                            clean_step = re.sub(r'^\s*[•\-*]\s+', '', step)
                            st.markdown(f"""
                            <div class="step-card">
                                <span class="step-number">{j}</span>
                                <span>{clean_step}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        # Fallback
                        st.text(recipe)
        
        # Download PDF option
        st.markdown(get_pdf_download_link(st.session_state.recipes), unsafe_allow_html=True)
    
    # Back button
    if st.button("Back to Ingredients", use_container_width=True):
        st.session_state.page = "Identify Ingredients"
        st.rerun()

def view_saved_recipe():
    if not st.session_state.viewing_recipe:
        st.session_state.page = "Home"
        st.rerun()
        return
    
    recipe = st.session_state.viewing_recipe
    
    st.title(recipe['title'])
    
    tabs = st.tabs(["Overview", "Ingredients", "Steps"])
    
    with tabs[0]:
        st.markdown(f"<h3>{recipe['title']}</h3>", unsafe_allow_html=True)
        
        if recipe['diet'] != "None":
            st.markdown(f"**Diet:** {recipe['diet']}")
        st.markdown(f"**Cuisine:** {recipe['cuisine']}")
        
        st.markdown("<h4>Ingredients Used</h4>", unsafe_allow_html=True)
        st.write(", ".join(recipe['ingredients']))
        
        # PDF download for this recipe
        st.markdown(get_pdf_download_link([recipe['content']], recipe['title']), unsafe_allow_html=True)
        
        # Delete recipe button
        if st.button("Delete Recipe"):
            st.session_state.saved_recipes = [r for r in st.session_state.saved_recipes if r['id'] != recipe['id']]
            st.success("Recipe deleted")
            st.session_state.page = "Home"
            st.rerun()
    
    with tabs[1]:
        # Extract ingredients section
        ingredients = parse_recipe_ingredients(recipe['content'])
        
        if ingredients:
            st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
            for ingredient in ingredients:
                # Clean any bullet points in the ingredient
                clean_ingredient = re.sub(r'^\s*[•\-*]\s+', '', ingredient)
                st.markdown(f"""
                <div class="ingredient-list-item">
                    <span class="ingredient-bullet">•</span>
                    <span>{clean_ingredient}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback to showing part of the recipe
            st.write(recipe['content'].split('\n\n')[0] if '\n\n' in recipe['content'] else recipe['content'])
    
    with tabs[2]:
        steps = parse_recipe_steps(recipe['content'])
        
        if steps:
            st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
            for idx, step in enumerate(steps, 1):
                # Ensure no bullet points in the step text
                clean_step = re.sub(r'^\s*[•\-*]\s+', '', step)
                st.markdown(f"""
                <div class="step-card">
                    <span class="step-number">{idx}</span>
                    <span>{clean_step}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback
            st.write(recipe['content'])
    
    # Back button
    if st.button("Back to Home", use_container_width=True):
        st.session_state.viewing_recipe = None
        st.session_state.page = "Home"
        st.rerun()

def main():
    init_session_state()
    
    # Display navigation
    if st.session_state.page != "Home":
        show_navigation()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Chef's Fridge")
        
        if st.sidebar.button("🏠 Home"):
            st.session_state.page = "Home"
            st.rerun()
        if st.sidebar.button("📷 Upload Images"):
            st.session_state.page = "Upload Images"
            st.rerun()
        if st.sidebar.button("🍎 Ingredients"):
            st.session_state.page = "Identify Ingredients" 
            st.rerun()
        if st.sidebar.button("👨‍🍳 Recipes"):
            st.session_state.page = "Generate Recipe"
            st.rerun()
        
        # Saved recipes in sidebar
        if st.session_state.saved_recipes:
            st.sidebar.markdown("---")
            st.sidebar.header("Saved Recipes")
            for recipe in st.session_state.saved_recipes:
                if st.sidebar.button(recipe['title'], key=f"sidebar_{recipe['id']}"):
                    st.session_state.viewing_recipe = recipe
                    st.session_state.page = "View Recipe"
                    st.rerun()
    
    # Display correct page
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Upload Images":
        upload_images_page()
    elif st.session_state.page == "Identify Ingredients":
        identify_ingredients_page()
    elif st.session_state.page == "Generate Recipe":
        generate_recipe_page()
    elif st.session_state.page == "View Recipe":
        view_saved_recipe()

if __name__ == "__main__":
    main()
