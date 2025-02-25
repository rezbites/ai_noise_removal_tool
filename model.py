import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D
from tensorflow.keras.models import Model

class NoiseRemovalModel:
    def __init__(self, model_path=None):
        """
        Initialize the noise removal model.
        
        Args:
            model_path: Path to pre-trained model weights (optional)
        """
        self.model_loaded = False
        
        if model_path:
            try:
                # Load a pre-trained Denoising Autoencoder
                self.model = self._build_autoencoder()
                self.model.load_weights(model_path)
                self.model_loaded = True
                print(f"Model loaded from {model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model_loaded = False
        else:
            # Build a new model if no path is provided
            self.model = self._build_autoencoder()
            print("New model initialized (not trained)")
    
    def _build_autoencoder(self):
        """
        Build a Denoising Autoencoder model.
        
        Returns:
            A TensorFlow/Keras model
        """
        # Input layer
        input_img = Input(shape=(256, 256, 3))  # Adjust input size as needed
        
        # Encoder
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(input_img)
        x = MaxPooling2D((2, 2), padding='same')(x)
        x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        x = MaxPooling2D((2, 2), padding='same')(x)
        x = Conv2D(256, (3, 3), activation='relu', padding='same')(x)
        encoded = MaxPooling2D((2, 2), padding='same')(x)
        
        # Decoder
        x = Conv2D(256, (3, 3), activation='relu', padding='same')(encoded)
        x = UpSampling2D((2, 2))(x)
        x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D((2, 2))(x)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D((2, 2))(x)
        decoded = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)
        
        # Autoencoder model
        autoencoder = Model(input_img, decoded)
        autoencoder.compile(optimizer='adam', loss='mse')  # Mean Squared Error loss
        return autoencoder
    
    def remove_noise(self, image):
        """
        Remove noise from the image using the Denoising Autoencoder.
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Denoised image (numpy array)
        """
        if not self.model_loaded:
            print("Model not loaded. Using traditional denoising as fallback.")
            return self._traditional_denoising(image)
        
        # Preprocess the image
        resized_image = cv2.resize(image, (256, 256))  # Resize to model input size
        normalized_image = resized_image / 255.0  # Normalize to [0, 1]
        input_image = np.expand_dims(normalized_image, axis=0)  # Add batch dimension
        
        # Predict the denoised image
        denoised_image = self.model.predict(input_image)
        
        # Postprocess the image
        denoised_image = np.squeeze(denoised_image, axis=0)  # Remove batch dimension
        denoised_image = (denoised_image * 255).astype(np.uint8)  # Scale back to [0, 255]
        denoised_image = cv2.resize(denoised_image, (image.shape[1], image.shape[0]))  # Resize to original size
        
        return denoised_image
    
    def remove_background_noise(self, image):
        """
        Remove noise from the background while preserving the foreground.
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Image with background noise removed (numpy array)
        """
        # Step 1: Segment foreground and background
        mask = self._segment_foreground(image)
        
        # Step 2: Denoise the entire image
        denoised_image = self.remove_noise(image)
        
        # Step 3: Blend original foreground with denoised background
        result = image.copy()
        background_mask = 1 - mask
        
        # Expand dimensions for mask if needed
        if len(mask.shape) == 2 and len(image.shape) == 3:
            mask = np.expand_dims(mask, axis=2)
            background_mask = np.expand_dims(background_mask, axis=2)
        
        # Blend images using the mask
        result = (image * mask + denoised_image * background_mask).astype(np.uint8)
        
        return result
    
    def _traditional_denoising(self, image):
        """
        Apply traditional computer vision methods for noise removal.
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Denoised image (numpy array)
        """
        if len(image.shape) == 3:  # Color image
            denoised = cv2.fastNlMeansDenoisingColored(image, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21)
        else:  # Grayscale image
            denoised = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
        return denoised
    
    def _segment_foreground(self, image):
        """
        Segment the foreground from the background.
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Binary mask where 1 represents foreground and 0 represents background
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Otsu's thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Normalize mask to range [0, 1]
        mask = thresh / 255.0
        
        return mask
