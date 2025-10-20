import React from 'react';
import { useNavigate } from 'react-router-dom';
import './About.css';

const About: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="about">
      <div className="about-content">
        <button className="back-button" onClick={() => navigate('/')}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>

        <div className="about-header">
          <div className="nc-ask-logo">
            {/* Inline SVG so it can inherit currentColor and respond to dark mode */}
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor" className="brain-icon" role="img" aria-label="Neurology">
              <path d="M390-120q-51 0-88-35.5T260-241q-60-8-100-53t-40-106q0-21 5.5-41.5T142-480q-11-18-16.5-38t-5.5-42q0-61 40-105.5t99-52.5q3-51 41-86.5t90-35.5q26 0 48.5 10t41.5 27q18-17 41-27t49-10q52 0 89.5 35t40.5 86q59 8 99.5 53T840-560q0 22-5.5 42T818-480q11 18 16.5 38.5T840-400q0 62-40.5 106.5T699-241q-5 50-41.5 85.5T570-120q-25 0-48.5-9.5T480-156q-19 17-42 26.5t-48 9.5Zm130-590v460q0 21 14.5 35.5T570-200q20 0 34.5-16t15.5-36q-21-8-38.5-21.5T550-306q-10-14-7.5-30t16.5-26q14-10 30-7.5t26 16.5q11 16 28 24.5t37 8.5q33 0 56.5-23.5T760-400q0-5-.5-10t-2.5-10q-17 10-36.5 15t-40.5 5q-17 0-28.5-11.5T640-440q0-17 11.5-28.5T680-480q33 0 56.5-23.5T760-560q0-33-23.5-56T680-640q-11 18-28.5 31.5T613-587q-16 6-31-1t-20-23q-5-16 1.5-31t22.5-20q15-5 24.5-18t9.5-30q0-21-14.5-35.5T570-760q-21 0-35.5 14.5T520-710Zm-80 460v-460q0-21-14.5-35.5T390-760q-21 0-35.5 14.5T340-710q0 16 9 29.5t24 18.5q16 5 23 20t2 31q-6 16-21 23t-31 1q-21-8-38.5-21.5T279-640q-32 1-55.5 24.5T200-560q0 33 23.5 56.5T280-480q17 0 28.5 11.5T320-440q0 17-11.5 28.5T280-400q-21 0-40.5-5T203-420q-2 5-2.5 10t-.5 10q0 33 23.5 56.5T280-320q20 0 37-8.5t28-24.5q10-14 26-16.5t30 7.5q14 10 16.5 26t-7.5 30q-14 19-32 33t-39 22q1 20 16 35.5t35 15.5q21 0 35.5-14.5T440-250Zm40-230Z"/>
            </svg>
            <h1 className="app-title">NC Ask</h1>
          </div>
        </div>
        
        <div className="about-description">
          <p>
            Led by Dr. Rohan Patel, a Developmental Behavioral Pediatrician, NC Autism 
            Support and Knowledge (ASK) addresses a critical need he sees every day in his 
            work. As a developmental pediatrician and clinical informatician who treats 
            children with Autism Spectrum Disorder (ASD), he witnessed firsthand the 
            immense challenges families and providers face with information overload and 
            the complexities of navigating healthcare, insurance, and educational systems.
          </p>
          
          <p>
            NC ASK is an educational tool, driven by an LLM application that provides clear, 
            tailored, and actionable guidance, cutting through the noise to deliver reliable 
            information.
          </p>
        </div>
        
        <div className="feature-badges">
          <div className="feature-badge">Family-centered</div>
          <div className="feature-badge">Simple to use</div>
          <div className="feature-badge">Safe & secure</div>
        </div>
      </div>
    </div>
  );
};

export default About;