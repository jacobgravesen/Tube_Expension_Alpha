import cv2
import numpy as np

def generate_chessboard(rows, cols, square_size):
    """
    Generate a chessboard image.
    
    Parameters:
    - rows: Number of rows in the chessboard
    - cols: Number of columns in the chessboard
    - square_size: Size of each square in pixels
    
    Returns:
    - chessboard: The generated chessboard image
    """
    
    # Initialize an empty array for the chessboard
    chessboard = np.zeros((rows * square_size, cols * square_size), dtype=np.uint8)
    
    # Fill in alternate squares
    for i in range(rows):
        for j in range(cols):
            if (i + j) % 2 == 0:
                chessboard[i * square_size:(i + 1) * square_size, j * square_size:(j + 1) * square_size] = 255
                
    return chessboard

# Generate a 7x6 chessboard with each square of size 50 pixels
rows = 7
cols = 6
square_size = 130
chessboard = generate_chessboard(rows, cols, square_size)

# Save the chessboard image
cv2.imwrite('chessboard.png', chessboard)

# Display the chessboard image
cv2.imshow('Chessboard', chessboard)
cv2.waitKey(0)
cv2.destroyAllWindows()
