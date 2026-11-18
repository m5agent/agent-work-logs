// Replays the first-chunk arithmetic of the I2C write path:
//   size_t len = ((length - 1) % txfifo_limit) + 1;   then len = txfifo_limit
// and reports the largest single FIFO burst each (limit, hardware depth) pair produces.
#include <cstddef>
#include <cstdint>
#include <cstdio>

static void sim(uint32_t lim, int lo, int hi, uint32_t hw, const char* tag) {
  int worst = 0, worst_len = 0, over = 0, sumbad = 0;
  for (int n = lo; n <= hi; ++n) {
    size_t rem = (size_t)n, len = ((size_t)(n - 1) % lim) + 1, total = 0;
    int maxchunk = 0;
    do {
      if ((int)len > maxchunk) maxchunk = (int)len;
      total += len; rem -= len; len = lim;
    } while (rem);
    if (total != (size_t)n) ++sumbad;
    if (maxchunk > worst) { worst = maxchunk; worst_len = n; }
    if ((uint32_t)maxchunk > hw) ++over;
  }
  std::printf("%-26s lim=%2u lens %d..%d : max chunk %2d (at %3d bytes), chunks > HW %2u : %d, bad sums: %d\n",
              tag, lim, lo, hi, worst, worst_len, hw, over, sumbad);
}

int main() {
  sim(32, 9, 97, 16, "6.x base, LP hw=16");
  sim(16, 9, 97, 16, "PR head, LP hw=16");
  sim(16, 9, 97, 16, "5.x, C5/C6/P4 LP");
  sim(32, 33, 97, 32, "6.x base, HP hw=32");
  sim(32, 33, 97, 16, "6.x base, C2 hw=16");
  sim(16, 33, 97, 16, "PR head, C2 hw=16");
  return 0;
}
