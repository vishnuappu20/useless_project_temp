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

def advanced_preprocessing(gray):
    """Multi-stage preprocessing for optimal shape detection"""
    # Stage 1: Noise reduction with bilateral filter
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Stage 2: Adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Stage 3: Multi-scale Gaussian blur
    blur1 = cv2.GaussianBlur(enhanced, (3, 3), 0)
    blur2 = cv2.GaussianBlur(enhanced, (7, 7), 0)
    combined_blur = cv2.addWeighted(blur1, 0.7, blur2, 0.3, 0)
    
    # Stage 4: Advanced thresholding with multiple methods
    # Otsu's thresholding
    _, thresh_otsu = cv2.threshold(combined_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Adaptive thresholding
    thresh_adaptive = cv2.adaptiveThreshold(combined_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Combine thresholding methods
    thresh_combined = cv2.bitwise_or(thresh_otsu, thresh_adaptive)
    
    # Stage 5: Advanced morphological operations
    # Multiple kernel sizes for different shape scales
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_medium = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Close small gaps
    closed = cv2.morphologyEx(thresh_combined, cv2.MORPH_CLOSE, kernel_small)
    # Remove small noise
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_small)
    # Fill holes
    filled = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_medium)
    
    return filled

def detect_shapes_by_contours(preprocessed):
    """Advanced contour-based shape detection"""
    contours, _ = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    shapes = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 300:  # Reduced threshold for better sensitivity
            continue
        
        # Enhanced geometric analysis
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
            
        # Multiple approximation levels for better accuracy
        approx_loose = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
        approx_tight = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        approx_very_tight = cv2.approxPolyDP(cnt, 0.01 * perimeter, True)
        
        # Comprehensive geometric properties
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h
        
        # Advanced shape metrics
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        # Circularity and compactness
        circularity = 4 * math.pi * area / (perimeter * perimeter)
        compactness = perimeter * perimeter / area
        
        # Moments for advanced analysis
        moments = cv2.moments(cnt)
        if moments["m00"] != 0:
            hu_moments = cv2.HuMoments(moments)
        else:
            hu_moments = np.zeros(7)
        
        # Classify shape with multiple criteria
        shape_result = classify_ultra_advanced_shape(
            approx_loose, approx_tight, approx_very_tight,
            aspect_ratio, circularity, solidity, compactness,
            area, cnt, hu_moments
        )
        
        if shape_result:
            shapes.append(shape_result)
    
    return shapes

