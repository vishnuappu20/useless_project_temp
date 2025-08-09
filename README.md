<img width="3188" height="1202" alt="frame (3)" src="https://github.com/user-attachments/assets/517ad8e9-ad22-457d-9538-a9e62d137cd7" />


# SHAPE DETECTOR 


## Basic Details
### Team Name:[HACK ACADEMIA 3.0]


### Team Members
- Team Lead: [VISHNU HAREENDRAN] - [COLLEGE OF ENGINEERING THALASSERY]
- Member 2: [ASWANA ASHOK] - [COLLEGE OF ENGINEERING THALASSERY]
  

### Project Description
The Shape Detector site is a playful, minimal web app where users can either draw shapes on a digital canvas or upload images containing shapes, and the system will identify them—often with an intentionally sarcastic or humorous twist.

Landing Page:
A clean introduction to the project with a catchy tagline (“Draw, Upload, Detect… Pointlessly!”), a visual preview of the app, and buttons to open the application or learn more. The header holds the logo and name, while the footer contains credits, license info, and links.

App Interface (Desktop):
The screen is split into two main sections:

Canvas Area: Tools to draw, erase, clear, undo, and start detection.

Result Panel: Shows the detected shape, a confidence percentage, and a witty comment, plus the option to save results.
A fixed footer provides quick credits and instructions for running the app locally.

Mobile Layout:
Optimized for small screens with a full-width canvas and large touch-friendly buttons for drawing, uploading, detecting, and clearing. Results are shown in a collapsible panel below the canvas.

Overall, the site is designed to be fun, interactive, and simple—half useful for detecting shapes, half comedic in how it presents the results.

### The Problem (that doesn't exist)
Millions of people wake up every morning unsure whether the thing they just drew is a circle, a square, or a badly executed potato. This lack of shape self-confidence causes confusion, unproductive meetings, and even ruined picnics because no one can agree if the sandwich is “more rectangular than triangular.” The world urgently needs a way to settle pointless shape debates once and for all — preferably with a dash of sarcasm.

### The Solution (that nobody asked for)
  We’re solving the world’s nonexistent shape-identification crisis by throwing way too much tech at it.

Here’s how:

The Digital Canvas – For all your “is it a circle or just a lumpy potato?” scenarios. Draw with the precision of a mouse or the chaos of your finger.

Shape Detection Wizardry – Powered by advanced math, machine learning (well… kinda), and a questionable obsession with polygons.

Sarcasm Delivery System – Every result comes with a sprinkle of snark, because why not hurt your feelings and your shapes at the same time?

History Log – Keep track of every shape you’ve ever drawn so you can look back and wonder why you wasted so much time here.

We’re basically taking OpenCV, sprinkling in a sense of humor, and calling it innovation. Because sometimes, building something utterly useless is the most fun you can have with code

## Technical Details
### Technologies/Components Used
For Software:
- [Python (for backend logic in app.py)
HTML (for web page templates in templates/)
JavaScript (for client-side scripting in static/script.js)
CSS (likely used within your HTML files for styling)
Flask (Python web framework)]
- Frameworks used: Flask (Python web framework)
- Libraries used: OpenCV (cv2), NumPy, base64, re, random, math, collections (Counter)
- Tools used: Python, Flask development server, web browser (for testing), image files (for shape detection)
  
### Implementation
For Software:The backend is implemented using Flask, a lightweight Python web framework. The main logic resides in `app.py`, which handles HTTP requests, renders HTML templates, and processes images for shape detection using OpenCV and NumPy. Users interact with the web interface via HTML pages (`index.html`, `landing.html`), and client-side interactivity is managed by JavaScript (`static/script.js`).

The shape detection works by drwing a shape, which is then analyzed on the server to identify geometric shapes. Results and fun, sarcastic comments are displayed to the user.

# Installation
. Clone the repository:
   ```
   git clone <repo-url>
   ```
2. Navigate to the project directory:
   ```
   cd useless_project_temp
   ```
3. Install required Python packages:
   ```
   pip install flask opencv-python numpy
   ```


# Run
1. Start the Flask development server:

   python app.py
   
2. Open your web browser and go to:
   
   http://127.0.0.1:5000/
   
### Project Documentation
For Software:
 The project consists of a Flask backend (`app.py`) that handles image uploads and shape detection using OpenCV and NumPy.
- HTML templates (`index.html`, `landing.html`) provide the user interface, styled with CSS and enhanced with JavaScript (`static/script.js`).
- Users can draw shapes, and the backend processes these to detect shapes, returning results and fun comments.
- The README includes installation, run instructions, and technical details for easy setup and understanding.
- 
  
# Screenshots (Add at least 3)
<img width="3188" height="1202" alt="frame (3)" src="screenshots/s1 home page.png" />
<img width="3188" height="1202" alt="frame (3)" src="screenshots/s2 home page down part.png" />
<img width="3188" height="1202" alt="frame (3)" src="screenshots/s3 main page.png" />
<img width="3188" height="1202" alt="frame (3)" src="screenshots/s4 main after drawing.png" />
<img width="3188" height="1202" alt="frame (3)" src="screenshots/s4 main page diplaying switches.png" />

# Diagrams
![Workflow](Add your workflow/architecture diagram here)
*Add caption explaining your workflow*

For Hardware:

# Schematic & Circuit
![Circuit](Add your circuit diagram here)
*Add caption explaining connections*

![Schematic](Add your schematic diagram here)
*Add caption explaining the schematic*

# Build Photos
![Components](Add photo of your components here)
*List out all components shown*

![Build](Add photos of build process here)
*Explain the build steps*

![Final](Add photo of final product here)
*Explain the final build*

### Project Demo
# Video
[Add your demo video link here]
*Explain what the video demonstrates*

# Additional Demos
[Add any extra demo materials/links]

## Team Contributions
- [Name 1]: [Specific contributions]
- [Name 2]: [Specific contributions]
- [Name 3]: [Specific contributions]

---
Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--25-25?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)



