import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
from IPython import display

def plot_bicharacters(vectorizer, X):
    """Plots the bigram counts in a vectorizer

    Args:
        vectorizer: A CountVectorizer or TfidfVectorizer object 
        X: A sparse matrix of bigram counts
    """    
    # Initialize a dictionary to store the counts
    bigram_counts = {}

    # Get a list of bigram features
    bigrams = vectorizer.get_feature_names_out()

    # Count the occurrences of each bigram
    for bigram in bigrams:
        bigram_counts[bigram] = np.sum(X.toarray()[:, vectorizer.vocabulary_[bigram]])

    # Sort the dictionary alphabetically by bigram
    bigram_counts = dict(sorted(bigram_counts.items()))

    # Step 1: Find unique characters
    chars = sorted(list(set(''.join(bigrams))))

    # Step 2: Create an empty tensor
    matrix = torch.zeros((len(chars), len(chars)), dtype=torch.int)

    # Create a mapping from characters to indices
    char_to_index = {char: index for index, char in enumerate(chars)}

    # Step 3: Fill the tensor
    for bigram, count in bigram_counts.items():
        # Get the row and column indices for the characters in this bigram
        row_index = char_to_index[bigram[0]]
        col_index = char_to_index[bigram[1]]
        
        # Set the corresponding cell in the tensor to the bigram count
        matrix[row_index, col_index] = count

    plt.figure(figsize=(16,16))
    plt.imshow(matrix, cmap='Blues')

    for i in range(30):
        for j in range(30):
            bichar = chars[i] + chars[j]
            plt.text(j, i, bichar, ha="center", va="bottom", color='gray')
            plt.text(j, i, matrix[i, j].item(), ha="center", va="top", color='gray')
    plt.axis('off');


def plot_convolution(image, filt):
    """Plots the convolution operation

    Args:
        image (tensor): A 2D tensor representing the image
        filt (tensor): A 2D tensor representing the filter

    Returns:
        tensor: The result of the convolution operation
    """
    # Result placeholder
    result = np.zeros_like(image)

    # Zero-pad the image
    image_padded = np.pad(image, pad_width=1, mode='constant', constant_values=0)

    # Apply convolution operation
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            # Extract a 3x3 region from the original (padded) image
            region = image_padded[y:y+3, x:x+3]
            
            # Perform the convolution operation (elementwise multiplication and sum)
            result[y, x] = np.sum(region * filt)
            
            # Plot original image, filter, and resulting image at this step
            fig, ax = plt.subplots(1, 4, figsize=(13, 5))
            
            # Original image with rectangle
            ax[0].imshow(image, cmap='gray')
            ax[0].set_title('Original image')
            
            # Add rectangle around the 3x3 region in the original image
            # Adjust rectangle's size and position at the borders of the image
            rect_x = max(x-1, 0)
            rect_y = max(y-1, 0)
            rect_w = min(x+2, image.shape[1]) - rect_x
            rect_h = min(y+2, image.shape[0]) - rect_y
            rect = patches.Rectangle((rect_x-0.5, rect_y-0.5), rect_w, rect_h, linewidth=1, edgecolor='r', facecolor='none')
            ax[0].add_patch(rect)
            
            # For each subplot, show the image and overlay the cell values
            for i, (img, title) in enumerate(zip([region, filt, result], ['Original 3x3 region', 'Filter', 'Result up to this point'])):
                ax[i+1].imshow(img, cmap='gray')
                ax[i+1].set_title(title)
                for (j, k), val in np.ndenumerate(img):
                    ax[i+1].text(k, j, int(val), ha='center', va='center', color='red')
            
            # Show the plot, then clear it for the next step
            plt.show()
            time.sleep(0.25)
            display.clear_output(wait=True)
            plt.close(fig)

    return result
def plot_pooling(results):
    """Plots the max-pooling operation

    Args:
        results (tensor): The result of the convolution operation
    """    
    # Define the size of the pooling window
    pool_size = 2

    # Compute the size of the output of the pooling operation
    pool_output_dim = (results.shape[0] - pool_size + 1, results.shape[1] - pool_size + 1)

    # Initialize the output array
    pool_result = np.zeros(pool_output_dim)

    for x in range(0, pool_output_dim[1]):
        for y in range(0, pool_output_dim[0]):
            # Compute the coordinates of the top-left corner of the pooling window
            x_start, y_start = x, y
            # Extract a pool_size x pool_size region from the convolution result
            region = results[y_start:y_start+pool_size, x_start:x_start+pool_size]
            
            # Perform the max-pooling operation (maximum value in the region)
            max_value = np.max(region)
            pool_result[y, x] = max_value

            # Plot the resulting pooled image
            fig, ax = plt.subplots(1, 3, figsize=(10, 5))

            # Original convolution result with rectangle
            ax[0].imshow(results, cmap='gray')
            ax[0].set_title('Convolution result')
            rectangle = plt.Rectangle((x_start, y_start), pool_size, pool_size, fill=False, color='red')
            ax[0].add_patch(rectangle)
            for i in range(results.shape[0]):
                for j in range(results.shape[1]):
                    ax[0].text(j, i, str(results[i, j]), ha='center', va='center', color='r')

            # Max-pooling operation
            ax[1].imshow(region, cmap='gray')
            ax[1].set_title('Max-pooling operation')
            ax[1].text(0.5, 0.5, str(max_value), fontsize=12, ha='center')

            # Result up to this point
            ax[2].imshow(pool_result, cmap='gray')
            ax[2].set_title('Result after Max-Pooling')
            for i in range(pool_result.shape[0]):
                for j in range(pool_result.shape[1]):
                    ax[2].text(j, i, str(pool_result[i, j]), ha='center', va='center', color='r')

            plt.show()
            time.sleep(0.25)
            display.clear_output(wait=True)
            plt.close(fig)
