import React from 'react';
import { Authenticator } from '@aws-amplify/ui-react';
import { useNavigate } from 'react-router-dom';
import '@aws-amplify/ui-react/styles.css';
import './Login.css';

function LoginPage() {
  const navigate = useNavigate();
  
  return (
    <Authenticator>
      {({ signOut, user }) => {
        // Redirect to home page upon successful login
        if (user) {
          navigate('/home');
        }

        return (
          <div>
            <h1>Welcome, {user.username}</h1>
            <button onClick={signOut}>Sign out</button>
          </div>
        );
      }}
    </Authenticator>
  );
}

export default LoginPage;