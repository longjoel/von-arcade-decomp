/* Pure pieces of the communication-board recovery path at i960 0xc5870. */

#include <stdint.h>

enum recovered_comm_role_message {
    RECOVERED_COMM_ROLE_RELAY = 0,
    RECOVERED_COMM_ROLE_MASTER = 1,
    RECOVERED_COMM_ROLE_SLAVE = 2,
    RECOVERED_COMM_ROLE_STANDALONE = 3,
    RECOVERED_COMM_ROLE_ILLEGAL = 4
};

/* The ROM's five-way branch on byte 0x5770b1. */
enum recovered_comm_role_message recovered_comm_role_message(uint8_t node_role)
{
    if (node_role == 0U)
        return RECOVERED_COMM_ROLE_RELAY;
    if (node_role == 1U)
        return RECOVERED_COMM_ROLE_MASTER;
    if (node_role == 2U)
        return RECOVERED_COMM_ROLE_SLAVE;
    if (node_role == 3U)
        return RECOVERED_COMM_ROLE_STANDALONE;
    return RECOVERED_COMM_ROLE_ILLEGAL;
}

/* Bit 0 set is the immediate "no communication board" failure path. */
uint8_t recovered_comm_board_present(uint8_t status_byte)
{
    return (uint8_t)((status_byte & 1U) == 0U);
}

/* Hardware control-byte reset at 0xc5608. */
void recovered_comm_control_reset(uint8_t control_bytes[2])
{
    control_bytes[0] = 0;
    control_bytes[1] = 0;
}
