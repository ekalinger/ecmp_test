def jhash_1word(a: int, initval: int = 0) -> int:
    """Jenkins hash for a single 32-bit word."""
    # Internal mix function from jhash.h
    def __jhash_mix32(key: int) -> int:
        key = (key + 0x95f4a5f1) * 0x97968887
        key = ((key ^ (key >> 0x10)) + 0x85ebca6b) * 0xc2b2ae35
        return key ^ (key >> 0x0c)
    JHASH_INITVAL = 0x561ccd0b
    return __jhash_mix32(a) ^ __jhash_mix32(0) ^ __jhash_mix32(0) ^ (initval + JHASH_INITVAL + 4)