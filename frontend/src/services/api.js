import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const res = await axios({
        url,
        method: options.method || 'GET',
        headers: options.headers,
        data: options.body,
        params: options.params,
      });
      
      return res.data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  //Пример метода
  getUserProfile(userId) {
    return this.request(`/users/${userId}/`);
  }
}

const apiService = new ApiService();
export default apiService;
