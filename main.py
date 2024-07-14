import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import base64
from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader
import warnings

warnings.filterwarnings("ignore")

# Function to read different formats of files
def read_txt(file):
    return file.getvalue().decode("utf-8")

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    pdf_reader = PdfReader(file)
    return " ".join([page.extract_text() for page in pdf_reader.pages])

# Function to filter out stopwords
def remove_stopwords(text, additional_stopwords=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_stopwords))
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# Function to create word cloud download button
def create_image_download_link(buffered, format_):
    image_base64 = base64.b64encode(buffered.getbuffer()).decode('utf-8')
    href = f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}" target="_blank">Download Word Cloud</a>'
    return href

# Function to generate a download link for dataframe
def get_table_download_link_csv(df, filename, file_label):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'
    return href

# Set up the page title and favicon
st.set_page_config(page_title="WordCloud App", page_icon="🌥️")

# Custom CSS for colorful headings with hover effects and enhanced button styles
st.markdown("""
    <style>
    .title {
        color: #4CAF50;
        text-align: center;
    }
    .subheader {
        color: #FF5733;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
    }
    .download-button {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .large-button {
        font-size: 18px;
        padding: 10px 20px;
        background-color: #FF5733;
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.3s ease;
    }
    .large-button:hover {
        background-color: #FF4500;
        transform: scale(1.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit app code
st.markdown("<h1 class='title'>Word Cloud Generator App</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subheader'>Upload a PDF, DOCX or TXT file to generate Word Cloud</h2>", unsafe_allow_html=True)

file = st.file_uploader("Upload file", type=["pdf", "docx", "txt"])
st.set_option('deprecation.showfileUploaderEncoding', False)

if file:
    file_details = {"Filename": file.name, "Filetype": file.type, "Filesize": file.size}
    st.write(file_details)

    # Check the file type and read the file
    if file.type == "text/plain":
        text = read_txt(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(file)
    elif file.type == "application/pdf":
        text = read_pdf(file)
    else:
        st.error("Only txt, docx, and pdf files are supported")
        st.stop()

    # Sidebar: Checkbox and Multiselect box for stopwords
    use_standard_stopwords = st.sidebar.checkbox("Use standard stopwords", value=True)
    additional_stopwords = st.sidebar.text_area("Add additional stopwords (comma-separated)", "")

    if st.sidebar.button("Apply Stopwords"):
        additional_stopwords_list = additional_stopwords.split(",")
        text = remove_stopwords(text, additional_stopwords_list)

    if text:
        # Word cloud dimensions
        width = st.sidebar.slider("Select the Word Cloud Width", 400, 2000, 1200, 50)
        height = st.sidebar.slider("Select the Word Cloud Height", 200, 2000, 800, 50)

        # Generate word cloud
        st.markdown("<h2 class='subheader'>Word Cloud</h2>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(width / 100, height / 100))
        wordcloud = WordCloud(width=width, height=height, background_color="white").generate(text)
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Save the plot functionality
        st.markdown("<h2 class='subheader'>Select file format to save the Word Cloud</h2>", unsafe_allow_html=True)
        format_ = st.selectbox(" ", ["png", "svg", "pdf", "jpg"])

        st.markdown("<h2 class='subheader'>Select the resolution</h2>", unsafe_allow_html=True)
        resolution = st.slider(" ", 100, 500, 300, 50)

        # Generate word count table
        st.markdown("<h2 class='subheader'>Word Count Table</h2>", unsafe_allow_html=True)
        words = text.split()
        word_count = pd.DataFrame(pd.Series(words).value_counts().reset_index())
        word_count.columns = ["Word", "Count"]
        st.write(word_count)

        if st.button(f"Save as {format_}"):
            buffered = BytesIO()
            fig.savefig(buffered, format=format_, dpi=resolution)
            st.markdown(f"<div class='download-button'>{create_image_download_link(buffered, format_)}</div>", unsafe_allow_html=True)
