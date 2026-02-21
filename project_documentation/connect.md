# Frontend Connection Guide

Agar aap ek React, Next.js, ya Vue.js frontend bana rahe hain, toh is API ko connect karne ke liye niche di gayi information zaroori hai.

### 1. API Configuration
- **Base URL**: `https://insta-api1-production.up.railway.app/`
- **Swagger Docs**: `/docs` (Always check this for live endpoint testing).

### 2. Endpoints Detail

#### Fetch Profile Data
- **URL**: `${BASE_URL}/profile/${username}`
- **Method**: `GET`
- **Frontend Use**: User followers, posts count, aur profile picture dikhane ke liye.

#### Get User Media
- **URL**: `${BASE_URL}/media/${username}`
- **Method**: `GET`
- **Frontend Use**: Profile ke saare videos/posts ki list dikhane ke liye.

#### Bulk Download ZIP
- **URL**: `${BASE_URL}/bulk-download/${username}`
- **Method**: `POST`
- **Frontend Use**: Button click par puri list download karwane ke liye.

### 3. JavaScript Code Snippet (Axios Example)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://insta-api1-production.up.railway.app' 
});

// Fetch Profile
export const getProfile = async (username) => {
  try {
    const response = await api.get(`/profile/${username}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching profile:", error.response?.data?.detail || error.message);
  }
};

// Bulk Download
export const downloadAll = async (username) => {
  try {
    const response = await api.post(`/bulk-download/${username}`, {}, {
      responseType: 'blob' // Important for ZIP files
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${username}_bulk.zip`);
    document.body.appendChild(link);
    link.click();
  } catch (error) {
     console.error("Download failed:", error);
  }
};
```

### 4. Important Considerations
- **CORS**: Platform par `CORS_ORIGINS=["*"]` set hai, isliye aap kisi bhi local ya production frontend se call kar sakte hain.
- **Handling BLOBS**: Bulk download ke liye frontend par `responseType: 'blob'` set karna mat bhuliye.
- **Error Handling**: Agar user nahi milta, toh API `404` status return karegi. Isse UI mein "User Not Found" dikhane ke liye use karein.
