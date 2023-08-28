"""
Functions and variables to help with time series analysis.
"""
from typing import Union
import numpy as np

def fahrenheit_to_celcius(temp_f: Union[float, int]) -> Union[float, int]:
    """
    Convert temperature in Fahrenheit to Celcius.
    
    Args:
        temp_f: Temperature in Fahrenheit.
    
    Returns:
        Temperature in Celcius.
    """
    if isinstance(temp_f, float):
        temp_f = temp_f*100
    
    return (temp_f - 32) * 5/9

def root_mean_squared_error(predictions, targets) -> float:
    """Calculate the root mean squared error 
    between predictions and targets.

    Args:
        predictions: Predictions 
        targets: Targets

    Returns:
        Calculated root mean squared error.
    """
    return np.sqrt(((predictions - targets) ** 2).mean())

def percent_change(new_number: Union[float, int], old_number: Union[float, int]) -> float:
    """Calculate the percent change between two numbers.

    Args:
        new_number (Union[float, int]): The new number.
        old_number (Union[float, int]): The old number.

    Returns:
        float: The percent change between the two numbers.
    """
    return round((new_number - old_number) / abs(old_number) * 100, 2)
