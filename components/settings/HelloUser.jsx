import React from 'react';

const HelloUser = ({ username }) => {
  return (
    <div style={{ padding: '10px', fontSize: '20px', fontWeight: 'bold', textAlign: 'center', display: 'flex', justifyContent: 'center' }}>
      Hello, {username || 'User'}!
    </div>
  );
};

export default HelloUser;
