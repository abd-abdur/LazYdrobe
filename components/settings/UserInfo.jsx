import React, { useState, useEffect } from 'react';

const UserInfo = ({ initialUserInfo = {} }) => {
  const [userInfo, setUserInfo] = useState({
    feet: '',
    inches: '',
    gender: '',
    ...initialUserInfo, // Prefill if initialUserInfo is provided
  });

  useEffect(() => {
    if (initialUserInfo) {
      setUserInfo((prevInfo) => ({
        ...prevInfo,
        ...initialUserInfo,
      }));
    }
  }, [initialUserInfo]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === 'inches') {
      const inchesValue = parseFloat(value);
      if (isNaN(inchesValue) || inchesValue < 0 || inchesValue >= 12) return;
    }

    setUserInfo((prevInfo) => ({
      ...prevInfo,
      [name]: value,
    }));
  };

  return (
    <div style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px', maxWidth: '300px', margin: '0 auto' }}>
      <h3>User Information</h3>
      <label>
        Height:
        <div style={{ display: 'flex', gap: '10px', margin: '8px 0' }}>
          <input
            type="number"
            name="feet"
            value={userInfo.feet}
            onChange={handleChange}
            placeholder="Feet"
            style={{ padding: '4px', width: '50px' }}
          />
          <input
            type="number"
            name="inches"
            value={userInfo.inches}
            onChange={handleChange}
            placeholder="Inches"
            step="0.1"
            style={{ padding: '4px', width: '55px' }}
          />
        </div>
      </label>
      <label>
        Gender:
        <input
          type="text"
          name="gender"
          value={userInfo.gender}
          onChange={handleChange}
          placeholder="e.g., Female"
          style={{ display: 'block', margin: '8px 0', padding: '4px', width: '100%' }}
        />
      </label>
      <div>
        <strong>Height:</strong> {userInfo.feet ? `${userInfo.feet}'` : ''} {userInfo.inches ? `${userInfo.inches}"` : ''}
      </div>
      <div>
        <strong>Gender:</strong> {userInfo.gender || 'Not specified'}
      </div>
    </div>
  );
};

export default UserInfo;
