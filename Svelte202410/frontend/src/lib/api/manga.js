import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const mangaApi = {
    async getMangas(page = 1, limit = 12) {
        const response = await axios.get(`${API_URL}/mangas?page=${page}&size=${limit}`);
        return response.data;
    },
    
    async searchMangas(query, page = 1, limit = 12) {
        const response = await axios.get(
            `${API_URL}/mangas?search=${query}&page=${page}&size=${limit}`
        );
        return response.data;
    }
};