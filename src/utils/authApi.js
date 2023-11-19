// src/utils/authApi.js

import axios from 'axios';

const API_BASE_URL = 'https://chicago.quack.boo/school/oauth';

const authenticateUser = async (credentials) => {
	try {
		const response = await axios.post(`${API_BASE_URL}/login`, credentials);
		// Handle the response as needed
		return response.data;
	} catch (error) {
		// Handle errors (e.g., display an error message)
		throw error;
	}
};

export default authenticateUser;
