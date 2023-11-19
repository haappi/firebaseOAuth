import logo from './logo.svg';
import './App.css';
import Form from "./components/Form";
import LoginForm from "./components/LoginForm";
import GoogleSignInButton from "./components/GoogleSignIn";

function App() {
  return (
    <div className="App">
      <header className="App-header">
          <GoogleSignInButton />
      </header>
    </div>
  );
}

export default App;
