// Standalone ADSP-2106x 40-bit arithmetic oracle.
//
// This is intentionally independent of MAME's SHARC_REG implementation.  It
// is a small executable contract for the future interpreter/DRC conversion;
// it is not intended to be linked into the game or used as a fast emulator
// implementation.  The arbitrary-width intermediate keeps halfway and large
// exponent-distance cases exact.

#include <boost/multiprecision/cpp_int.hpp>

#include <cstdint>
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

using boost::multiprecision::cpp_int;

namespace {

constexpr int fraction_bits = 31;
constexpr int exponent_bias = 127;

struct binary_value
{
	bool negative = false;
	cpp_int significand = 0;
	int shift = 0;
};

binary_value decode(std::uint64_t raw)
{
	const unsigned exponent = (raw >> fraction_bits) & 0xffU;
	const std::uint32_t fraction = raw & 0x7fffffffU;
	if (exponent == 0 && fraction == 0)
	{
		binary_value zero;
		zero.negative = (raw >> 39) != 0;
		return zero;
	}
	if (exponent == 0 || exponent == 0xffU)
		throw std::runtime_error("reference input must be normal");

	binary_value value;
	value.negative = (raw >> 39) != 0;
	value.significand = (cpp_int(1) << fraction_bits) | fraction;
	value.shift = static_cast<int>(exponent) - exponent_bias - fraction_bits;
	return value;
}

cpp_int signed_significand(binary_value const &value)
{
	return value.negative ? -value.significand : value.significand;
}

std::uint64_t encode(binary_value value, int precision, bool truncate)
{
	if (value.significand == 0)
		return 0;

	cpp_int magnitude = value.significand;
	if (magnitude < 0)
	{
		magnitude = -magnitude;
		value.negative = !value.negative;
	}

	const unsigned bit_length = boost::multiprecision::msb(magnitude) + 1;
	int exponent = static_cast<int>(bit_length) - 1 + value.shift;
	cpp_int significand;

	if (bit_length > static_cast<unsigned>(precision))
	{
		const unsigned dropped = bit_length - precision;
		significand = magnitude >> dropped;
		const cpp_int remainder = magnitude - (significand << dropped);
		if (!truncate)
		{
			const cpp_int halfway = cpp_int(1) << (dropped - 1);
			if (remainder > halfway || (remainder == halfway && (significand & 1) != 0))
				++significand;
		}
	}
	else
	{
		significand = magnitude << (precision - bit_length);
	}

	if (significand == (cpp_int(1) << precision))
	{
		significand >>= 1;
		++exponent;
	}

	const int exponent_field = exponent + exponent_bias;
	if (exponent_field <= 0 || exponent_field >= 0xff)
		throw std::runtime_error("reference result is outside normal range");

	cpp_int fraction = significand - (cpp_int(1) << (precision - 1));
	if (precision < 32)
		fraction <<= 32 - precision;

	std::uint64_t result = (static_cast<std::uint64_t>(exponent_field) << fraction_bits) |
		static_cast<std::uint64_t>(fraction);
	if (value.negative)
		result |= std::uint64_t(1) << 39;
	return result;
}

binary_value rounded_input(std::uint64_t raw, bool rnd32, bool truncate)
{
	binary_value value = decode(raw);
	const std::uint64_t rounded = encode(value, rnd32 ? 24 : 32, truncate);
	return decode(rounded);
}

std::uint64_t binary_operation(std::string const &operation, std::uint64_t x,
	bool rnd32, bool truncate, std::uint64_t y)
{
	const int precision = rnd32 ? 24 : 32;
	binary_value left = rounded_input(x, rnd32, truncate);
	binary_value right = rounded_input(y, rnd32, truncate);
	binary_value result;

	if (operation == "FADD")
	{
		result.shift = std::min(left.shift, right.shift);
		const cpp_int left_value = signed_significand(left) << (left.shift - result.shift);
		const cpp_int right_value = signed_significand(right) << (right.shift - result.shift);
		const cpp_int sum = left_value + right_value;
		if (sum < 0)
		{
			result.negative = true;
			result.significand = -sum;
		}
		else
		{
			result.significand = sum;
		}
	}
	else if (operation == "FMUL")
	{
		const cpp_int product = signed_significand(left) * signed_significand(right);
		result.shift = left.shift + right.shift;
		if (product < 0)
		{
			result.negative = true;
			result.significand = -product;
		}
		else
		{
			result.significand = product;
		}
	}
	else
	{
		throw std::runtime_error("operation must be FADD or FMUL");
	}

	return encode(result, precision, truncate);
}

std::uint64_t float_integer(std::int64_t integer)
{
	binary_value value;
	value.negative = integer < 0;
	value.significand = integer < 0 ? -cpp_int(integer) : cpp_int(integer);
	return encode(value, 32, true);
}

std::uint64_t parse_raw(std::string const &text)
{
	size_t consumed = 0;
	const std::uint64_t value = std::stoull(text, &consumed, 0);
	if (consumed != text.size() || value >= (std::uint64_t(1) << 40))
		throw std::runtime_error("raw value is not a 40-bit integer");
	return value;
}

} // anonymous namespace

int main(int argc, char **argv)
{
	try
	{
		if (argc == 2 && std::string(argv[1]) == "FLOAT")
		{
			std::cout << std::hex << std::setfill('0') << std::setw(10) << float_integer(3) << '\n';
			return 0;
		}
		if (argc != 5 && argc != 6)
			throw std::runtime_error("usage: FADD|FMUL x y rnd32 truncate, or FLOAT");

		const std::string operation = argv[1];
		const std::uint64_t x = parse_raw(argv[2]);
		const std::uint64_t y = parse_raw(argv[3]);
		const bool rnd32 = std::stoi(argv[4]) != 0;
		const bool truncate = argc == 6 ? (std::stoi(argv[5]) != 0) : true;
		const std::uint64_t result = binary_operation(operation, x, rnd32, truncate, y);
		std::cout << std::hex << std::setfill('0') << std::setw(10) << result << '\n';
	}
	catch (std::exception const &error)
	{
		std::cerr << "sharc_40bit_reference: " << error.what() << '\n';
		return 2;
	}
	return 0;
}
