# NC-ASK Safety & Crisis Detection

## Overview

NC-ASK includes built-in crisis detection to identify when users may be experiencing a mental health emergency and immediately provide them with appropriate crisis support resources. This system is designed to be **always-on**, **privacy-preserving**, and **fail-safe**.

## How Crisis Detection Works

### Detection Method

NC-ASK uses **keyword-based detection** to identify crisis situations in user queries. The system operates in real-time as part of the RAG pipeline and triggers before, during, or after the standard response generation.

### Three-Tier Severity Classification

Queries are classified into one of four severity levels:

#### 1. Critical (Highest Priority)
**Keywords**: suicide, suicidal, kill myself, end my life, want to die, going to die, better off dead, no reason to live, plan to hurt myself, plan to kill

**Action**: Immediate crisis banner with all resources displayed prominently

#### 2. High Priority
**Keywords**: self harm, self-harm, cut myself, hurt myself, overdose, pills, harm to others, hurt someone, abuse, neglect, violence

**Action**: Crisis banner with crisis resources displayed

#### 3. Moderate Priority
**Keywords**: hopeless, can't go on, unbearable, desperate, crisis, emergency, help me please

**Action**: Crisis banner with support resources

#### 4. None
No crisis keywords detected. Standard response provided.

### Implementation Details
- **Location**: `backend/services/crisis_detection.py`
- **Class**: `KeywordCrisisDetector`
- **Detection**: Case-insensitive substring matching

## Crisis Resources Provided

When a crisis is detected, users are **immediately** shown:

### 1. 988 Suicide & Crisis Lifeline (Priority 1)
- **Phone**: 988
- **Description**: 24/7 free and confidential support for people in distress
- **Website**: https://988lifeline.org/
- **Availability**: Call or text, 24/7

### 2. Crisis Text Line (Priority 2)
- **Phone**: Text HOME to 741741
- **Description**: 24/7 text-based crisis support
- **Website**: https://www.crisistextline.org/

### 3. NC Hope4NC Helpline (Priority 3)
- **Phone**: 1-855-587-3463
- **Description**: North Carolina's free 24/7 crisis and emotional support line
- **Website**: https://www.mhanc.org/hope4nc/

### 4. Emergency Services (Priority 4)
- **Phone**: 911
- **Description**: For immediate life-threatening emergencies


## Privacy & Logging
### What We Log
- **Severity level** (critical, high, moderate)
- **Matched keywords** (e.g., "suicidal", "hopeless")
- **Session ID** (ephemeral, not linked to user identity)
- **Timestamp**

### Logging Example
```
2025-11-05 12:34:56 WARNING CRITICAL crisis detected. Keywords: ['suicidal', 'want to die']
```

This de-identified approach allows us to:
- Monitor system effectiveness
- Improve detection algorithms
- Ensure the system is working
- Without compromising user privacy or storing sensitive information

### Known Limitations

1. **Keyword-Based Detection**: May miss crises expressed without trigger keywords
2. **No Context Analysis**: Cannot understand complex or nuanced situations
3. **False Positives Possible**: Academic or hypothetical discussions may trigger detection
4. **English Only**: Currently only detects English-language crisis keywords
5. **No Follow-Up**: System cannot track if user contacted resources

### Legal Disclaimer

NC-ASK displays the following disclaimer on all responses:

> **Disclaimer**: NC-ASK is an educational tool and does not provide medical, legal, or crisis intervention services. Information provided is for educational purposes only. Always consult qualified professionals for medical advice, legal guidance, or crisis support. In emergencies, call 911 or contact the 988 Suicide & Crisis Lifeline.