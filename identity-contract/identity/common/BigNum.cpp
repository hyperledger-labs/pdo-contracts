/* Copyright 2023 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


#include <algorithm>
#include <array>
#include <vector>
#include <initializer_list>
#include <stdint.h>

#include "BigNum.h"

#define MAXIMUM_WORD_VALUE 256

// -----------------------------------------------------------------
// Bit operations
// -----------------------------------------------------------------
uint8_t ww::types::get_bit(
    const ww::types::ByteArray& v,
    const size_t index)
{
    uint8_t byte = v[index / 8];
    return ((byte >> (8 - (index % 8) - 1)) & 0x01);
}

void ww::types::set_bit(
    const size_t index,
    const uint8_t value,
    ww::types::ByteArray& v)
{
    uint8_t byte = v[index / 8];
    uint8_t mask = (0x01 << (8 - (index % 8) - 1));
    byte = value ? (byte | mask) : (byte & (~ mask));
    v[index / 8] = byte;
}

// -----------------------------------------------------------------
// cmp_big_numbers
// Compare two big numbers with return similar to other comparison
// operators: <0 if num1 < num2, 0 if num1 == num2, 1 if num1 > num2;
// -255 if something has gone wrong.
// -----------------------------------------------------------------
int ww::types::cmp_big_numbers(
    const ww::types::ByteArray& num1,
    const ww::types::ByteArray& num2)
{
    // we don't really have an error and cant throw an
    // exception
    if (num1.size() != num2.size())
        return -255;

    const size_t SIZE = num1.size();

    for (size_t i = 0; i < SIZE; i++)
    {
        if (num1[i] < num2[i])
            return -1;
        else if (num1[i] > num2[i])
            return 1;
    }

    return 0;
}

// -----------------------------------------------------------------
// add_big_numbers
//
// Add two equally sized big numbers, put the result in another
// big number, numbers are encoded in ByteArrays, numbers are all
// assumed to be positive and there is no overflow.
// -----------------------------------------------------------------
bool ww::types::add_big_numbers(
    const ww::types::ByteArray& num1,
    const ww::types::ByteArray& num2,
    ww::types::ByteArray& result)
{
    if (num1.size() != num2.size())
        return false;

    const size_t SIZE = num1.size();

    result.resize(SIZE);
    result.assign(SIZE, 0);

    uint8_t carry = 0;

    // least significant digit to most significant
    for (size_t i = SIZE; i > 0; i--)
    {
        uint32_t sum = carry + num1[i-1] + num2[i-1];
        carry = sum / MAXIMUM_WORD_VALUE;
        result[i-1] = sum % MAXIMUM_WORD_VALUE;
    }

    return true;
}

// -----------------------------------------------------------------
// sub_big_numbers
//
// Subtract one big number from another and put the result into a
// third. Big numbers are assumed to be positive and the result must
// be positive (e.g. num1 > num2).
// -----------------------------------------------------------------
bool ww::types::sub_big_numbers(
    const ww::types::ByteArray& num1,
    const ww::types::ByteArray& num2,
    ww::types::ByteArray& result)
{
    if (num1.size() != num2.size())
        return false;

    const size_t SIZE = num1.size();

    // num1 must be greater than num2
    if (cmp_big_numbers(num1, num2) < 0)
        return false;

    result.resize(SIZE);
    result.assign(SIZE, 0);

    uint8_t borrow = 0;

    // least significant digit to most significant
    for (size_t i = SIZE; i > 0; i--)
    {
        if (num1[i-1] - borrow < num2[i-1])
        {
            result[i-1] = MAXIMUM_WORD_VALUE + num1[i-1] - borrow - num2[i-1];
            borrow = 1;
        }
        else
        {
            result[i-1] = num1[i-1] - borrow - num2[i-1];
            borrow = 0;
        }
    }

    return true;
}

// -----------------------------------------------------------------
// mod_big_numbers
//
// Compute the remainder after dividing one big number from another.
// Put the result into a third. All numbers are assumed to be positive.
// -----------------------------------------------------------------
bool ww::types::mod_big_numbers(
    const ww::types::ByteArray& num,
    const ww::types::ByteArray& mod,
    ww::types::ByteArray& result)
{
    if (num.size() != mod.size())
        return false;

    const size_t SIZE = num.size();

    result.resize(SIZE);
    result.assign(SIZE, 0);

    // if num < mod, then the result is num
    if (cmp_big_numbers(num, mod) < 0)
    {
        result.assign(num.begin(), num.end());
        return true;
    }

    size_t msb_num = find_most_significant_bit(num);
    size_t msb_mod = find_most_significant_bit(mod);
    ww::types::ByteArray temp_num = num;

    // Multiply mod so that it is almost as big as num, basically
    // this code fixes one binary digit at a time in the subtraction
    for (size_t i = msb_mod - msb_num + 1; i > 0; i--)
    {
        ww::types::ByteArray temp_mod;

        shift_left_big_numbers(i-1, mod, temp_mod);
        if (cmp_big_numbers(temp_mod,temp_num) < 0)
        {
            if (! sub_big_numbers(temp_num, temp_mod, result))
                return false;

            temp_num = result;
        }
    }

    return true;
}

// -----------------------------------------------------------------
// shift_left_big_numbers
//
// Shift bits from least significant to most significant, dropping
// any carry bits. Copy the result to a new array.
// -----------------------------------------------------------------
bool ww::types::shift_left_big_numbers(
    const size_t shift,
    const ww::types::ByteArray& num,
    ww::types::ByteArray& result)
{
    const size_t SIZE = num.size();

    if (8 * SIZE <= shift)
        return false;

    result.resize(SIZE);
    result.assign(SIZE, 0);

    for (size_t i = 0; i < (8 * SIZE) - shift; i++)
    {
        uint8_t b = ww::types::get_bit(num, i+shift);
        ww::types::set_bit(i, b, result);
    }

    return true;
}

// -----------------------------------------------------------------
// find_most_significant_bit
//
// Utility function that helps to compute modulus
// -----------------------------------------------------------------
size_t ww::types::find_most_significant_bit(
    const ww::types::ByteArray& num)
{
    const size_t SIZE = num.size();

    size_t w, b;
    for (w = 0; w < SIZE; w++)
    {
        if (num[w] > 0) break;
    }

    uint8_t word = num[w];
    for (b = 0; b < 8; b++)
    {
        if (word & 0x80)
            break;
        word = word << 1;
    }

    return w * 8 + b;
}
