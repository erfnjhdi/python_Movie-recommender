import React from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
import SearchMovie from './searchMovie';

const root = createRoot(document.getElementById('root'));

class Main extends React.Component {
    render() {
      return (
        <div className="container">
            <h1 className="title">Movie Search</h1>
            <SearchMovie />
        </div>
      );
    }
  }
  
  
  root.render(<Main />);
