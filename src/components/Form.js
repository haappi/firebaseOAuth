import React, { useState } from 'react';
import axios from 'axios';

const SecretForm = () => {
	const [formData, setFormData] = useState({
		client_id: '',
		client_secret: '',
		firebase_secret: '',
		auto_firebase: false,
	});

	const handleInputChange = (e) => {
		const { name, value, type, checked } = e.target;
		setFormData({
			...formData,
			[name]: type === 'checkbox' ? checked : value,
		});
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		try {
			const response = await axios.post('/dashboard/create', formData);
			console.log(response.data);
		} catch (error) {
			console.error('Error creating secret:', error);
		}
	};

	return (
		<form className="max-w-lg mx-auto mt-8" onSubmit={handleSubmit}>
			<div className="mb-4">
				<label htmlFor="client_id" className="block text-gray-700 font-bold mb-2">
					Client ID
				</label>
				<input
					type="text"
					id="client_id"
					name="client_id"
					value={formData.client_id}
					onChange={handleInputChange}
					className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300"
					required
				/>
			</div>

			<div className="mb-4">
				<label htmlFor="client_secret" className="block text-gray-700 font-bold mb-2">
					Client Secret
				</label>
				<input
					type="text"
					id="client_secret"
					name="client_secret"
					value={formData.client_secret}
					onChange={handleInputChange}
					className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300"
					required
				/>
			</div>

			<div className="mb-4">
				<label htmlFor="firebase_secret" className="block text-gray-700 font-bold mb-2">
					Firebase Secret
				</label>
				<textarea
					id="firebase_secret"
					name="firebase_secret"
					value={formData.firebase_secret}
					onChange={handleInputChange}
					rows="4"
					className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300"
				/>
			</div>

			<div className="mb-4">
				<label className="block text-gray-700 font-bold mb-2">Auto Firebase</label>
				<label className="flex items-center">
					<input
						type="checkbox"
						name="auto_firebase"
						checked={formData.auto_firebase}
						onChange={handleInputChange}
						className="mr-2"
					/>
					<span className="text-sm">Enable Auto Firebase</span>
				</label>
			</div>

			<button
				type="submit"
				className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring focus:border-blue-300"
			>
				Create Secret
			</button>
		</form>
	);
};

export default SecretForm;
