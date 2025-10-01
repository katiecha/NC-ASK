import React from 'react';
import './About.css';

const About: React.FC = () => {
  return (
    <div className="about">
      <div className="about-content">
        <div className="about-header">
          <div className="nc-ask-logo">
            <img src="/neurology.svg" alt="Neurology" className="brain-icon" />
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