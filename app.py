from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import re
import random
import math
from collections import Counter

app = Flask(__name__)

# Focused sarcastic comments for the 5 core shapes only
sarcasm_dict = {
    "Triangle": [
        "🍕 Looks like a slice of pizza someone already ate... and regretted.",
        "🔺 Illuminati confirmed! 👁️ They're watching your drawing skills.",
        "🔥 Oh great, a Dorito that survived the snack apocalypse!",
        "⚠️ Three sides, infinite possibilities... or just basic geometry 101.",
        "🌊 Bermuda Triangle vibes, but your drawing skills are the real mystery!",
        "📐 *Chef's kiss* 👌 Peak triangular excellence right here!",
        "🎪 Ladies and gentlemen, behold... THE TRIANGLE! *crowd goes mild*",
        "🏔️ Mountain peak or geometric masterpiece? You decide! 🗻",
        "🎯 Three points of pure triangular perfection! Nailed it! ✨"
    ],
    "Square": [
        "🟫 Perfect for Minecraft real estate! 🏠 Steve would be proud.",
        "📝 Looks like a post-it note that gave up on life.",
        "📦 Very boxy. Very... *yawn* ...riveting stuff here.",
        "🤖 Four equal sides of pure robotic perfection! BEEP BOOP! 🔧",
        "😎 Squares are hip now, right? RIGHT?! *nervous laughter*",
        "🎯 Nailed it! If 'it' was drawing the most basic shape possible.",
        "🏆 Winner of the 'Most Predictable Shape' award! 🥇",
        "🧊 Ice cube vibes! Cool and perfectly square! ❄️",
        "🎲 Dice without the dots! Ready to roll! 🎮",
        "🔲 Square perfection achieved! Geometry teachers everywhere rejoice! 📚"
    ],
    "Rectangle": [
        "🚪 Could be a door... or a coffin. Your artistic future, perhaps? ⚰️",
        "📱 Looks like a Nokia 3310! Indestructible, just like this drawing.",
        "😴 *YAWN* Rectangle detected. Wake me up when it gets interesting.",
        "💔 It's like a square that gave up on its dreams and settled.",
        "📺 Ah yes, the classic 'TV screen from 1995' aesthetic! 📼",
        "🎪 Step right up! See the AMAZING... rectangle. *crickets chirping* 🦗",
        "🤷‍♂️ Rectangular excellence at its most... rectangular-y.",
        "🏗️ Building block of architecture! Foundation of boredom! 🧱",
        "📄 Paper sheet perfection! Ready for important documents! 📋"
    ],
    "Circle": [
        "🍪 Looks like a cookie! 🤤 Sadly, pixels aren't edible.",
        "⭕ Perfect circle detected! Michelangelo is rolling in his grave! 🎨",
        "🍩 Is this a donut having an existential crisis? 🤔",
        "🔄 Round and proud! No corners, no problems, no personality! 😅",
        "🎯 360 degrees of 'meh'... I mean, geometric perfection! ✨",
        "🌕 Moon-shaped masterpiece! 🚀 One small step for art, one giant leap for... never mind.",
        "⚽ Sports ball or artistic expression? The world may never know! 🤷‍♀️",
        "🎡 Ferris wheel of artistic achievement! Round and round we go! 🎠",
        "🔴 Red dot special! Minimalism at its finest! 🎨",
        "⭕ O-M-G! Outstanding circular geometry! Perfect roundness achieved! 🏆"
    ],
    "Heart": [
        "💖 Aww, how romantic! If you're into geometric love stories! 📚",
        "💕 Love is in the air... and on your canvas! Cupid approves! 🏹",
        "❤️ Heart-shaped perfection! Your cardiovascular system is jealous! 🫀",
        "💘 I HEART this shape! Get it? HEART? 😂 *slaps knee*",
        "💓 Anatomically questionable but emotionally VALID! 🥺",
        "💖 Love at first sight! This heart has stolen mine! 😍",
        "💕 Romantic geometry! Shakespeare would write sonnets about this! 📝",
        "💝 Gift-wrapped emotion! Love delivered in geometric form! 🎁",
        "💗 Beating with artistic passion! Ba-dum, ba-dum! 🥁",
        "💞 Two hearts become one... wait, that's just one heart! Math is hard! 🤓"
    ],
    "Unknown": [
        "👽 Unidentified Drawing Object spotted! 🛸 *alien noises* BEEP BOOP!",
        "🎨 Abstract expressionism or gave up halfway? 🤷‍♀️ Modern art vibes!",
        "🤯 This shape exists in dimensions I don't understand! 🌌 *mind blown*",
        "🎭 Picasso would be... confused. And that's saying something! 😵‍💫",
        "🚨 SHAPE ALERT! 🚨 We've got a rogue geometry situation here! 👮‍♂️",
        "🎪 Ladies and gentlemen... THE MYSTERY SHAPE! 🎭 *dramatic gasp*",
        "🔮 Fortune teller says: 'Your shape's future is... unclear!' ✨",
        "🤖 ERROR 404: Shape not found! 💻 *computer noises*",
        "🎨 This is either genius or... well, let's go with genius! 🏆",
        "🦄 Mythical geometry detected! Unicorns are jealous! ✨",
        "🎲 Random shape generator activated! Chaos theory in action! 🌪️",
        "🌀 Shape-shifting masterpiece! Defying all known geometry! 🔄"
    ]
}

