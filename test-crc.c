#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint8_t crc_t;

crc_t crc_update(crc_t crc, const void *data, size_t data_len) {
	const unsigned char *d = (const unsigned char *)data;
	unsigned int i;
	bool bit;
	unsigned char c;

	while (data_len--) {
		c = *d++;
		for (i = 0x80; i > 0; i >>= 1) {
			bit = crc & 0x80;
			if (c & i) {
				bit = !bit;
			}
			crc <<= 1;
			if (bit) {
				crc ^= 0x07;
			}
		}
		crc &= 0xff;
	}
	return crc & 0xff;
}

int main()
{
	uint8_t test1[] = { 1, 2, 3 };
	uint8_t test2[] = { 0, 255, 3, 245 };

	printf("%d\n", crc_update(0, test1, sizeof(test1)));
	printf("%d\n", crc_update(0, test2, sizeof(test2)));

	return 0;
}