def detect_shapes_by_hough_transforms(preprocessed):
    """Hough transform-based detection for circles and lines"""
    shapes = []
    
    # Hough Circle Transform for perfect circle detection
    circles = cv2.HoughCircles(
        preprocessed, cv2.HOUGH_GRADIENT, dp=1, minDist=30,
        param1=50, param2=30, minRadius=10, maxRadius=200
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            shapes.append({
                'name': 'Circle',
                'confidence': 0.95,
                'center': (x, y),
                'radius': r,
                'method': 'hough'
            })
    
    # Hough Line Transform for detecting straight edges
    edges = cv2.Canny(preprocessed, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
    
    if lines is not None and len(lines) >= 3:
        # Analyze line patterns for polygon detection
        line_angles = []
        for line in lines:
            rho, theta = line[0]
            angle = theta * 180 / np.pi
            line_angles.append(angle)
        
        # Detect regular polygons based on line patterns
        polygon_shape = analyze_line_patterns(line_angles)
        if polygon_shape:
            shapes.append(polygon_shape)
    
    return shapes

def detect_shapes_by_template_matching(preprocessed):
    """Template matching for specific shape patterns"""
    shapes = []
    
    # Create templates for common shapes
    templates = create_shape_templates()
    
    for template_name, template in templates.items():
        # Multi-scale template matching
        for scale in [0.5, 0.7, 1.0, 1.3, 1.5]:
            scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
            
            if scaled_template.shape[0] > preprocessed.shape[0] or scaled_template.shape[1] > preprocessed.shape[1]:
                continue
            
            result = cv2.matchTemplate(preprocessed, scaled_template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.7)
            
            for pt in zip(*locations[::-1]):
                shapes.append({
                    'name': template_name,
                    'confidence': float(result[pt[1], pt[0]]),
                    'location': pt,
                    'scale': scale,
                    'method': 'template'
                })
    
    return shapes

def create_shape_templates():
    """Create template images for common shapes"""
    templates = {}
    
    # Star template
    star_template = np.zeros((60, 60), dtype=np.uint8)
    star_points = np.array([
        [30, 5], [35, 20], [50, 20], [40, 30], [45, 45],
        [30, 35], [15, 45], [20, 30], [10, 20], [25, 20]
    ], np.int32)
    cv2.fillPoly(star_template, [star_points], 255)
    templates['Star'] = star_template
    
    # Heart template
    heart_template = np.zeros((60, 60), dtype=np.uint8)
    cv2.circle(heart_template, (20, 20), 12, 255, -1)
    cv2.circle(heart_template, (40, 20), 12, 255, -1)
    heart_bottom = np.array([[30, 50], [15, 30], [45, 30]], np.int32)
    cv2.fillPoly(heart_template, [heart_bottom], 255)
    templates['Heart'] = heart_template
    
    # Arrow template
    arrow_template = np.zeros((60, 60), dtype=np.uint8)
    arrow_points = np.array([
        [10, 25], [35, 25], [35, 15], [50, 30], [35, 45], [35, 35], [10, 35]
    ], np.int32)
    cv2.fillPoly(arrow_template, [arrow_points], 255)
    templates['Arrow'] = arrow_template
    
    return templates

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

def validate_and_cluster_shapes(all_shapes, preprocessed):
    """Advanced shape validation and clustering to remove duplicates"""
    if not all_shapes:
        return []
    
    # Convert shapes to consistent format
    validated_shapes = []
    
    for shape in all_shapes:
        if isinstance(shape, dict):
            validated_shapes.append(shape)
        else:
            # Convert old format to new format
            validated_shapes.append({
                'name': shape,
                'confidence': 0.8,
                'method': 'contour'
            })
    
    # Remove duplicates and low-confidence detections
    filtered_shapes = []
    for shape in validated_shapes:
        if shape['confidence'] >= 0.5:  # Minimum confidence threshold
            filtered_shapes.append(shape)
    
    # Group similar shapes and keep the highest confidence
    final_shapes = []
    shape_groups = {}
    
    for shape in filtered_shapes:
        shape_name = shape['name']
        if shape_name not in shape_groups:
            shape_groups[shape_name] = []
        shape_groups[shape_name].append(shape)
    
    # Keep best detection for each shape type
    for shape_name, group in shape_groups.items():
        best_shape = max(group, key=lambda x: x['confidence'])
        final_shapes.append(best_shape)
    
    return final_shapes

def analyze_line_patterns(line_angles):
    """Analyze line patterns to detect regular polygons"""
    if len(line_angles) < 3:
        return None
    
    # Normalize angles to 0-180 range
    normalized_angles = [angle % 180 for angle in line_angles]
    
    # Count angle frequencies
    angle_counts = Counter([round(angle / 10) * 10 for angle in normalized_angles])
    
    # Detect patterns
    if len(angle_counts) == 2:  # Two dominant angles
        angles = list(angle_counts.keys())
        diff = abs(angles[0] - angles[1])
        if 85 <= diff <= 95:  # Perpendicular lines
            return {
                'name': 'Rectangle',
                'confidence': 0.85,
                'method': 'hough_lines'
            }
    elif len(angle_counts) == 3:  # Three angles - triangle
        return {
            'name': 'Triangle',
            'confidence': 0.8,
            'method': 'hough_lines'
        }
    
    return None

def classify_ultra_advanced_shape(approx_loose, approx_tight, approx_very_tight, 
                                 aspect_ratio, circularity, solidity, compactness,
                                 area, contour, hu_moments):
    """Ultra-advanced shape classification with multiple criteria"""
    
    # Use different approximation levels for different analyses
    vertices_loose = len(approx_loose)
    vertices_tight = len(approx_tight)
    vertices_very_tight = len(approx_very_tight)
    
    # Calculate confidence based on multiple factors
    base_confidence = 0.7
    
    # High circularity indicates circular shapes
    if circularity > 0.75:
        if 0.85 <= aspect_ratio <= 1.15:
            confidence = min(0.95, base_confidence + circularity * 0.3)
            return {
                'name': 'Circle',
                'confidence': confidence,
                'method': 'contour_advanced'
            }
        else:
            confidence = min(0.9, base_confidence + circularity * 0.2)
            return {
                'name': 'Ellipse',
                'confidence': confidence,
                'method': 'contour_advanced'
            }
    
    # Polygon classification based on vertices
    primary_vertices = vertices_tight
    
    if primary_vertices == 3:
        # Triangle analysis
        confidence = base_confidence + (solidity * 0.2)
        return {
            'name': 'Triangle',
            'confidence': min(0.95, confidence),
            'method': 'contour_advanced'
        }
    
    elif primary_vertices == 4:
        # Quadrilateral analysis
        if 0.95 <= aspect_ratio <= 1.05:
            # Square vs Diamond detection
            if is_diamond_oriented_advanced(approx_tight):
                return {
                    'name': 'Diamond',
                    'confidence': base_confidence + 0.1,
                    'method': 'contour_advanced'
                }
            else:
                return {
                    'name': 'Square',
                    'confidence': base_confidence + 0.15,
                    'method': 'contour_advanced'
                }
        elif 0.4 <= aspect_ratio <= 0.6 or 1.6 <= aspect_ratio <= 2.5:
            # Rectangle detection
            return {
                'name': 'Rectangle',
                'confidence': base_confidence + 0.1,
                'method': 'contour_advanced'
            }
        else:
            # Other quadrilaterals
            if is_parallelogram(approx_tight):
                if is_rhombus(approx_tight):
                    return {
                        'name': 'Rhombus',
                        'confidence': base_confidence,
                        'method': 'contour_advanced'
                    }
                else:
                    return {
                        'name': 'Parallelogram',
                        'confidence': base_confidence,
                        'method': 'contour_advanced'
                    }
            elif is_trapezoid(approx_tight):
                return {
                    'name': 'Trapezoid',
                    'confidence': base_confidence,
                    'method': 'contour_advanced'
                }
    
    elif primary_vertices == 5:
        return {
            'name': 'Pentagon',
            'confidence': base_confidence + 0.1,
            'method': 'contour_advanced'
        }
    
    elif primary_vertices == 6:
        return {
            'name': 'Hexagon',
            'confidence': base_confidence + 0.1,
            'method': 'contour_advanced'
        }
    
    elif primary_vertices == 8:
        return {
            'name': 'Octagon',
            'confidence': base_confidence + 0.1,
            'method': 'contour_advanced'
        }
    
    elif primary_vertices > 8:
        # Complex shapes
        if is_star_shape_advanced(contour, approx_loose):
            return {
                'name': 'Star',
                'confidence': base_confidence,
                'method': 'contour_advanced'
            }
        elif circularity > 0.5:
            return {
                'name': 'Circle',
                'confidence': base_confidence - 0.1,
                'method': 'contour_advanced'
            }
    
    # Special shape detection using Hu moments
    if detect_heart_by_moments(hu_moments):
        return {
            'name': 'Heart',
            'confidence': base_confidence,
            'method': 'contour_advanced'
        }
    
    if detect_arrow_by_geometry(contour, aspect_ratio):
        return {
            'name': 'Arrow',
            'confidence': base_confidence,
            'method': 'contour_advanced'
        }
    
    if detect_cross_by_solidity(solidity, aspect_ratio, area):
        return {
            'name': 'Cross',
            'confidence': base_confidence,
            'method': 'contour_advanced'
        }
    
    if detect_crescent_shape(contour, solidity, aspect_ratio):
        return {
            'name': 'Crescent',
            'confidence': base_confidence,
            'method': 'contour_advanced'
        }
    
    if detect_spiral_shape(contour, hu_moments):
        return {
            'name': 'Spiral',
            'confidence': base_confidence,
            'method': 'contour_advanced'
        }
    
    return None

def classify_advanced_shape(approx, aspect_ratio, circularity, solidity, area, contour):
    """Advanced shape classification using multiple geometric features"""
    vertices = len(approx)
    
    # Circle detection (high circularity)
    if circularity > 0.7:
        if 0.85 <= aspect_ratio <= 1.15:
            return "Circle"
        else:
            return "Ellipse"
    
    # Polygon detection based on vertices
    if vertices == 3:
        return "Triangle"
    elif vertices == 4:
        # Distinguish between square, rectangle, and diamond
        if 0.95 <= aspect_ratio <= 1.05:
            # Check if it's rotated (diamond)
            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                # Check orientation
                if is_diamond_oriented(approx):
                    return "Diamond"
                else:
                    return "Square"
            return "Square"
        else:
            return "Rectangle"
    elif vertices == 5:
        return "Pentagon"
    elif vertices == 6:
        return "Hexagon"
    elif vertices == 8:
        return "Octagon"
    elif vertices > 8:
        # Could be a star or highly complex polygon
        if is_star_shape(contour, approx):
            return "Star"
        elif circularity > 0.5:
            return "Circle"  # Likely a circle with many approximation points
        else:
            return "Unknown"
    else:
        # Special shape detection for complex forms
        if is_heart_shape(contour, aspect_ratio):
            return "Heart"
        elif is_arrow_shape(contour, aspect_ratio):
            return "Arrow"
        elif is_cross_shape(contour, aspect_ratio, solidity):
            return "Cross"
        else:
            return "Unknown"

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
