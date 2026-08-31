/* Recovered Model 2 polygon-ROM stream decoder; SHARC command production is separate. */
typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned long usize;

typedef struct { float x, y, z; } recovered_polygon_vec3;
typedef struct {
    u32 attribute, vertex_count;
    recovered_polygon_vec3 vertex[4];
} recovered_polygon_record;
typedef int (*recovered_polygon_emit)(void *, const recovered_polygon_record *);

static u32 read_u32(const u8 *p)
{
    return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}
static recovered_polygon_vec3 read_vec3(const u8 *p)
{
    union { u32 bits; float value; } convert;
    recovered_polygon_vec3 v;
    convert.bits = read_u32(p); v.x = convert.value;
    convert.bits = read_u32(p + 4); v.y = convert.value;
    convert.bits = read_u32(p + 8); v.z = convert.value;
    return v;
}
/* OBA low 22 bits are a word index. Records are attr, three auxiliary words, p2, p3. */
int recovered_polygon_rom_decode(const u8 *rom, usize bytes, u32 oba,
                                 u32 limit, recovered_polygon_emit emit, void *context)
{
    usize offset = (usize)(oba & 0x003fffffU) * 4U;
    recovered_polygon_vec3 p0, p1;
    u32 count = 0;
    if (!rom || !emit || offset > bytes || bytes - offset < 24) return -1;
    p0 = read_vec3(rom + offset); p1 = read_vec3(rom + offset + 12); offset += 24;
    while (offset <= bytes && bytes - offset >= 40) {
        recovered_polygon_record r; u32 link;
        r.attribute = read_u32(rom + offset);
        if (!(r.attribute & 3U)) break;
        r.vertex_count = (r.attribute & 1U) ? 4U : 3U;
        r.vertex[0] = p0; r.vertex[1] = p1;
        r.vertex[2] = read_vec3(rom + offset + 16); r.vertex[3] = read_vec3(rom + offset + 28);
        if (emit(context, &r)) return -2;
        ++count; if (limit && count >= limit) break;
        link = (r.attribute >> 8) & 3U;
        if (link == 0 || link == 2) { p0 = r.vertex[2]; p1 = r.vertex[3]; }
        else if (link == 1) p1 = r.vertex[2]; else p0 = r.vertex[3];
        offset += 40;
    }
    return (int)count;
}
