# -*- coding: utf-8 -*-


# This file defines functions used for getting the data.


# Import the math module for rounding numbers.
import math
# Import the collections module for getting the mode of a list of numbers.
import collections


def mean(numbers):
    """Finds the mean of a list of numbers."""
    
    # Add the numbers
    total = 0
    for i in numbers:
        total += i
    
    # Divide by the length of the list.
    return total / len(numbers)


def median(numbers2):
    """Finds the median of a list of numbers."""
    
    # Make a copy of the data. The original list should be unmodified.
    numbers = numbers2[:]
    
    # Sort the list.
    numbers.sort()
    
    # If the list has an odd number of items:
    if len(numbers) % 2:
        return numbers[int(math.floor(len(numbers) / 2))];
    
    # If the list has an even number of items:
    else:
        return (numbers[len(numbers) / 2] + numbers[(len(numbers) / 2) - 1]) / 2;


def range(numbers):
    """Finds the range of a list of numbers."""
    
    # Calculate the range.
    return max(numbers) - min(numbers)


def mode(numbers):
    """Finds the mode of a list of numbers."""
    
    # Put the numbers in a collection.
    collect = collections.Counter(numbers)
    
    # Get the mode of the numbers.
    return collect.most_common(1)[0][0]