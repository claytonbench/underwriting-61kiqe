import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material'; // v5.14.0
import useStyles, { SIGNATURE_CANVAS_WIDTH, SIGNATURE_CANVAS_HEIGHT } from './styles';

/**
 * Props for the SignatureCapture component
 */
interface SignatureCaptureProps {
  /**
   * Callback function called when signature is captured and submitted
   */
  onCapture: (signatureData: string) => void;
  
  /**
   * Callback function called when signature capture is cancelled
   */
  onCancel: () => void;
  
  /**
   * Additional CSS class name for styling
   */
  className?: string;
  
  /**
   * Width of the signature canvas in pixels
   * @default SIGNATURE_CANVAS_WIDTH from styles.ts (400)
   */
  width?: number;
  
  /**
   * Height of the signature canvas in pixels
   * @default SIGNATURE_CANVAS_HEIGHT from styles.ts (200)
   */
  height?: number;
}

/**
 * Internal state interface for drawing functionality
 */
interface DrawingState {
  isDrawing: boolean;
  signatureData: string | null;
  lastX: number;
  lastY: number;
}

/**
 * Component that provides a canvas for capturing electronic signatures
 */
const SignatureCapture: React.FC<SignatureCaptureProps> = ({
  onCapture,
  onCancel,
  className,
  width = SIGNATURE_CANVAS_WIDTH,
  height = SIGNATURE_CANVAS_HEIGHT,
}) => {
  // Canvas and context references
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const contextRef = useRef<CanvasRenderingContext2D | null>(null);
  
  // State for tracking drawing and signature data
  const [state, setState] = useState<DrawingState>({
    isDrawing: false,
    signatureData: null,
    lastX: 0,
    lastY: 0
  });
  
  // Get styled classes
  const classes = useStyles();
  
  // Initialize canvas and context on component mount
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    // Set canvas dimensions with device pixel ratio for better quality
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    
    // Set display size
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    
    // Get and configure canvas context
    const context = canvas.getContext('2d');
    if (!context) return;
    
    // Scale context for device pixel ratio
    context.scale(dpr, dpr);
    
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.strokeStyle = 'black';
    context.lineWidth = 2;
    
    // Store context in ref
    contextRef.current = context;
    
    // Clear canvas initially
    context.clearRect(0, 0, width, height);
  }, [width, height]);
  
  // Helper function to get coordinates from mouse or touch event
  const getCoordinates = (event: MouseEvent | TouchEvent): { x: number, y: number } => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    
    const rect = canvas.getBoundingClientRect();
    
    // Handle both mouse and touch events
    if ('touches' in event) {
      // Touch event
      return {
        x: event.touches[0].clientX - rect.left,
        y: event.touches[0].clientY - rect.top,
      };
    } else {
      // Mouse event
      return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      };
    }
  };
  
  // Start drawing handler
  const handleMouseDown = (event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    
    const { x, y } = getCoordinates(event.nativeEvent);
    const context = contextRef.current;
    
    if (context) {
      context.beginPath();
      context.moveTo(x, y);
      
      setState(prev => ({
        ...prev,
        isDrawing: true,
        lastX: x,
        lastY: y
      }));
    }
  };
  
  // Continue drawing handler
  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    
    if (!state.isDrawing) return;
    
    const { x, y } = getCoordinates(event.nativeEvent);
    const context = contextRef.current;
    
    if (context) {
      // Draw a smooth line from last position to current position
      context.beginPath();
      context.moveTo(state.lastX, state.lastY);
      context.lineTo(x, y);
      context.stroke();
      
      // Update last position
      setState(prev => ({
        ...prev,
        lastX: x,
        lastY: y
      }));
    }
  };
  
  // End drawing handler
  const handleMouseUp = (event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    
    // Store signature data
    const canvas = canvasRef.current;
    if (canvas) {
      const dataUrl = canvas.toDataURL('image/png');
      
      setState(prev => ({
        ...prev,
        isDrawing: false,
        signatureData: dataUrl
      }));
    }
  };
  
  // End drawing when mouse leaves canvas
  const handleMouseLeave = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (state.isDrawing) {
      handleMouseUp(event);
    }
  };
  
  // Clear the canvas
  const handleClear = () => {
    const canvas = canvasRef.current;
    const context = contextRef.current;
    
    if (canvas && context) {
      context.clearRect(0, 0, width, height);
      
      setState(prev => ({
        ...prev,
        signatureData: null
      }));
    }
  };
  
  // Submit the signature
  const handleSubmit = () => {
    if (state.signatureData) {
      onCapture(state.signatureData);
    }
  };
  
  // Handle keyboard interaction for accessibility
  const handleKeyDown = (event: React.KeyboardEvent<HTMLCanvasElement>) => {
    // Space or Enter key to toggle drawing mode
    if (event.key === ' ' || event.key === 'Enter') {
      event.preventDefault();
      setState(prev => ({
        ...prev,
        isDrawing: !prev.isDrawing
      }));
    }
    
    // Escape key to clear canvas
    if (event.key === 'Escape') {
      event.preventDefault();
      handleClear();
    }
  };
  
  return (
    <Box className={`${classes.signatureContainer} ${className || ''}`}>
      <Typography id="signature-instructions" variant="body1" className={classes.instructions}>
        Sign your name in the box below. Use your mouse or finger to draw your signature.
      </Typography>
      
      <Paper elevation={0}>
        <canvas
          ref={canvasRef}
          aria-label="Signature capture area"
          role="img"
          tabIndex={0}
          aria-describedby="signature-instructions"
          className={classes.signatureCanvas}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
          onTouchStart={handleMouseDown}
          onTouchMove={handleMouseMove}
          onTouchEnd={handleMouseUp}
          onKeyDown={handleKeyDown}
        />
      </Paper>
      
      <Box className={classes.buttonGroup}>
        <Button 
          variant="outlined" 
          color="primary" 
          onClick={handleClear}
          aria-label="Clear signature"
        >
          Clear
        </Button>
        <Button 
          variant="outlined" 
          color="secondary" 
          onClick={onCancel}
          aria-label="Cancel signature"
        >
          Cancel
        </Button>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleSubmit}
          disabled={!state.signatureData}
          aria-label="Submit signature"
        >
          Submit Signature
        </Button>
      </Box>
    </Box>
  );
};

export default SignatureCapture;