"""
This module provides functions to generate and verify checksums for binary data using a custom algorithm.
Functions:
    generate_checksum(data: str) -> str:
        Generates a checksum for the given binary string data.
        The data is split into chunks of fixed size, and each chunk is further divided into smaller bit-sized words.
        The checksum is calculated by summing the integer values of these words, folding any carries, and then taking the bitwise complement.
        The complemented checksum is appended to each chunk, and the resulting string is returned.
    verify_checksum(data: str) -> bool:
        Verifies the checksum of the given binary string data.
        The data is split into words consisting of the original chunk and its checksum.
        For each word, the integer values are summed, carries are folded, and the result is checked to be all 1s (indicating a valid checksum).
        Returns True if all checksums are valid, otherwise False.
Usage:
    The module can be used to generate checksums for binary data before transmission and verify the integrity of received data.
"""
chunk = 16
bit_size = 2*8

def generate_checksum(data: str) -> str:
    """
    Generates a checksum for the given binary data string using chunking and bitwise operations.
    The function splits the input data into chunks and further divides each chunk into words of a specified bit size.
    It then computes the sum of these words, folds any carries, and generates a checksum by complementing the result.
    The checksum is appended to each chunk, and the final result is the concatenation of all chunks with their checksums.
    Args:
        data (str): The binary string data to generate the checksum for.
    Returns:
        str: The binary string with appended checksums for each chunk.
    Note:
        The function expects the global variables `chunk` and `bit_size` to be defined, which determine the chunk size and word bit size respectively.
    """
    n = len(data)
    if n % chunk != 0:
        data = '0'*(chunk - n % chunk) + data
        n = len(data)

    # words = [data[i:i+chunk] for i in range(0, n, chunk)]
    checksum_strings = []
    word = data

    # for word in words:
    numbers = [int(word[i:i+bit_size], 2) for i in range(0, len(word), bit_size)]
    checksum = sum(numbers)

    while checksum >= (1 << bit_size):
        # fold carries
        checksum = (checksum >> bit_size) + (checksum & ((1 << bit_size)-1))

    checksum_string = format(checksum, '0{}b'.format(bit_size))
    # complement
    checksum_string_complemented = ''.join('0' if b == '1' else '1' for b in checksum_string)
    # checksum_strings.append(word + checksum_string_complemented)

    # return ''.join(checksum_strings)
    return checksum_string_complemented


def verify_checksum(data: str) -> bool:
    """
    Verifies the checksum of a binary data string using a specified word and bit size.
    Args:
        data (str): The binary string to verify.
    Returns:
        bool: True if the checksum is valid for all words in the data, False otherwise.
    Notes:
        - The function expects global variables `chunk` and `bit_size` to be defined.
        - Pads the data with leading zeros if its length is not a multiple of the word size.
        - Splits the data into words, then further into numbers of `bit_size` bits.
        - Sums the numbers and performs end-around carry until the sum fits in `bit_size` bits.
        - The checksum is valid if the result is all 1s in `bit_size` bits for every word.
    """
    n = len(data)
    word_size = chunk + bit_size
    if n % word_size != 0:
        data = '0'*(word_size - n % word_size) + data
        n = len(data)

    # words = [data[i:i+word_size] for i in range(0, n, word_size)]
    word = data

    # for word in words:
    numbers = [int(word[i:i+bit_size], 2) for i in range(0, len(word), bit_size)]
    checksum = sum(numbers)

    while checksum >= (1 << bit_size):
        checksum = (checksum >> bit_size) + (checksum & ((1 << bit_size)-1))

    if checksum != (1 << bit_size) - 1:  # must be all 1s
        return False

    return True
