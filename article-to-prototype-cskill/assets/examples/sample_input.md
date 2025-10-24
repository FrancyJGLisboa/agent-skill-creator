# Quick Sort Algorithm

## Overview

Quick Sort is an efficient, divide-and-conquer sorting algorithm. It works by selecting a 'pivot' element and partitioning the array around it.

## Algorithm

The Quick Sort algorithm follows these steps:

1. Choose a pivot element from the array
2. Partition the array so that:
   - Elements less than pivot are on the left
   - Elements greater than pivot are on the right
3. Recursively apply the same process to sub-arrays

## Complexity

- **Time Complexity**: O(n log n) average case, O(n²) worst case
- **Space Complexity**: O(log n) for recursion stack

## Implementation Outline

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)
```

## Usage

Quick Sort is widely used for:
- General-purpose sorting
- In-place sorting when memory is limited
- Systems where average-case performance matters

## References

Hoare, C. A. R. (1962). "Quicksort". The Computer Journal.
