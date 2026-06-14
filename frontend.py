import streamlit as st
import requests
import base64
import urllib.parse
import os

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Quick Post", layout="wide")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'upload_success' not in st.session_state:
    st.session_state.upload_success = False


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("Welcome to Quick Post")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        email = st.text_input("Email:", key="login_email")
        password = st.text_input("Password:", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                login_data = {"username": email, "password": password}
                response = requests.post(f"{BASE_URL}/auth/jwt/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    user_response = requests.get(f"{BASE_URL}/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password!")

    with tab_signup:
        new_username = st.text_input("Username:", key="signup_username")
        new_email = st.text_input("Email:", key="signup_email")
        new_password = st.text_input("Password:", type="password", key="signup_password")

        if st.button("Sign Up", type="secondary", use_container_width=True):
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields.")
            else:
                signup_data = {"username": new_username, "email": new_email, "password": new_password}
                response = requests.post(f"{BASE_URL}/auth/register", json=signup_data)

                if response.status_code == 201:
                    st.success("Account created! Go to Login tab.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")


def upload_page():
    st.title("📸 Share Something")

    if st.session_state.upload_success:
        st.success("Uploaded successfully!")
        st.session_state.upload_success = False

    uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.session_state.upload_success = True
                st.rerun()
            else:
                st.error("Upload failed!")


def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        # Add text overlay at bottom with semi-transparent background
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-80,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")

    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def feed_page():
    st.title("🏠 Feed")

    response = requests.get(f"{BASE_URL}/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            st.markdown("---")

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{post['username']}**")
            with col2:
                if post.get('is_owner', False):
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                        response = requests.delete(f"{BASE_URL}/posts/{post['id']}", headers=get_headers())
                        if response.status_code == 200:
                            st.success("Post deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            caption = post.get('caption', '')
            if post['file_type'] == 'image':
                st.image(post['url'], width=300)
            else:
                uniform_video_url = create_transformed_url(post['url'], "w-400,h-200,cm-pad_resize,bg-blurred")
                st.video(uniform_video_url, width=300)

            if caption:
                st.markdown(caption)

            st.markdown("")  # Space between posts
    else:
        st.error("Failed to load feed")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Sidebar navigation
    display_name = st.session_state.user.get('username') or st.session_state.user['email']
    st.sidebar.title(f"👋 Hi {display_name}!")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()