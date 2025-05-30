import React from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
import SearchMovie from './searchMovie';

const root = createRoot(document.getElementById('root'));

class Main extends React.Component {
    render() {
      return (
        <>
          <div className="hero">
            <div className="hero-overlay">
              <div className="container">
                <h1 className="hero-text">Uncover Hidden Gems & Blockbusters</h1>
                <p className="hero-subtext">Search for your favorite movie and get personalized recommendations based on your taste instantly.</p>
              </div>
            </div>
          </div>
          <div className='search-container'>
            <div className="container">
                <SearchMovie />
            </div>
          </div>
        </>
      );
    }
  }
  
  
  root.render(<Main />);
