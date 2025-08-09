class ShapeDetectorApp {
  constructor() {
    this.canvas = document.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.drawing = false;
    this.drawingHistory = [];
    this.currentPath = [];
    
    // UI elements
    this.detectBtn = document.getElementById("detectBtn");
    this.clearBtn = document.getElementById("clearBtn");
    this.undoBtn = document.getElementById("undoBtn");
    this.result = document.getElementById("result");
    this.canvasOverlay = document.getElementById("canvasOverlay");
    this.toast = document.getElementById("toast");
    this.toastMessage = document.getElementById("toastMessage");
    this.particlesContainer = document.getElementById("particlesContainer");
    this.confettiContainer = document.getElementById("confettiContainer");
    
    this.init();
  }
  
  init() {
    this.setupCanvas();
    this.setupEventListeners();
    this.saveCanvasState();
  }
  
  setupCanvas() {
    this.ctx.fillStyle = "white";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.strokeStyle = "#1f2937";
    this.ctx.lineWidth = 4;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
  }
  
  setupEventListeners() {
    // Mouse events
    this.canvas.addEventListener("mousedown", (e) => this.startDrawing(e));
    this.canvas.addEventListener("mousemove", (e) => this.draw(e));
    this.canvas.addEventListener("mouseup", () => this.stopDrawing());
    this.canvas.addEventListener("mouseout", () => this.stopDrawing());
    
    // Touch events for mobile support
    this.canvas.addEventListener("touchstart", (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      const rect = this.canvas.getBoundingClientRect();
      const mouseEvent = new MouseEvent("mousedown", {
        clientX: touch.clientX,
        clientY: touch.clientY
      });
      this.canvas.dispatchEvent(mouseEvent);
    });
    
    this.canvas.addEventListener("touchmove", (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      const rect = this.canvas.getBoundingClientRect();
      const mouseEvent = new MouseEvent("mousemove", {
        clientX: touch.clientX,
        clientY: touch.clientY
      });
      this.canvas.dispatchEvent(mouseEvent);
    });
    
    this.canvas.addEventListener("touchend", (e) => {
      e.preventDefault();
      const mouseEvent = new MouseEvent("mouseup", {});
      this.canvas.dispatchEvent(mouseEvent);
    });
    
    // Button events
    this.detectBtn.addEventListener("click", () => this.detectShape());
    this.clearBtn.addEventListener("click", () => this.clearCanvas());
    this.undoBtn.addEventListener("click", () => this.undoLastAction());
  }
  
  getCoordinates(e) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    };
  }
  
  startDrawing(e) {
    this.drawing = true;
    this.canvas.classList.add("drawing");
    this.hideCanvasOverlay();
    
    const coords = this.getCoordinates(e);
    this.ctx.beginPath();
    this.ctx.moveTo(coords.x, coords.y);
    this.currentPath = [{ x: coords.x, y: coords.y, type: 'move' }];
  }
  
  draw(e) {
    if (!this.drawing) return;
    
    const coords = this.getCoordinates(e);
    this.ctx.lineTo(coords.x, coords.y);
    this.ctx.stroke();
    this.currentPath.push({ x: coords.x, y: coords.y, type: 'line' });
  }
  
  stopDrawing() {
    if (!this.drawing) return;
    
    this.drawing = false;
    this.canvas.classList.remove("drawing");
    
    if (this.currentPath.length > 1) {
      this.saveCanvasState();
      this.updateUndoButton();
    }
    
    this.currentPath = [];
  }
  
  saveCanvasState() {
    const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    this.drawingHistory.push(imageData);
    
    // Limit history to prevent memory issues
    if (this.drawingHistory.length > 10) {
      this.drawingHistory.shift();
    }
  }
  
  updateUndoButton() {
    this.undoBtn.disabled = this.drawingHistory.length <= 1;
  }
  
  undoLastAction() {
    if (this.drawingHistory.length <= 1) return;
    
    this.drawingHistory.pop(); // Remove current state
    const previousState = this.drawingHistory[this.drawingHistory.length - 1];
    
    this.ctx.putImageData(previousState, 0, 0);
    this.updateUndoButton();
    this.clearResult();
    
    this.showToast("Last action undone", "success");
  }
  
  clearCanvas() {
    this.ctx.fillStyle = "white";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawingHistory = [];
    this.saveCanvasState();
    this.updateUndoButton();
    this.clearResult();
    this.showCanvasOverlay();
    
    this.showToast("Canvas cleared", "success");
  }
  
  async detectShape() {
    // Check if canvas is blank
    if (this.isCanvasBlank()) {
      this.showResult("Please draw something first! ", "error");
      return;
    }
    
    this.setLoadingState(true);
    
    try {
      const dataUrl = this.canvas.toDataURL("image/png");
      const response = await fetch("/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      this.showResult(data.shape, "success");
      
    } catch (error) {
      console.error("Detection error:", error);
      this.showResult("Oops! Something went wrong. Please try again.", "error");
      this.showToast("Detection failed. Please try again.", "error");
    } finally {
      this.setLoadingState(false);
    }
  }
  
  isCanvasBlank() {
    const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    const data = imageData.data;
    
    // Check if all pixels are white (255, 255, 255, 255)
    for (let i = 0; i < data.length; i += 4) {
      if (data[i] !== 255 || data[i + 1] !== 255 || data[i + 2] !== 255) {
        return false;
      }
    }
    return true;
  }
  
  setLoadingState(loading) {
    if (loading) {
      this.detectBtn.classList.add("btn-loading");
      this.detectBtn.querySelector(".spinner").style.display = "block";
      this.detectBtn.disabled = true;
    } else {
      this.detectBtn.classList.remove("btn-loading");
      this.detectBtn.querySelector(".spinner").style.display = "none";
      this.detectBtn.disabled = false;
    }
  }
  
  showResult(text, type = "success") {
    this.result.innerHTML = `
      <div class="result-icon">
        <i class="fas ${type === 'success' ? 'fa-magic' : 'fa-exclamation-triangle'}"></i>
      </div>
      <div class="result-text">${text}</div>
    `;
    
    this.result.className = type;
    
    // Add entrance animation
    this.result.style.transform = "translateY(20px)";
    this.result.style.opacity = "0";
    
    requestAnimationFrame(() => {
      this.result.style.transition = "all 0.3s ease";
      this.result.style.transform = "translateY(0)";
      this.result.style.opacity = "1";
      
      // Trigger animated feedback for successful shape detection
      if (type === 'success' && text && !text.includes('No shapes detected')) {
        setTimeout(() => {
          this.triggerAnimatedFeedback(text);
        }, 300);
      }
    });
  }
  
  clearResult() {
    this.result.innerHTML = "";
    this.result.className = "";
  }
  
  showToast(message, isError = false) {
    this.toastMessage.textContent = message;
    this.toast.className = `toast ${isError ? 'error' : ''} show`;
    
    setTimeout(() => {
      this.toast.classList.remove('show');
    }, 3000);
  }
  
  hideCanvasOverlay() {
    this.canvasOverlay.classList.add("hidden");
  }
  
  showCanvasOverlay() {
    this.canvasOverlay.classList.remove("hidden");
  }

  // Animated Feedback Functions
  createParticles(x, y, color = '#4ecdc4') {
    const particleCount = 15;
    
    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      
      // Random size and color variations
      const size = Math.random() * 8 + 4;
      const colors = ['#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff6b6b'];
      const particleColor = colors[Math.floor(Math.random() * colors.length)];
      
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      particle.style.backgroundColor = particleColor;
      particle.style.left = `${x + (Math.random() - 0.5) * 100}px`;
      particle.style.top = `${y + (Math.random() - 0.5) * 100}px`;
      
      // Random animation duration and delay
      particle.style.animationDuration = `${1.5 + Math.random()}s`;
      particle.style.animationDelay = `${Math.random() * 0.3}s`;
      
      this.particlesContainer.appendChild(particle);
      
      // Remove particle after animation
      setTimeout(() => {
        if (particle.parentNode) {
          particle.parentNode.removeChild(particle);
        }
      }, 2500);
    }
  }

  createConfetti() {
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti';
      
      // Random position across the top of the screen
      confetti.style.left = `${Math.random() * 100}%`;
      confetti.style.top = '-10px';
      
      // Random animation duration and delay
      confetti.style.animationDuration = `${2 + Math.random() * 2}s`;
      confetti.style.animationDelay = `${Math.random() * 0.5}s`;
      
      this.confettiContainer.appendChild(confetti);
      
      // Remove confetti after animation
      setTimeout(() => {
        if (confetti.parentNode) {
          confetti.parentNode.removeChild(confetti);
        }
      }, 4000);
    }
  }

  createShapeOutline(shapeName) {
    const canvasRect = this.canvas.getBoundingClientRect();
    const outline = document.createElement('div');
    outline.className = `shape-outline ${shapeName.toLowerCase()}`;
    
    // Position the outline over the canvas center
    const centerX = canvasRect.width / 2;
    const centerY = canvasRect.height / 2;
    
    if (shapeName.toLowerCase() === 'circle') {
      const size = 100;
      outline.style.width = `${size}px`;
      outline.style.height = `${size}px`;
      outline.style.left = `${centerX - size/2}px`;
      outline.style.top = `${centerY - size/2}px`;
    } else if (shapeName.toLowerCase() === 'square') {
      const size = 100;
      outline.style.width = `${size}px`;
      outline.style.height = `${size}px`;
      outline.style.left = `${centerX - size/2}px`;
      outline.style.top = `${centerY - size/2}px`;
    } else if (shapeName.toLowerCase() === 'rectangle') {
      outline.style.width = '120px';
      outline.style.height = '80px';
      outline.style.left = `${centerX - 60}px`;
      outline.style.top = `${centerY - 40}px`;
    } else if (shapeName.toLowerCase() === 'triangle') {
      outline.style.left = `${centerX - 50}px`;
      outline.style.top = `${centerY - 43}px`;
    } else if (shapeName.toLowerCase() === 'heart') {
      outline.style.width = '52px';
      outline.style.height = '45px';
      outline.style.left = `${centerX - 26}px`;
      outline.style.top = `${centerY - 22}px`;
    }
    
    this.particlesContainer.appendChild(outline);
    
    // Remove outline after animation
    setTimeout(() => {
      if (outline.parentNode) {
        outline.parentNode.removeChild(outline);
      }
    }, 2000);
  }

  triggerSuccessPulse() {
    this.result.classList.add('success-pulse');
    setTimeout(() => {
      this.result.classList.remove('success-pulse');
    }, 600);
  }

  triggerAnimatedFeedback(result) {
    // Extract shape name from result
    const shapeName = result.split(' ')[0];
    const canvasRect = this.canvas.getBoundingClientRect();
    const centerX = canvasRect.width / 2;
    const centerY = canvasRect.height / 2;
    
    // Always create particles for any detection
    this.createParticles(centerX, centerY);
    
    // Create shape outline animation
    if (['Square', 'Rectangle', 'Circle', 'Triangle', 'Heart'].includes(shapeName)) {
      this.createShapeOutline(shapeName);
    }
    
    // Trigger confetti for high-confidence detections (🎯 emoji indicates high confidence)
    if (result.includes('🎯')) {
      setTimeout(() => {
        this.createConfetti();
      }, 300);
    }
    
    // Success pulse for the result container
    this.triggerSuccessPulse();
  }
}

// Initialize the app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new ShapeDetectorApp();
});
