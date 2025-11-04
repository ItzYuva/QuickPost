# QuickPost  
A modern social media micro-platform to **share images and videos instantly**, built with **FastAPI**, and **PostgreSQL**.  

---

## **Overview**

**QuickPost** lets users register, log in, upload media (images/videos), and view posts from all users in a simple, clean feed.  

It’s powered by:
-  **FastAPI**: backend for API endpoints and authentication  
-  **ImageKit**: for cloud media storage and delivery  
-  **PostgreSQL**: (via SQLAlchemy) for database persistence  
-  **Streamlit**: frontend for real time web interaction  
-  **Render**: (backend hosting) and **Streamlit Cloud** (frontend hosting)  

---

## **Features**

1. User authentication (Sign-up, Login, Logout) via JWT  
2. Upload images or videos directly from your browser  
3. View all posts in a unified feed with owner tagging  
4. Delete your own posts securely  
5. Cloud storage & transformation via ImageKit  
6. Responsive dark-mode UI built with Streamlit  
7. PostgreSQL integration with async SQLAlchemy