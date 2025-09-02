"""
This module implements CRC (Cyclic Redundancy Check) generation and verification for binary data using various standard CRC polynomials.
Functions:
    xor_division(dividend: str, divisor: str) -> str:
        Performs bitwise XOR division (modulo-2 division) of the dividend by the divisor (polynomial) and returns the remainder.
    generate_crc(data: str) -> str:
        Generates the CRC code for the given binary data using the selected polynomial and returns the data appended with the CRC remainder.
    verify_crc(data: str) -> bool:
        Verifies the integrity of the received binary data (including CRC) using the selected polynomial. Returns True if no error is detected, otherwise False.
Global Variables:
    polynomials: dict
        Dictionary mapping CRC scheme names to their corresponding binary polynomial strings.
    polynomial: str
        The currently selected polynomial name or binary string.
Usage:
    Select a polynomial by setting the 'polynomial' variable to one of the keys in 'polynomials' (e.g., "CRC-16").
    Use 'generate_crc' to append CRC to data before transmission.
    Use 'verify_crc' to check received data for errors.
Note:
    The module expects binary strings as input data.
"""

polynomials = {
    "CRC-8": "100000111",
    "CRC-10": "11000000011",
    "CRC-16": "11000000000000101",
    "CRC-32": "100000100110000010001110110110111",
}

polynomial = ""

def xor_division(dividend:str, divisor:str)->str:
    """
    Performs bitwise XOR division (modulo-2 division) of a binary dividend by a binary divisor.
    This function simulates the division process used in CRC (Cyclic Redundancy Check) calculations.
    It repeatedly XORs the divisor with the current bits of the dividend and shifts left, 
    returning the remainder after the division.
    Args:
        dividend (str): The binary string representing the dividend.
        divisor (str): The binary string representing the divisor (generator polynomial).
    Returns:
        str: The binary string representing the remainder after XOR division.
    """
    n = len(divisor)
    pick = n
    temp = dividend[:pick]
    
    while pick < len(dividend):
        if temp[0] == '1':
            temp = format(int(temp, 2)^int(divisor, 2), '0' + str(n) + 'b')
        temp = temp[1:]+dividend[pick]
        pick += 1
        
    if temp[0] == '1':
        temp = format(int(temp, 2)^int(divisor, 2), '0' + str(n) + 'b')
        
    return temp[1:]

def generate_crc(data:str, polynomial:str) -> str:
    """
    Generates a CRC (Cyclic Redundancy Check) code for the given data using a specified polynomial.
    Args:
        data (str): The binary string data to encode.
    Returns:
        str: The original data concatenated with the CRC remainder (the data to send).
    Notes:
        - Uses a global variable 'polynomial' to determine the CRC polynomial.
        - If 'polynomial' is a key in the global 'polynomials' dictionary, it is replaced with its value.
        - The function appends (len(polynomial)-1) zeros to the data before performing the XOR division.
        - The 'xor_division' function is used to compute the CRC remainder.
    """
    if not data:
        return ""
    # global polynomial
    if polynomial in polynomials:
        polynomial = polynomials[polynomial]

    dividend = data + '0'*(len(polynomial)-1)
    
    rem = xor_division(dividend, polynomial)
    
    # data_to_send = data+rem
    return rem

def verify_crc(data:str, polynomial:str)->bool:
    """
    Verifies the integrity of the given data using CRC (Cyclic Redundancy Check).
    Args:
        data (str): The binary string data to be verified.
    Returns:
        bool: True if the CRC remainder is zero (data is valid), False otherwise.
    Notes:
        - Uses a global 'polynomial' and a dictionary 'polynomials' for CRC calculation.
        - Relies on the 'xor_division' function to compute the remainder.
    """
    if not data:
        return True
    # global polynomial
    if polynomial in polynomials:
        polynomial = polynomials[polynomial]
        
    dividend = data
    
    rem = xor_division(dividend, polynomial)
    return int(rem, 2)==0