def detect_shape(img):
    """Optimized detection for 5 core shapes: Square, Rectangle, Circle, Triangle, Heart"""
    output = img.copy()
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    
    # Enhanced preprocessing specifically for the 5 core shapes
    preprocessed = optimized_preprocessing_for_core_shapes(gray)
    
    # Specialized detection methods for each core shape
    detected_shapes = []
    
    # Priority detection order: Circle first (most distinctive), then Square, Triangle, Rectangle, Heart
    circle_result = detect_circle_optimized(preprocessed)
    if circle_result:
        detected_shapes.append(circle_result)
    
    square_result = detect_square_optimized(preprocessed)
    if square_result:
        detected_shapes.append(square_result)
    
    triangle_result = detect_triangle_optimized(preprocessed)
    if triangle_result:
        detected_shapes.append(triangle_result)
    
    rectangle_result = detect_rectangle_optimized(preprocessed)
    if rectangle_result:
        detected_shapes.append(rectangle_result)
    
    heart_result = detect_heart_optimized(preprocessed)
    if heart_result:
        detected_shapes.append(heart_result)
    
    if detected_shapes:
        # Sort by confidence and return the best match
        detected_shapes.sort(key=lambda x: x['confidence'], reverse=True)
        best_shape = detected_shapes[0]
        
        shape_name = best_shape['name']
        confidence = best_shape['confidence']
        sarcasm = random.choice(sarcasm_dict.get(shape_name, sarcasm_dict["Unknown"]))
        
        # Add confidence indicator
        confidence_emoji = get_confidence_emoji(confidence)
        return f"{shape_name} {confidence_emoji} – {sarcasm}"
    
    return "🤖 No shapes detected – Try drawing something that actually exists! 🎨"

def optimized_preprocessing_for_core_shapes(gray):
    """Optimized preprocessing specifically for the 5 core shapes"""
    # Stage 1: Bilateral filter for noise reduction while preserving edges
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Stage 2: Adaptive histogram equalization for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Stage 3: Gaussian blur optimized for shape detection
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # Stage 4: Combined thresholding approach
    # Otsu's method for automatic threshold selection
    _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Adaptive thresholding for varying lighting conditions
    thresh_adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Combine both methods for robustness
    thresh_combined = cv2.bitwise_or(thresh_otsu, thresh_adaptive)
    
    # Stage 5: Morphological operations optimized for core shapes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    
    # Close small gaps
    closed = cv2.morphologyEx(thresh_combined, cv2.MORPH_CLOSE, kernel)
    
    # Remove small noise
    cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
    
    return cleaned

