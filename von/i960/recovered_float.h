#ifndef VON_RECOVERED_FLOAT_H
#define VON_RECOVERED_FLOAT_H

#include <stdint.h>

static inline float recovered_float_from_bits(uint32_t bits)
{
    union { uint32_t bits; float value; } value;
    value.bits = bits;
    return value.value;
}

static inline uint32_t recovered_float_to_bits(float value)
{
    union { uint32_t bits; float value; } result;
    result.value = value;
    return result.bits;
}

static inline uint32_t recovered_float_add_bits(uint32_t left_bits,
                                                uint32_t right_bits)
{
    return recovered_float_to_bits(recovered_float_from_bits(left_bits) +
                                   recovered_float_from_bits(right_bits));
}

static inline float recovered_rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

static inline float recovered_rounded_add(float left, float right)
{
    volatile float result = left + right;
    return result;
}

static inline float recovered_rounded_sub(float left, float right)
{
    volatile float result = left - right;
    return result;
}

static inline void recovered_rotate_y(float matrix[9], float sine, float cosine)
{
    for (unsigned column = 0; column < 3; ++column) {
        float row0 = matrix[column];
        float row2 = matrix[6 + column];
        matrix[column] = cosine * row0 + sine * row2;
        matrix[6 + column] = -sine * row0 + cosine * row2;
    }
}

static inline void recovered_rotate_x(float matrix[9], float sine, float cosine)
{
    for (unsigned column = 0; column < 3; ++column) {
        float row1 = matrix[3 + column];
        float row2 = matrix[6 + column];
        matrix[3 + column] = cosine * row1 - sine * row2;
        matrix[6 + column] = sine * row1 + cosine * row2;
    }
}

static inline void recovered_rotate_z(float matrix[9], float sine, float cosine)
{
    for (unsigned column = 0; column < 3; ++column) {
        float row0 = matrix[column];
        float row1 = matrix[3 + column];
        matrix[column] = cosine * row0 - sine * row1;
        matrix[3 + column] = sine * row0 + cosine * row1;
    }
}

#endif
