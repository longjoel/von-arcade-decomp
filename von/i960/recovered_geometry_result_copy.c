/* Initial response placement shared by result builders at 0x9e050/0x9e250. */
typedef unsigned int u32;

void recovered_geometry_result_copy(const u32 responses[3],
                                    u32 left_record[7],
                                    u32 right_record[7])
{
    left_record[0] = responses[0];
    left_record[1] = responses[1];
    left_record[2] = responses[2];
    right_record[4] = responses[0];
    right_record[5] = responses[1];
    right_record[6] = responses[2];
}