def detect_circle_optimized(preprocessed):
    """Ultra-optimized circle detection using multiple methods"""
    # Method 1: Hough Circle Transform (most reliable for circles)
    circles = cv2.HoughCircles(
        preprocessed, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
        param1=50, param2=30, minRadius=15, maxRadius=300
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        # Return the most confident circle detection
        return {
            'name': 'Circle',
            'confidence': 0.95,
            'method': 'hough_optimized'
        }
    
    # Method 2: Contour-based circle detection
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # Minimum area threshold
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Calculate circularity (4π*Area/Perimeter²)
        circularity = 4 * math.pi * area / (perimeter * perimeter)
        
        # Get bounding rectangle for aspect ratio
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # High circularity + good aspect ratio = circle
        if circularity > 0.75 and 0.8 <= aspect_ratio <= 1.2:
            confidence = min(0.9, 0.6 + circularity * 0.4)
            return {
                'name': 'Circle',
                'confidence': confidence,
                'method': 'contour_optimized'
            }
    
    return None

def detect_square_optimized(preprocessed):
    """Ultra-optimized square detection with enhanced precision"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # Minimum area threshold
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Multiple approximation levels for better accuracy
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # Must have exactly 4 vertices
        if len(approx) != 4:
            continue
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Square criteria: aspect ratio close to 1
        if 0.9 <= aspect_ratio <= 1.1:
            # Additional validation: check if sides are approximately equal
            points = approx.reshape(-1, 2)
            side_lengths = []
            
            for i in range(4):
                side = points[(i + 1) % 4] - points[i]
                length = np.linalg.norm(side)
                side_lengths.append(length)
            
            # Check side length consistency
            avg_length = np.mean(side_lengths)
            side_variance = np.var(side_lengths)
            
            # Low variance indicates equal sides (square)
            if side_variance < (avg_length * 0.1) ** 2:
                # Calculate confidence based on how "square" it is
                aspect_score = 1.0 - abs(1.0 - aspect_ratio)
                side_score = 1.0 - (side_variance / (avg_length ** 2))
                confidence = min(0.95, 0.7 + aspect_score * 0.15 + side_score * 0.1)
                
                return {
                    'name': 'Square',
                    'confidence': confidence,
                    'method': 'contour_optimized'
                }
    
    return None

def detect_triangle_optimized(preprocessed):
    """Optimized triangle detection"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Approximate the contour
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # Must have exactly 3 vertices
        if len(approx) == 3:
            # Calculate solidity (area/convex hull area)
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # Triangles should have high solidity
            if solidity > 0.8:
                confidence = min(0.9, 0.7 + solidity * 0.2)
                return {
                    'name': 'Triangle',
                    'confidence': confidence,
                    'method': 'contour_optimized'
                }
    
    return None

def detect_rectangle_optimized(preprocessed):
    """Optimized rectangle detection (excluding squares)"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # Must have exactly 4 vertices
        if len(approx) != 4:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Rectangle criteria: NOT square (aspect ratio significantly different from 1)
        if aspect_ratio < 0.85 or aspect_ratio > 1.15:
            # Additional validation: check if opposite sides are parallel
            points = approx.reshape(-1, 2)
            
            # Calculate side vectors
            sides = []
            for i in range(4):
                side = points[(i + 1) % 4] - points[i]
                sides.append(side)
            
            # Check if opposite sides are parallel
            def are_parallel(v1, v2, tolerance=0.3):
                v1_norm = v1 / np.linalg.norm(v1)
                v2_norm = v2 / np.linalg.norm(v2)
                cross = abs(np.cross(v1_norm, v2_norm))
                return cross < tolerance
            
            parallel_pairs = 0
            if are_parallel(sides[0], sides[2]):
                parallel_pairs += 1
            if are_parallel(sides[1], sides[3]):
                parallel_pairs += 1
            
            if parallel_pairs == 2:
                # Calculate confidence based on rectangularity
                rect_score = min(aspect_ratio, 1.0/aspect_ratio) if aspect_ratio > 0 else 0
                confidence = min(0.9, 0.6 + rect_score * 0.3)
                
                return {
                    'name': 'Rectangle',
                    'confidence': confidence,
                    'method': 'contour_optimized'
                }
    
    return None

def detect_heart_optimized(preprocessed):
    """Optimized heart detection using template matching and geometric analysis"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 800:  # Hearts need larger minimum area
            continue
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Hearts typically have specific aspect ratio (wider at top, pointed at bottom)
        if 0.7 <= aspect_ratio <= 1.4:
            # Calculate solidity
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # Hearts have moderate solidity due to the indent at the top
            if 0.6 <= solidity <= 0.85:
                # Calculate moments for shape analysis
                moments = cv2.moments(contour)
                if moments["m00"] != 0:
                    hu_moments = cv2.HuMoments(moments)
                    
                    # Heart-specific Hu moment characteristics
                    if (0.1 < abs(hu_moments[0]) < 0.4 and 
                        abs(hu_moments[1]) < 0.1 and 
                        abs(hu_moments[2]) < 0.05):
                        
                        confidence = min(0.85, 0.6 + solidity * 0.25)
                        return {
                            'name': 'Heart',
                            'confidence': confidence,
                            'method': 'contour_optimized'
                        }
    
    return None

def get_confidence_emoji(confidence):
    """Return emoji based on confidence level"""
    if confidence >= 0.9:
        return "🎯"
    elif confidence >= 0.8:
        return "✨"
    elif confidence >= 0.7:
        return "👍"
    elif confidence >= 0.6:
        return "🤔"
    else:
        return "❓"

def parse_base64_image(data_url):
    img_str = re.search(r'base64,(.*)', data_url).group(1)
    img_bytes = base64.b64decode(img_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/app")
def index():
    return render_template("index.html")

@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Convert to numpy array
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Use the new ultra-enhanced detection method
        result = detect_shape_ultra_enhanced(img)
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': f'Detection failed: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)

def get_confidence_emoji(confidence):
    """Return emoji based on confidence level"""
    if confidence >= 0.9:
        return "🎯"
    elif confidence >= 0.8:
        return "✨"
    elif confidence >= 0.7:
        return "👍"
    elif confidence >= 0.6:
        return "🤔"
    else:
        return "❓"

# Enhanced detection functions for improved accuracy
def advanced_preprocessing_v3(gray):
    """Ultra-enhanced preprocessing for maximum shape detection accuracy"""
    # Stage 1: Advanced noise reduction with edge preservation
    denoised = cv2.bilateralFilter(gray, 11, 80, 80)
    
    # Stage 2: Enhanced contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Stage 3: Multi-scale Gaussian blur for better edge detection
    blur_small = cv2.GaussianBlur(enhanced, (3, 3), 0)
    blur_large = cv2.GaussianBlur(enhanced, (7, 7), 0)
    blurred = cv2.addWeighted(blur_small, 0.7, blur_large, 0.3, 0)
    
    # Stage 4: Advanced thresholding combination
    # Otsu's method
    _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Adaptive thresholding with multiple methods
    thresh_adaptive_mean = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10)
    thresh_adaptive_gaussian = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 10)
    
    # Combine all thresholding methods
    combined = cv2.bitwise_or(thresh_otsu, thresh_adaptive_mean)
    combined = cv2.bitwise_or(combined, thresh_adaptive_gaussian)
    
    # Stage 5: Advanced morphological operations
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_medium = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Close gaps and remove noise
    closed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel_medium)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_small)
    
    return opened

