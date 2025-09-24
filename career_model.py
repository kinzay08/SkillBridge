import requests
from typing import Optional

def ask_career_bot(user_input: str) -> str:
    """Main career bot function using Groq API"""
    
    # Put your Groq API key here
    GROQ_API_KEY = "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"  # Replace with your actual Groq key
    
    # If no API key provided, use backup advice
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        return get_backup_advice(user_input)
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [
                    {"role": "system", "content": "You are a professional career counselor and interview coach. Give practical, actionable career advice in 2-3 sentences. Be specific and helpful."},
                    {"role": "user", "content": user_input}
                ],
                "model": "llama3-8b-8192",
                "max_tokens": 200,
                "temperature": 0.7
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        elif response.status_code == 401:
            return "Error: Invalid Groq API key. Please check your key at console.groq.com"
        elif response.status_code == 429:
            return "Rate limit reached. Using backup advice: " + get_backup_advice(user_input)
        else:
            return get_backup_advice(user_input)
            
    except requests.exceptions.Timeout:
        return "Request timed out. Using backup advice: " + get_backup_advice(user_input)
    except requests.exceptions.RequestException:
        return get_backup_advice(user_input)
    except Exception:
        return get_backup_advice(user_input)

def get_backup_advice(user_input: str) -> str:
    """Enhanced career advice based on keywords"""
    user_lower = user_input.lower()
    
    # Interview preparation
    if any(word in user_lower for word in ["interview", "interviewing"]):
        if "technical" in user_lower or "coding" in user_lower:
            return "For technical interviews: Practice coding problems on LeetCode daily. Review data structures (arrays, linked lists, trees, graphs) and algorithms (sorting, searching, dynamic programming). Practice explaining your code step-by-step and discussing time/space complexity. Mock interview with friends or use platforms like Pramp."
        elif "behavioral" in user_lower:
            return "For behavioral interviews: Use the STAR method (Situation, Task, Action, Result). Prepare 5-7 specific examples covering teamwork, leadership, conflict resolution, and problem-solving. Research the company's values and culture. Practice with mock interviews and record yourself to improve delivery."
        else:
            return "Interview preparation: Research the company and role thoroughly. Prepare thoughtful questions about team dynamics, growth opportunities, and challenges. Practice common questions out loud. Plan your outfit and route in advance. Follow up within 24 hours with a personalized thank-you email."
    
    # Resume and CV advice
    elif any(word in user_lower for word in ["resume", "cv"]):
        return "Resume best practices: Keep it to 1-2 pages with clear sections (Summary, Experience, Education, Skills). Use action verbs and quantify achievements with specific numbers/percentages. Tailor keywords for each application to pass ATS systems. Use consistent formatting and professional fonts. Proofread multiple times and have others review it."
    
    # Skills and learning
    elif any(word in user_lower for word in ["skill", "learn", "technology"]):
        if "programming" in user_lower or "coding" in user_lower:
            return "Programming skills: Start with one language (Python for beginners, JavaScript for web development). Build real projects and put them on GitHub. Join coding communities like freeCodeCamp or The Odin Project. Contribute to open-source projects. Create a portfolio website showcasing your work."
        elif "data" in user_lower:
            return "Data skills: Master SQL for database queries, Python/R for analysis, and Excel for basic tasks. Learn data visualization with Tableau or Power BI. Practice with real datasets on Kaggle. Complete Google Data Analytics or IBM Data Science certificates. Build a portfolio with 3-5 data projects."
        else:
            return "Skill development: Identify the top 3-5 skills in your target field through job postings analysis. Use free resources like Coursera, edX, or YouTube for learning. Practice daily with hands-on projects. Join professional communities and attend virtual events. Get industry certifications when relevant."
    
    # Career change
    elif any(word in user_lower for word in ["career change", "transition", "switch"]):
        return "Career transition strategy: Map your transferable skills to the new field requirements. Network extensively through LinkedIn, industry events, and informational interviews. Consider a gradual transition through side projects or part-time work. Update your skills with online courses or bootcamps. Craft a compelling narrative explaining your career change motivation."
    
    # Salary negotiation
    elif any(word in user_lower for word in ["salary", "negotiate", "pay"]):
        return "Salary negotiation: Research market rates using Glassdoor, PayScale, and industry reports. Document your achievements and unique value proposition. Practice your negotiation conversation beforehand. Consider total compensation (benefits, PTO, remote work options). Wait for an offer before negotiating and be prepared to justify your request with data."
    
    # Networking
    elif any(word in user_lower for word in ["networking", "network"]):
        return "Networking strategies: Optimize your LinkedIn profile with a professional photo and detailed experience section. Engage with industry content by commenting thoughtfully on posts. Attend virtual and in-person industry events. Offer help to your network before asking for favors. Follow up with new connections within 48 hours with personalized messages."
    
    # Remote work
    elif any(word in user_lower for word in ["remote", "work from home"]):
        return "Remote work success: Create a dedicated workspace with good lighting and minimal distractions. Establish clear work hours and communicate them to your team. Over-communicate progress through regular updates and check-ins. Use productivity tools like time-tracking apps and project management software. Schedule virtual coffee chats to maintain relationships."
    
    # LinkedIn optimization
    elif any(word in user_lower for word in ["linkedin", "profile"]):
        return "LinkedIn optimization: Use a professional headshot and compelling headline that goes beyond your job title. Write a summary that tells your story and includes relevant keywords. Add specific achievements to your experience section with numbers. Request recommendations from colleagues. Post industry-relevant content regularly to increase visibility."
    
    # Job search
    elif any(word in user_lower for word in ["job search", "finding job", "job hunt"]):
        return "Job search strategy: Apply to 10-15 carefully selected positions weekly rather than mass applications. Use multiple channels: company websites, LinkedIn, job boards, and networking. Customize your resume for each application. Track applications in a spreadsheet. Follow up on applications after 1-2 weeks. Consider working with recruiters in your field."
    
    # General career advice
    else:
        return f"I can provide detailed guidance on your question about '{user_input}'. I specialize in: interview prep (technical & behavioral), resume optimization, skill development, career transitions, salary negotiation, networking, remote work tips, LinkedIn optimization, and job search strategies. What specific area needs the most attention?"