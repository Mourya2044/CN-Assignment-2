'''
injecterror.py
This module provides functions to simulate bit errors in binary strings, useful for testing error detection and correction mechanisms in computer networks.
Functions:
    injecterror(data: str, errcnt: int = 1) -> str
    injectbursterror(data: str, burstsize: int = 1) -> str
    injectodderror(data: str) -> str
    undetectable_error(data: str, poly: str, shift: int = 0) -> str
        Flips bits in `data` according to the generator polynomial (`poly`), shifted by `shift`, to produce an undetectable error.
'''
import random

def injecterror(data: str, errcnt:int = 1) -> str:
    """
    Introduces bit errors into a binary string by flipping random bits.

    Args:
        data (str): The binary string to inject errors into (composed of '0's and '1's).
        errcnt (int, optional): The number of bits to flip. Defaults to 1.

    Returns:
        str: The binary string after injecting the specified number of bit errors.

    Note:
        Each bit flip is performed at a random position. Multiple flips may affect the same position.
    """
    n = len(data)
    data_list = list(data)
    for _ in range(errcnt):
        index = random.randint(0, n-1)
        if data_list[index] == '1':
            data_list[index] = '0'
        else:
            data_list[index] = '1'
    return ''.join(data_list)

def injectbursterror(data: str, burstsize: int = 1) -> str:
    """
    Introduces a burst error into a binary string by flipping bits within a randomly chosen segment.

    Args:
        data (str): The input binary string (composed of '0's and '1's).
        burstsize (int, optional): The number of consecutive bits to consider for error injection. Defaults to 1.

    Returns:
        str: The binary string after burst error injection.

    Notes:
        - Each bit in the burst segment has a 40% chance of being flipped.
        - The burst segment is chosen randomly within the bounds of the input string.
    """
    n = len(data)
    index = random.randint(0, n-burstsize)
    data_list = list(data)
    for i in range(index, index+burstsize):
        if random.random() < 0.4:
            if data_list[i] == '1':
                data_list[i] = '0'
            else:
                data_list[i] = '1'
    return ''.join(data_list)

def injectodderror(data: str) -> str:
    """
    Introduces random bit errors into the input binary string by flipping an odd number of bits.
    Args:
        data (str): A binary string consisting of '0's and '1's.
    Returns:
        str: The binary string after flipping an odd number of bits at random positions.
    Note:
        - The number of bits flipped is randomly chosen to be an odd number between 1 and the length of the input string.
        - Each flipped bit is selected randomly and independently.
    """
    n = len(data)
    data_list = list(data)
    flip_count = random.choice([i for i in range(1, n, 2)])  
    indices = random.sample(range(n), flip_count)
    
    for idx in indices:
        data_list[idx] = '0' if data_list[idx] == '1' else '1'
    
    return ''.join(data_list)

def undetectable_error(data: str, poly: str, shift: int = 0) -> str:
    """
    Flip bits in `data` according to the generator polynomial (poly),
    shifted by `shift`, to produce an undetectable error.

    Args:
        data (str): binary string (e.g. '11110000...')
        poly (str): generator polynomial in binary (e.g. '100000111')
        shift (int): optional shift (default 0 = align mask at LSB)

    Returns:
        str: corrupted binary string (same length as data)
    """
    n = len(data)
    m = len(poly)

    # pad polynomial to length of data, shifted into place
    mask = ['0'] * n
    for i, bit in enumerate(poly):
        if bit == '1':
            pos = n - m - shift + i  # align poly with right side then shift
            if 0 <= pos < n:
                mask[pos] = '1'

    # XOR data with mask
    corrupted = [
        '1' if (d != m) else '0'
        for d, m in zip(data, mask)
    ]

    return ''.join(corrupted)
