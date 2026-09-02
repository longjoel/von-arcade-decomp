/* Recovered identity reset and direct translation-tail write for opcode 0x37. */

void recovered_sharc_opcode_37_reset(
    const float translation[3], float matrix[9], float tail[3])
{
    matrix[0] = 1.0f;
    matrix[1] = 0.0f;
    matrix[2] = 0.0f;
    matrix[3] = 0.0f;
    matrix[4] = 1.0f;
    matrix[5] = 0.0f;
    matrix[6] = 0.0f;
    matrix[7] = 0.0f;
    matrix[8] = 1.0f;

    tail[0] = translation[0];
    tail[1] = translation[1];
    tail[2] = translation[2];
}
