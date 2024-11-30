# **Social Server**  

**Social Server** is a backend platform designed for a social media-like application.  
It enables users to create posts, follow others, comment on posts, and communicate in real-time chats.  

## 📋 Features  

- **User Management**  
  - Register, log in, and manage user profiles.  
  - Follow or unfollow other users to create a personalized feed.  

- **Post Management**  
  - Create, edit, and delete posts.  
  - Comment on posts and interact with other users.  

- **Real-Time Chat**  
  - Send and receive messages in real-time via WebSockets.  
  - Participate in group or private chats.  

## 🛠 Technology Stack  

1. **Frontend Proxy:** Nginx  
2. **Containerization & Orchestration:** Docker & Kubernetes  
3. **Programming Language:** Python  
4. **Web Framework:** Django & Django Rest Framework (DRF)  
5. **Messaging Queue:** Kafka  
6. **Databases:**  
   - Relational: PostgreSQL  
   - Non-relational: MongoDB  
7. **Caching:** Redis  
8. **Real-Time Communication:** WebSockets  
9. **File Storage:** NFS (Network File System)  

## 🏗 Microservices Architecture  

The system follows a **microservices architecture** to ensure separation of concerns and scalability. The key microservices are:

1. **Users Service**  
   - Manages user authentication, profiles, and follower relationships.  

2. **Posts Service**  
   - Handles the creation, editing, and deletion of posts.  
   - Manages comments and interactions on posts.  

3. **Chats Service**  
   - Manages real-time chat functionality, including private and group chats.  

Each service communicates using **Kafka** for event-driven architecture and real-time updates.  

 ### 📲 Installation  
  
 1. **Clone** the repository:  
    ```bash  
    git clone https://github.com/MarkRBro69/servak-app.git 
    cd servak-app  
    ```  
 2. **Set Up Environment Variables:**  
    Configure `.env` file with database credentials, Kafka, Redis, and NFS settings.  
 3. **Deploy with Docker Compose or Kubernetes:**  
    - Docker Compose:  
      ```bash  
      docker-compose up --build  
      ```  
    - Kubernetes:  
      ```bash  
      kubectl apply -f k8s/  
      ```  
 4. **Access the API:**  
    The API will be available at `http://localhost/` or your configured domain.  

## 🚀 Usage  

1. **User Registration and Login:**  
   Use the `/api/usr/` endpoint to register and authenticate users with JWT tokens.  

2. **Posts Management:**  
   - Create posts using `/api/pst/`.  
   - Fetch personalized feeds from `/api/feed/`.  

3. **Chats:**  
   - Start a chat or send messages using `/chats/`.  
   - Real-time updates are handled via WebSockets at `ws://localhost/api/chats/`.  

## 🤝 Contributing  

**Contributions are welcome!**  
Feel free to fork this repository and submit pull requests for:  
- **New features**  
- **Bug fixes**  
- **Performance improvements**  

---
