"""
✨ Audiobook Creator App ✨
This bad boy turns boring text into fire audiobooks using
that Sesame CSM-1b model! Vibes for days...
"""

import streamlit as st
import requests
import os
import time

# 🌐 API stuff - change if ur hosting elsewhere
API_URL = "http://localhost:8000"

# 🎨 Page setup - making it look cute
st.set_page_config(
    page_title="Audiobook Creator",
    page_icon="📚",
    layout="wide",
)

# 💅 CSS drip - style makeover
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FFFFFF;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 1rem;
    }
    .book-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 1rem;
    }
    .book-title {
        font-size: 1.2rem;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
    }
    .book-author {
        font-size: 0.9rem;
        color: #4B5563;
        margin-bottom: 0.5rem;
    }
    .book-date {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .status-pending {
        color: #D97706;
        font-weight: bold;
    }
    .status-processing {
        color: #2563EB;
        font-weight: bold;
    }
    .status-completed {
        color: #059669;
        font-weight: bold;
    }
    .status-failed {
        color: #DC2626;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 🧠 Memory check - gotta remember our stuff between refreshes
if 'audiobooks' not in st.session_state:
    st.session_state.audiobooks = []
if 'selected_book' not in st.session_state:
    st.session_state.selected_book = None
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 5  # seconds to wait between vibes
if 'progress_value' not in st.session_state:
    st.session_state.progress_value = 0.0
if 'progress_bars' not in st.session_state:
    st.session_state.progress_bars = []

# 🛠️ Helper functions - doing the heavy lifting

def fetch_audiobooks():
    """🔍 Grab all the books from the API - yeet if it fails"""
    try:
        response = requests.get(f"{API_URL}/audiobooks/")
        if response.status_code == 200:
            st.session_state.audiobooks = response.json()["audiobooks"]
        else:
            st.error(f"Error fetching audiobooks: {response.text}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def create_audiobook(title, author, voice_id, text_file=None, text_content=None):
    """🔮 Create a fresh book - magic happens here"""
    try:
        files = {}
        data = {"title": title, "author": author, "voice_id": voice_id}
        
        if text_file is not None:
            files["text_file"] = text_file
        
        if text_content is not None:
            data["text_content"] = text_content
            
        response = requests.post(
            f"{API_URL}/audiobook/", 
            data=data,
            files=files
        )
        
        if response.status_code == 200:
            st.success("Audiobook creation started successfully!")
            time.sleep(1)
            fetch_audiobooks()
            return response.json()["book_id"]
        else:
            st.error(f"Error creating audiobook: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def delete_audiobook(book_id):
    """🗑️ Yeet a book into oblivion - delete it from existence"""
    try:
        response = requests.delete(f"{API_URL}/audiobook/{book_id}")
        if response.status_code == 200:
            st.success("Audiobook deleted successfully!")
            # Clean up our memory
            st.session_state.audiobooks = [book for book in st.session_state.audiobooks if book["id"] != book_id]
            if st.session_state.selected_book and st.session_state.selected_book["id"] == book_id:
                st.session_state.selected_book = None
            return True
        else:
            st.error(f"Error deleting audiobook: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def get_audiobook(book_id):
    """📖 Fetch deets for a specific book - all the tea"""
    try:
        response = requests.get(f"{API_URL}/audiobook/{book_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting audiobook: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_audio_url(book_id):
    """🔊 Get URL for the audio file - bops only"""
    return f"{API_URL}/audiobook/{book_id}/audio"

def format_status(status):
    """💄 Make status look cute with different colors"""
    if status == "pending":
        return f'<span class="status-pending">PENDING</span>'
    elif status == "processing":
        return f'<span class="status-processing">PROCESSING</span>'
    elif status == "completed":
        return f'<span class="status-completed">COMPLETED</span>'
    elif status == "failed":
        return f'<span class="status-failed">FAILED</span>'
    else:
        return status

# 🔄 Auto-refresh function - keeping our content fresh
def auto_refresh():
    if st.session_state.get('auto_refresh', False):
        # Any books still cooking?
        has_processing = any(book.get('status') == 'processing' for book in st.session_state.audiobooks)
        
        if has_processing:
            # Update progress animation - make it pulse
            if "progress_value" in st.session_state:
                # Wavy animation vibe
                st.session_state.progress_value = (st.session_state.progress_value + 0.05) % 1.0
            
            # Get fresh data
            fetch_audiobooks()
            
            # Update the book we're looking at
            if st.session_state.selected_book:
                book_id = st.session_state.selected_book["id"]
                updated_book = get_audiobook(book_id)
                if updated_book:
                    st.session_state.selected_book = updated_book

# 🗣️ Voice options - pick your vibe
VOICE_OPTIONS = {
    0: "Default Voice",
    1: "Male Voice 1",
    2: "Female Voice 1",
    3: "Male Voice 2",
    4: "Female Voice 2",
}

# 🚀 Main UI - where the magic happens
def main():
    st.markdown('<h1 class="main-header">Audiobook Creator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Convert text to audiobooks using Sesame CSM-1b for realistic speech</p>', unsafe_allow_html=True)
    
    # 📊 Sidebar - control center
    with st.sidebar:
        st.markdown('<h2 class="sub-header">Create New Audiobook</h2>', unsafe_allow_html=True)
        
        # Form fields - get the deets
        title = st.text_input("Title")
        author = st.text_input("Author")
        voice_id = st.selectbox("Voice", options=list(VOICE_OPTIONS.keys()), format_func=lambda x: VOICE_OPTIONS[x])
        
        # How you wanna input? File or text?
        input_type = st.radio("Input Type", ["Upload Text File", "Enter Text"])
        
        # Setup our vars
        text_file = None
        text_content = None
        
        # Show different inputs based on what they picked
        if input_type == "Upload Text File":
            text_file = st.file_uploader("Upload Text File", type=["txt", "md", "epub", "pdf"])
        else:  # Text area for the writers
            text_content = st.text_area("Book Text", height=200, placeholder="Enter your book text here...")
        
        # Let's go button!
        if st.button("Create Audiobook"):
            if not title or not author:
                st.error("Please enter both title and author")
            elif input_type == "Upload Text File" and not text_file:
                st.error("Please upload a text file")
            elif input_type == "Enter Text" and not text_content:
                st.error("Please enter book text")
            else:
                book_id = create_audiobook(title, author, voice_id, text_file, text_content)
                if book_id:
                    # Turn on auto-refresh
                    st.session_state.auto_refresh = True
                    st.balloons()
        
        # Auto-refresh toggle - stay up to date
        st.checkbox("Auto-refresh for processing books", value=True, key="auto_refresh")
        
        if st.session_state.get('auto_refresh', False):
            st.info(f"Auto-refreshing every {st.session_state.refresh_interval} seconds when books are processing")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app uses the Sesame CSM-1b model to generate fire audiobooks.
        Upload text or paste it to create realistic voices - it's that easy! ✨
        """)
    
    # 📑 Main content tabs
    tab1, tab2 = st.tabs(["My Audiobooks", "View Audiobook"])
    
    # 📚 Tab 1: Book list
    with tab1:
        st.markdown('<h2 class="sub-header">My Audiobooks</h2>', unsafe_allow_html=True)
        
        # Refresh button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Refresh"):
                fetch_audiobooks()
        
        # Load books if we don't have any
        if not st.session_state.audiobooks:
            fetch_audiobooks()
        
        # Display the book collection
        if st.session_state.audiobooks:
            for book in st.session_state.audiobooks:
                with st.container():
                    st.markdown(f'<div class="book-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        st.markdown(f'<div class="book-title">{book["title"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="book-author">by {book["author"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="book-date">{book["date"]}</div>', unsafe_allow_html=True)
                    with col2:
                        status_html = format_status(book["status"])
                        st.markdown(f'Status: {status_html}', unsafe_allow_html=True)
                        
                        if book["status"] == "processing":
                            # Loading animation vibes
                            st.spinner("Processing...")
                            # Progress bar with pulse effect
                            progress_bar = st.progress(st.session_state.progress_value)
                            # Keep track of our progress bars
                            if progress_bar not in st.session_state.progress_bars:
                                st.session_state.progress_bars.append(progress_bar)
                            # Info message
                            st.info("Audio generation in progress...")
                    with col3:
                        if st.button("View", key=f"view_{book['id']}"):
                            st.session_state.selected_book = book
                            # Switch tab
                            tab2.active = True
                        
                        if st.button("Delete", key=f"delete_{book['id']}"):
                            if delete_audiobook(book["id"]):
                                st.experimental_rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No audiobooks yet. Create one using the form in the sidebar.")
    
    # 🎧 Tab 2: Book details view
    with tab2:
        if st.session_state.selected_book:
            book = st.session_state.selected_book
            
            # Auto-refresh processing books
            if book["status"] == "processing" and st.session_state.get('auto_refresh', False):
                updated_book = get_audiobook(book["id"])
                if updated_book:
                    book = updated_book
                    st.session_state.selected_book = updated_book
            
            st.markdown(f'<h2 class="sub-header">{book["title"]}</h2>', unsafe_allow_html=True)
            st.markdown(f'<div class="book-author">by {book["author"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="book-date">{book["date"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### Status")
            status_html = format_status(book["status"])
            st.markdown(f'Status: {status_html}', unsafe_allow_html=True)
            
            if book["status"] == "processing":
                # Loading animation vibes
                st.spinner("Processing...")
                # Progress bar with pulse effect
                progress_bar = st.progress(st.session_state.progress_value)
                # Keep track of our progress bars
                if progress_bar not in st.session_state.progress_bars:
                    st.session_state.progress_bars.append(progress_bar)
                # Info message
                st.info("Audio generation in progress...")
            
            if book["status"] == "completed" and book.get("audio_path"):
                st.markdown("### Audio")
                st.audio(get_audio_url(book["id"]))
                
                # Download link
                audio_url = get_audio_url(book["id"])
                st.markdown(f'<a href="{audio_url}" download="{book["title"]}.wav">Download Audiobook</a>', unsafe_allow_html=True)
            
            # Show a preview of the book text
            if book.get("text_path") and os.path.exists(book["text_path"]):
                st.markdown("### Book Text Preview")
                try:
                    with open(book["text_path"], "r", encoding="utf-8") as f:
                        text_content = f.read()
                    
                    # Just show a snippet
                    preview = text_content[:500] + ("..." if len(text_content) > 500 else "")
                    st.text_area("Text Preview", preview, height=200, disabled=True)
                except Exception as e:
                    st.error(f"Error reading text file: {str(e)}")
        else:
            st.info("Select an audiobook from the list to view details.")
    
    # 🔄 Auto-refresh for processing books
    if st.session_state.get('auto_refresh', False):
        # Any books still cooking?
        has_processing = any(book.get('status') == 'processing' for book in st.session_state.audiobooks)
        
        if has_processing:
            # Update all progress bars with the current value
            for progress_bar in st.session_state.get('progress_bars', []):
                if 'progress_value' in st.session_state:
                    try:
                        progress_bar.progress(st.session_state.progress_value)
                    except:
                        pass
            
            # Chill for a bit
            time.sleep(st.session_state.refresh_interval)
            
            # Refresh everything
            auto_refresh()

# 🚀 Launch the app
if __name__ == "__main__":
    main() 