def ultra_enhanced_circle_detection(preprocessed):
    """Ultra-enhanced circle detection with multiple validation methods"""
    # Method 1: Hough Circle Transform with multiple parameter sets
    circles_detected = []
    
    # Try different parameter combinations for robustness
    param_sets = [
        {'dp': 1, 'minDist': 50, 'param1': 50, 'param2': 30, 'minRadius': 15, 'maxRadius': 300},
        {'dp': 1, 'minDist': 40, 'param1': 60, 'param2': 25, 'minRadius': 10, 'maxRadius': 250},
        {'dp': 2, 'minDist': 30, 'param1': 40, 'param2': 35, 'minRadius': 20, 'maxRadius': 200}
    ]
    
    for params in param_sets:
        circles = cv2.HoughCircles(preprocessed, cv2.HOUGH_GRADIENT, **params)
        if circles is not None:
            circles_detected.extend(circles[0, :])
    
    if circles_detected:
        return {
            'name': 'Circle',
            'confidence': 0.95,
            'method': 'hough_enhanced'
        }
    
    # Method 2: Enhanced contour-based circle detection
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Enhanced circularity calculation
        circularity = 4 * math.pi * area / (perimeter * perimeter)
        
        # Bounding rectangle analysis
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Solidity analysis
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        # Enhanced circle criteria with multiple validations
        if (circularity > 0.78 and 
            0.82 <= aspect_ratio <= 1.22 and 
            solidity > 0.88):
            
            # Additional validation: check roundness using moments
            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                # Calculate eccentricity for additional validation
                mu20 = moments["mu20"] / moments["m00"]
                mu02 = moments["mu02"] / moments["m00"]
                mu11 = moments["mu11"] / moments["m00"]
                
                eccentricity = ((mu20 - mu02)**2 + 4*mu11**2) / (mu20 + mu02)**2
                
                if eccentricity < 0.3:  # Low eccentricity indicates circular shape
                    confidence = min(0.92, 0.65 + circularity * 0.35 + solidity * 0.1)
                    return {
                        'name': 'Circle',
                        'confidence': confidence,
                        'method': 'contour_enhanced'
                    }
    
    return None

