import axios from 'axios';

// Read env variables
const apiUrl = process.env.REACT_APP_WEBSERVICE_URL;
const ftpServerUrl = process.env.REACT_APP_FTP_SERVER_URL;

if (!apiUrl || !ftpServerUrl) {
  console.error('API URL or FTP Server URL not set');
}

// Create an instance of axios with default headers
const api = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
      withCredentials: true // This allows cookies to be sent with each request
  }
});

// create an instance of axios for ftp server
const ftpApi = axios.create({
  baseURL: ftpServerUrl,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Set up axios request interceptor
api.interceptors.request.use(config => {
  // Add logic to dynamically set headers (e.g., authorization token)
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  return config;
}, error => Promise.reject(error));

// Set up axios response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Handle common error codes
      switch (error.response.status) {
        case 401: // Unauthorized
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          break;
        // Add more cases as needed for other status codes
        default:
          console.error(`HTTP error: ${error.response.status}`);
      }
    }
    return Promise.reject(error);
  }
);

export const signUp = (data) => api.post('/api/users/signup', data);
export const login = (data) => api.post('/token', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
export const getTasks = (params) => api.get('/api/tasks/', { params: params });
export const getTask = (id) => api.get(`/api/tasks/${id}`);
export const createTask = (data) => api.post('/api/tasks/', data, { headers: { 'Content-Type': 'application/multipart/form-data' } });
export const updateTask = (id, data) => api.put(`/api/tasks/${id}`, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
export const deleteTask = (id) => api.delete(`/api/tasks/${id}`);
export const getUsers = () => api.get('/api/users/');
export const getTaskHtml = (htmlfile) => ftpApi.get(htmlfile);
