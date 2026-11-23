#include <cstdint>
#include <cstdio>
#include <cstddef>
#include <initializer_list>
namespace t {
#include "funcs_head.inc"
}
static void chunks(const char* tag, unsigned limit, size_t length)
{
  size_t remain = length;
  size_t first = ((length - 1) % limit) + 1;
  size_t maxc = 0, n = 0, sum = 0, len = first;
  while (remain) { if (len > maxc) maxc = len; sum += len; ++n; remain -= len; len = limit; }
  printf("  %s limit=%u n=%zu max=%zu sum=%zu first=%zu\n", tag, limit, n, maxc, sum, first);
}
int main()
{
  printf("fifo:");
  for (int p = 0; p < 4; ++p) printf(" p%d=%u", p, t::getFifoLen(p));
  printf("\n");
  for (size_t L : {17u, 18u, 24u, 97u}) {
    printf("len=%zu\n", L);
    chunks("limit", 32, L);
    chunks("limit", 16, L);
  }
  return 0;
}