def ultra_enhanced_square_detection(preprocessed):
    """Ultra-enhanced square detection with precise geometric validation"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Multiple approximation levels for robustness
        approx_tight = cv2.approxPolyDP(contour, 0.015 * perimeter, True)
        approx_medium = cv2.approxPolyDP(contour, 0.025 * perimeter, True)
        
        # Must have exactly 4 vertices
        if len(approx_tight) != 4 and len(approx_medium) != 4:
            continue
        
        # Use the better approximation
        approx = approx_tight if len(approx_tight) == 4 else approx_medium
        
        # Bounding rectangle analysis
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Enhanced square criteria: aspect ratio close to 1
        if 0.88 <= aspect_ratio <= 1.14:
            # Advanced side length analysis
            points = approx.reshape(-1, 2)
            side_lengths = []
            
            for i in range(4):
                side = points[(i + 1) % 4] - points[i]
                length = np.linalg.norm(side)
                side_lengths.append(length)
            
            # Enhanced side consistency check
            avg_length = np.mean(side_lengths)
            side_variance = np.var(side_lengths)
            side_consistency = 1.0 - min(1.0, side_variance / (avg_length * 0.15) ** 2)
            
            # Angle analysis for right angles
            angles = []
            for i in range(4):
                p1 = points[i]
                p2 = points[(i + 1) % 4]
                p3 = points[(i + 2) % 4]
                
                v1 = p1 - p2
                v2 = p3 - p2
                
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = math.degrees(math.acos(np.clip(cos_angle, -1, 1)))
                angles.append(angle)
            
            # Check for right angles (around 90 degrees)
            right_angle_count = sum(1 for angle in angles if 85 <= angle <= 95)
            
            if side_consistency > 0.75 and right_angle_count >= 3:
                # Calculate comprehensive confidence
                aspect_score = 1.0 - abs(1.0 - aspect_ratio)
                angle_score = right_angle_count / 4.0
                confidence = min(0.96, 0.7 + aspect_score * 0.15 + side_consistency * 0.1 + angle_score * 0.01)
                
                return {
                    'name': 'Square',
                    'confidence': confidence,
                    'method': 'contour_ultra_enhanced'
                }
    
    return None

def ultra_enhanced_rectangle_detection(preprocessed):
    """Ultra-enhanced rectangle detection with advanced geometric validation"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Multiple approximation levels
        approx_tight = cv2.approxPolyDP(contour, 0.015 * perimeter, True)
        approx_medium = cv2.approxPolyDP(contour, 0.025 * perimeter, True)
        
        # Must have exactly 4 vertices
        if len(approx_tight) != 4 and len(approx_medium) != 4:
            continue
        
        approx = approx_tight if len(approx_tight) == 4 else approx_medium
        
        # Bounding rectangle analysis
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Rectangle criteria: NOT square (aspect ratio significantly different from 1)
        if aspect_ratio < 0.82 or aspect_ratio > 1.22:
            # Advanced parallel sides validation
            points = approx.reshape(-1, 2)
            
            # Calculate side vectors
            sides = []
            for i in range(4):
                side = points[(i + 1) % 4] - points[i]
                sides.append(side)
            
            # Enhanced parallel check function
            def are_parallel_enhanced(v1, v2, tolerance=0.25):
                v1_norm = v1 / np.linalg.norm(v1)
                v2_norm = v2 / np.linalg.norm(v2)
                cross = abs(np.cross(v1_norm, v2_norm))
                return cross < tolerance
            
            # Check opposite sides for parallelism
            parallel_pairs = 0
            if are_parallel_enhanced(sides[0], sides[2]):
                parallel_pairs += 1
            if are_parallel_enhanced(sides[1], sides[3]):
                parallel_pairs += 1
            
            # Right angle validation
            angles = []
            for i in range(4):
                p1 = points[i]
                p2 = points[(i + 1) % 4]
                p3 = points[(i + 2) % 4]
                
                v1 = p1 - p2
                v2 = p3 - p2
                
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = math.degrees(math.acos(np.clip(cos_angle, -1, 1)))
                angles.append(angle)
            
            right_angle_count = sum(1 for angle in angles if 85 <= angle <= 95)
            
            if parallel_pairs == 2 and right_angle_count >= 3:
                # Enhanced confidence calculation
                rect_score = min(aspect_ratio, 1.0/aspect_ratio) if aspect_ratio > 0 else 0
                parallel_score = parallel_pairs / 2.0
                angle_score = right_angle_count / 4.0
                confidence = min(0.94, 0.65 + rect_score * 0.2 + parallel_score * 0.05 + angle_score * 0.04)
                
                return {
                    'name': 'Rectangle',
                    'confidence': confidence,
                    'method': 'contour_ultra_enhanced'
                }
    
    return None

