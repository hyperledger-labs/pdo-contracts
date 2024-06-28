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

#pragma once

#include <algorithm>
#include <array>
#include <vector>
#include <initializer_list>
#include <stdint.h>

#include "Cryptography.h"
#include "Types.h"

/*
   This file contains a very simple implementation of big numbers. Specifically,
   it defines addition, subtraction and modulus operations for positive integers
   with fixed byte size. The numbers are encoded most significant digits at the
   low index in the array.
*/
namespace ww
{
namespace types
{
    // Big number operations
    int cmp_big_numbers(const std::vector<uint8_t>& num1, const std::vector<uint8_t>& num2);
    bool add_big_numbers(const std::vector<uint8_t>& num1, const std::vector<uint8_t>& num2, std::vector<uint8_t>& result);
    bool sub_big_numbers(const std::vector<uint8_t>& num1, const std::vector<uint8_t>& num2, std::vector<uint8_t>& result);
    bool mod_big_numbers(const std::vector<uint8_t>& num, const std::vector<uint8_t>& mod, std::vector<uint8_t>& result);
    bool shift_left_big_numbers(const size_t shift, const std::vector<uint8_t>& num, std::vector<uint8_t>& result);
    size_t find_most_significant_bit(const std::vector<uint8_t>& num);

    // Bit operations
    uint8_t get_bit(const std::vector<uint8_t>& v, const size_t index);
    void set_bit(const size_t index, const uint8_t value, std::vector<uint8_t>& v);

    template<std::size_t SIZE>
    class BigNum : protected ww::types::ByteArray
    {
    private:

    public:
        // Constructors
        BigNum(void) {
            resize(SIZE);
        };

        BigNum(std::initializer_list<uint8_t> n) : BigNum() {
            if (n.size() != SIZE)
                return; // throw std::runtime_error("bad length");

            std::copy_n(n.begin(), SIZE, this->begin());
        };

        BigNum(const ww::types::ByteArray& n) : BigNum()
        {
            this->decode(n);
        };

        BigNum(const std::string& encoded) : BigNum()
        {
            this->decode(encoded);
        }

        // assign from a raw byte array
        bool decode(const ww::types::ByteArray& n)
        {
            if (n.size() != SIZE)
                return false;
            std::copy_n(n.begin(), SIZE, this->begin());
            return true;
        }

        // copy to a raw byte array
        bool encode(ww::types::ByteArray& n) const
        {
            n.resize(SIZE);
            std::copy_n(this->begin(), SIZE, n.begin());
            return true;
        }

        // assign from a base64 encoded string
        bool decode(const std::string& encoded)
        {
            ww::types::ByteArray decoded;
            if (! ww::crypto::b64_decode(encoded, decoded))
                return false;
            return this->decode(decoded);
        }

        // copy to a base64 encoded string
        bool encode(std::string& encoded) const
        {
            ww::types::ByteArray n;
            if (! this->encode(n))
                return false;
            return ww::crypto::b64_encode(n, encoded);
        }

        void reset(void)
        {
            std::fill(this->begin(), this->end(), 0);
        };

        // Arithmetic operators
        BigNum<SIZE> operator+(const BigNum<SIZE> &b) const
        {
            BigNum<SIZE> result;
            ww::types::add_big_numbers(*this, b, result);
            return result;
        };

        BigNum<SIZE> operator-(const BigNum<SIZE> &b) const
        {
            BigNum<SIZE> result;
            ww::types::sub_big_numbers(*this, b, result);
            return result;
        };

        BigNum<SIZE> operator%(const BigNum<SIZE> &b) const
        {
            BigNum<SIZE> result;
            ww::types::mod_big_numbers(*this, b, result);
            return result;
        };

        // Comparison operators
        bool operator<(const BigNum<SIZE> &b) const
        {
            return ww::types::cmp_big_numbers(*this, b) < 0;
        };

        bool operator<=(const BigNum<SIZE> &b) const
        {
            return ww::types::cmp_big_numbers(*this, b) <= 0;
        };

        bool operator>(const BigNum<SIZE> &b) const
        {
            return ww::types::cmp_big_numbers(*this, b) > 0;
        };

        bool operator>=(const BigNum<SIZE> &b) const
        {
            return ww::types::cmp_big_numbers(*this, b) >= 0;
        };

        bool operator==(const BigNum<SIZE> &b) const
        {
            return ww::types::cmp_big_numbers(*this, b) == 0;
        };
    };

    typedef BigNum<4> BigNum32;
    typedef BigNum<32> BigNum256;
    typedef BigNum<48> BigNum384;
    typedef BigNum<64> BigNum512;
}; // types
} // ww
