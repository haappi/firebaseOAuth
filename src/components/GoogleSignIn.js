import React, {useState} from "react";
import axios from "axios";

const GoogleSignInButton = () => {
	const [isPressed, setIsPressed] = useState(false);

	const handleClick = () => {
		setIsPressed(true);

		setTimeout(() => {
			setIsPressed(false);
		}, 100);

		window.location = 'https://staging.quack.boo/school/oauth/login';
	};

	return (
		<img
			className={`google-btn ${isPressed ? 'pressed' : ''}`}
			src="/sign_in_google.svg"
			alt="Google Icon"
			style={{
				transform: isPressed ? 'translateY(10px)' : 'translateY(0)',
				transition: 'transform 0.1s',
			}}
			onClick={handleClick}
		/>
	);
};

export default GoogleSignInButton;
