import React from 'react';
import { useSelector } from 'react-redux';
import DataLoader from './components/DataLoader';

function App() {
  const users = useSelector(state => state.users);
  const posts = useSelector(state => state.posts);

  const getUserName = (userId) => {
    const user = users.find(user => user.id === userId);
    return user ? user.name : 'Неизвестный пользователь';
  };

  return (
    <div className="App">
      <DataLoader />
      <h1>Список постов с авторами</h1>
      {posts.map(post => (
        <div key={post.id} style={{
          border: '1px solid #ddd',
          margin: '10px 0',
          padding: '15px',
          borderRadius: '5px'
        }}>
          <div style={{ fontWeight: 'bold', color: '#007bff' }}>
            Автор: {getUserName(post.userId)}
          </div>
          <h3>{post.title}</h3>
          <p>{post.body}</p>
        </div>
      ))}
    </div>
  );
}

export default App;