def ultra_enhanced_triangle_detection(preprocessed):
    """Ultra-enhanced triangle detection with advanced geometric validation"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Multiple approximation levels for robustness
        approx_tight = cv2.approxPolyDP(contour, 0.015 * perimeter, True)
        approx_medium = cv2.approxPolyDP(contour, 0.025 * perimeter, True)
        approx_loose = cv2.approxPolyDP(contour, 0.035 * perimeter, True)
        
        # Must have exactly 3 vertices
        triangle_approx = None
        if len(approx_tight) == 3:
            triangle_approx = approx_tight
        elif len(approx_medium) == 3:
            triangle_approx = approx_medium
        elif len(approx_loose) == 3:
            triangle_approx = approx_loose
        
        if triangle_approx is None:
            continue
        
        # Enhanced solidity calculation
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        # Advanced triangle validation
        if solidity > 0.82:
            # Additional geometric validation
            points = triangle_approx.reshape(-1, 2)
            
            # Calculate side lengths
            side_lengths = []
            for i in range(3):
                side = points[(i + 1) % 3] - points[i]
                length = np.linalg.norm(side)
                side_lengths.append(length)
            
            # Triangle inequality check
            side_lengths.sort()
            if side_lengths[0] + side_lengths[1] > side_lengths[2]:
                # Calculate angles
                angles = []
                for i in range(3):
                    p1 = points[i]
                    p2 = points[(i + 1) % 3]
                    p3 = points[(i + 2) % 3]
                    
                    v1 = p1 - p2
                    v2 = p3 - p2
                    
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    angle = math.degrees(math.acos(np.clip(cos_angle, -1, 1)))
                    angles.append(angle)
                
                # Check if angles sum to approximately 180 degrees
                angle_sum = sum(angles)
                if 175 <= angle_sum <= 185:
                    # Enhanced confidence calculation
                    angle_score = 1.0 - abs(180 - angle_sum) / 180.0
                    confidence = min(0.93, 0.72 + solidity * 0.15 + angle_score * 0.06)
                    
                    return {
                        'name': 'Triangle',
                        'confidence': confidence,
                        'method': 'contour_ultra_enhanced'
                    }
    
    return None

# Now update the main detect_shape function to use the improved detection methods
def detect_shape_ultra_enhanced(img):
    """Ultra-enhanced detection for 4 core shapes: Square, Rectangle, Circle, Triangle"""
    output = img.copy()
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    
    # Use advanced preprocessing
    preprocessed = advanced_preprocessing_v3(gray)
    
    # Specialized ultra-enhanced detection methods for each core shape
    detected_shapes = []
    
    # Priority detection order: Circle first (most distinctive), then Square, Triangle, Rectangle
    circle_result = ultra_enhanced_circle_detection(preprocessed)
    if circle_result:
        detected_shapes.append(circle_result)
    
    square_result = ultra_enhanced_square_detection(preprocessed)
    if square_result:
        detected_shapes.append(square_result)
    
    triangle_result = ultra_enhanced_triangle_detection(preprocessed)
    if triangle_result:
        detected_shapes.append(triangle_result)
    
    rectangle_result = ultra_enhanced_rectangle_detection(preprocessed)
    if rectangle_result:
        detected_shapes.append(rectangle_result)
    
    if detected_shapes:
        # Sort by confidence and return the best match
        detected_shapes.sort(key=lambda x: x['confidence'], reverse=True)
        best_shape = detected_shapes[0]
        
        shape_name = best_shape['name']
        confidence = best_shape['confidence']
        sarcasm = random.choice(sarcasm_dict.get(shape_name, sarcasm_dict["Unknown"]))
        
        # Add confidence indicator
        confidence_emoji = get_confidence_emoji(confidence)
        return f"{shape_name} {confidence_emoji} – {sarcasm}"
    
    return "🤖 No shapes detected – Try drawing something that actually exists! 🎨"

def is_diamond_oriented(approx):
    """Check if a 4-sided polygon is oriented like a diamond"""
    if len(approx) != 4:
        return False
    
    # Calculate angles to determine orientation
    points = approx.reshape(-1, 2)
    angles = []
    
    for i in range(4):
        p1 = points[i]
        p2 = points[(i + 1) % 4]
        p3 = points[(i + 2) % 4]
        
        # Calculate angle
        v1 = p1 - p2
        v2 = p3 - p2
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = math.degrees(math.acos(np.clip(cos_angle, -1, 1)))
        angles.append(angle)
    
    # Check if it's rotated ~45 degrees (diamond orientation)
    # Look for the characteristic angle pattern of a rotated square
    return any(30 < angle < 60 or 120 < angle < 150 for angle in angles)

def is_star_shape(contour, approx):
    """Detect star shapes by analyzing convex defects"""
    hull = cv2.convexHull(contour, returnPoints=False)
    if len(hull) > 3:
        defects = cv2.convexityDefects(contour, hull)
        if defects is not None and len(defects) >= 5:
            # Count significant defects (inward points of star)
            significant_defects = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                if d > 1000:  # Threshold for significant defect
                    significant_defects += 1
            return significant_defects >= 5
    return False

def is_heart_shape(contour, aspect_ratio):
    """Detect heart shapes using geometric properties"""
    # Hearts typically have specific aspect ratio and shape characteristics
    if 0.8 <= aspect_ratio <= 1.4:
        # Check for the characteristic heart shape using moments
        moments = cv2.moments(contour)
        if moments["m00"] != 0:
            # Hearts have specific geometric properties
            hu_moments = cv2.HuMoments(moments)
            # Use Hu moments to identify heart-like shapes
            return 0.1 < hu_moments[0] < 0.4 and hu_moments[1] < 0.1
    return False

def is_arrow_shape(contour, aspect_ratio):
    """Detect arrow shapes"""
    # Arrows typically have elongated aspect ratios
    if aspect_ratio > 1.5 or aspect_ratio < 0.67:
        # Check for triangular head and rectangular body
        hull = cv2.convexHull(contour, returnPoints=False)
        defects = cv2.convexityDefects(contour, hull)
        if defects is not None:
            # Arrows have characteristic convexity defects
            return len(defects) >= 2 and len(defects) <= 6
    return False

def is_cross_shape(contour, aspect_ratio, solidity):
    """Detect cross/plus shapes"""
    # Crosses have specific solidity and aspect ratio characteristics
    if 0.7 <= aspect_ratio <= 1.3 and 0.4 <= solidity <= 0.8:
        # Check for the characteristic cross shape using bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        rect_area = w * h
        
        # Cross shapes have specific area to bounding rectangle ratio
        area_ratio = area / rect_area if rect_area > 0 else 0
        return 0.3 <= area_ratio <= 0.7
    return False

# Advanced helper functions for ultra-sophisticated detection

def is_diamond_oriented_advanced(approx):
    """Advanced diamond orientation detection"""
    if len(approx) != 4:
        return False
    
    points = approx.reshape(-1, 2)
    
    # Calculate center
    center_x = np.mean(points[:, 0])
    center_y = np.mean(points[:, 1])
    
    # Calculate angles from center to each vertex
    angles = []
    for point in points:
        angle = math.atan2(point[1] - center_y, point[0] - center_x)
        angles.append(math.degrees(angle))
    
    # Sort angles
    angles.sort()
    
    # Check if vertices are roughly at 45-degree intervals (diamond orientation)
    expected_intervals = [90, 90, 90, 90]
    actual_intervals = []
    
    for i in range(len(angles)):
        interval = (angles[(i + 1) % len(angles)] - angles[i]) % 360
        actual_intervals.append(interval)
    
    # Check if intervals are close to 90 degrees (allowing some tolerance)
    diamond_score = 0
    for actual, expected in zip(actual_intervals, expected_intervals):
        if abs(actual - expected) < 30:  # 30-degree tolerance
            diamond_score += 1
    
    return diamond_score >= 3

def is_parallelogram(approx):
    """Detect parallelogram shapes"""
    if len(approx) != 4:
        return False
    
    points = approx.reshape(-1, 2)
    
    # Calculate side vectors
    sides = []
    for i in range(4):
        side = points[(i + 1) % 4] - points[i]
        sides.append(side)
    
    # Check if opposite sides are parallel
    def are_parallel(v1, v2, tolerance=0.2):
        # Normalize vectors
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)
        
        # Check if cross product is close to zero (parallel) or close to 1 (anti-parallel)
        cross = abs(np.cross(v1_norm, v2_norm))
        return cross < tolerance
    
    parallel_pairs = 0
    if are_parallel(sides[0], sides[2]):
        parallel_pairs += 1
    if are_parallel(sides[1], sides[3]):
        parallel_pairs += 1
    
    return parallel_pairs == 2

def is_rhombus(approx):
    """Detect rhombus shapes (all sides equal)"""
    if len(approx) != 4:
        return False
    
    points = approx.reshape(-1, 2)
    
    # Calculate side lengths
    side_lengths = []
    for i in range(4):
        side = points[(i + 1) % 4] - points[i]
        length = np.linalg.norm(side)
        side_lengths.append(length)
    
    # Check if all sides are approximately equal
    avg_length = np.mean(side_lengths)
    tolerance = avg_length * 0.15  # 15% tolerance
    
    equal_sides = sum(1 for length in side_lengths if abs(length - avg_length) < tolerance)
    return equal_sides >= 3

def is_trapezoid(approx):
    """Detect trapezoid shapes (one pair of parallel sides)"""
    if len(approx) != 4:
        return False
    
    points = approx.reshape(-1, 2)
    
    # Calculate side vectors
    sides = []
    for i in range(4):
        side = points[(i + 1) % 4] - points[i]
        sides.append(side)
    
    # Check for one pair of parallel sides
    def are_parallel(v1, v2, tolerance=0.3):
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)
        cross = abs(np.cross(v1_norm, v2_norm))
        return cross < tolerance
    
    # Check opposite sides
    if are_parallel(sides[0], sides[2]) and not are_parallel(sides[1], sides[3]):
        return True
    if are_parallel(sides[1], sides[3]) and not are_parallel(sides[0], sides[2]):
        return True
    
    return False

def is_star_shape_advanced(contour, approx):
    """Advanced star shape detection using convexity defects"""
    hull = cv2.convexHull(contour, returnPoints=False)
    if len(hull) < 5:
        return False
    
    defects = cv2.convexityDefects(contour, hull)
    if defects is None:
        return False
    
    # Count significant defects (inward points)
    significant_defects = 0
    defect_depths = []
    
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        depth = d / 256.0  # Convert to actual distance
        defect_depths.append(depth)
        
        if depth > 10:  # Significant inward point
            significant_defects += 1
    
    # Stars typically have 5 or more significant defects
    if significant_defects >= 4:
        # Additional check: defects should be relatively uniform
        if len(defect_depths) > 0:
            avg_depth = np.mean(defect_depths)
            depth_variance = np.var(defect_depths)
            
            # Low variance indicates regular star pattern
            if depth_variance < avg_depth * avg_depth:
                return True
    
    return False

def detect_heart_by_moments(hu_moments):
    """Detect heart shapes using Hu moments"""
    if len(hu_moments) < 7:
        return False
    
    # Heart shapes have characteristic Hu moment signatures
    # These values are empirically determined
    heart_signature = [
        (0.15, 0.35),  # hu_moments[0] range
        (0.01, 0.08),  # hu_moments[1] range
        (0.0, 0.05),   # hu_moments[2] range
    ]
    
    matches = 0
    for i, (min_val, max_val) in enumerate(heart_signature):
        if min_val <= abs(hu_moments[i]) <= max_val:
            matches += 1
    
    return matches >= 2

def detect_arrow_by_geometry(contour, aspect_ratio):
    """Detect arrow shapes using geometric analysis"""
    if not (1.5 <= aspect_ratio <= 4.0 or 0.25 <= aspect_ratio <= 0.67):
        return False
    
    # Find the extreme points
    leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
    rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
    topmost = tuple(contour[contour[:, :, 1].argmin()][0])
    bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
    
    # Calculate distances to determine arrow direction
    width = rightmost[0] - leftmost[0]
    height = bottommost[1] - topmost[1]
    
    # Arrow detection based on point distribution
    hull = cv2.convexHull(contour, returnPoints=False)
    defects = cv2.convexityDefects(contour, hull)
    
    if defects is not None:
        # Arrows typically have 2-4 significant defects
        significant_defects = sum(1 for i in range(defects.shape[0]) if defects[i, 0, 3] > 1000)
        return 2 <= significant_defects <= 4
    
    return False

def detect_cross_by_solidity(solidity, aspect_ratio, area):
    """Enhanced cross detection using solidity and geometry"""
    # Cross shapes have characteristic solidity (0.4-0.8) and aspect ratio (0.7-1.3)
    if not (0.4 <= solidity <= 0.8 and 0.7 <= aspect_ratio <= 1.3):
        return False
    
    # Additional area-based validation
    if area < 500:  # Minimum area for reliable cross detection
        return False
    
    return True

def detect_crescent_shape(contour, solidity, aspect_ratio):
    """Detect crescent/moon shapes"""
    # Crescents have low solidity due to their concave nature
    if solidity > 0.85:
        return False
    
    # Crescents typically have elongated aspect ratios
    if not (0.3 <= aspect_ratio <= 0.8 or 1.2 <= aspect_ratio <= 3.0):
        return False
    
    # Check for concavity using convex hull
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    contour_area = cv2.contourArea(contour)
    
    if hull_area > 0:
        concavity_ratio = contour_area / hull_area
        # Crescents have significant concavity
        return concavity_ratio < 0.7
    
    return False

def detect_spiral_shape(contour, hu_moments):
    """Detect spiral shapes using Hu moments and geometric properties"""
    if len(hu_moments) < 7:
        return False
    
    # Spirals have very distinctive Hu moment signatures
    # High values in certain moments indicate spiral-like complexity
    spiral_indicators = [
        abs(hu_moments[2]) > 0.1,  # High third moment
        abs(hu_moments[3]) > 0.05,  # Significant fourth moment
        abs(hu_moments[6]) > 0.01,  # Non-zero seventh moment
    ]
    
    # Need at least 2 indicators for spiral detection
    return sum(spiral_indicators) >= 2

def parse_base64_image(data_url):
    img_str = re.search(r'base64,(.*)', data_url).group(1)
    img_bytes = base64.b64decode(img_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/app")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    data = request.json
    img_data = data.get("image")
    img = parse_base64_image(img_data)
    result = detect_shape(img)
    return jsonify({"shape": result})

if __name__ == "__main__":
    app.run(debug=True)
