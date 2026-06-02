import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setUsers } from '../store/usersSlice';
import { setPosts } from '../store/postsSlice';

const DataLoader = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const loadData = async () => {
      try {
        const [usersRes, postsRes] = await Promise.all([
          fetch('/users.json'),
          fetch('/posts.json'),
        ]);
        const users = await usersRes.json();
        const posts = await postsRes.json();

        dispatch(setUsers(users));
        dispatch(setPosts(posts));
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
      }
    };
    loadData();
  }, [dispatch]);

  return null;
};

export default DataLoader;
