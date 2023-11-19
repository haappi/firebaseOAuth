// src/components/ApiCallButton.js

import React from 'react';

const ApiCallButton = () => {
	const handleApiCall = async () => {
		try {
			// Make an API call using the utility function
			const apiResponse = await ('your-api-endpoint', 'POST', { /* your request payload */ });

			// Handle the API response as needed
			console.log('API Response:', apiResponse);
		} catch (error) {
			// Handle API call errors (e.g., show an error message)
			console.error('API Call Failed:', error.message);
		}
	};

	return (
		<button onClick={handleApiCall} className="bg-blue-500 text-white px-4 py-2 rounded">
			Call My API
		</button>
	);
};

export default ApiCallButton;
