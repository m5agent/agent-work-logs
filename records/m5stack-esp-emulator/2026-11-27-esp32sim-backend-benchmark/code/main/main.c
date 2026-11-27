#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
/* CPU-bound mix: CRC32, integer matrix multiply, list sort, all checksummed */
static uint32_t crc32(const uint8_t *p, size_t n){uint32_t c=~0u;while(n--){c^=*p++;for(int k=0;k<8;k++)c=(c>>1)^(0xEDB88320u&-(c&1));}return ~c;}
static int32_t A[24][24],Bm[24][24],C[24][24];
static uint32_t work(uint32_t seed){
  uint8_t buf[512]; for(int i=0;i<512;i++){seed=seed*1103515245u+12345u;buf[i]=seed>>16;}
  uint32_t r=crc32(buf,512);
  for(int i=0;i<24;i++)for(int j=0;j<24;j++){A[i][j]=(int32_t)(r+i*7+j);Bm[i][j]=(int32_t)(r^(i*j));}
  for(int i=0;i<24;i++)for(int j=0;j<24;j++){int32_t s=0;for(int k=0;k<24;k++)s+=A[i][k]*Bm[k][j];C[i][j]=s;}
  int32_t v[128]; for(int i=0;i<128;i++){seed=seed*1664525u+1013904223u;v[i]=(int32_t)seed;}
  for(int i=1;i<128;i++){int32_t x=v[i];int j=i-1;while(j>=0&&v[j]>x){v[j+1]=v[j];j--;}v[j+1]=x;}
  return r^(uint32_t)C[5][7]^(uint32_t)v[64];
}
void app_main(void){
  printf("BENCH_START\n");
  uint32_t acc=0, iters=0; int64_t t0=esp_timer_get_time(), last=t0;
  for(int sec=1; sec<=20;){
    acc^=work(acc+iters); iters++;
    int64_t now=esp_timer_get_time();
    if(now-last>=1000000){ printf("BENCH sec=%d iters=%lu acc=%08lx\n",sec,(unsigned long)iters,(unsigned long)acc); last=now; sec++; vTaskDelay(1);}
  }
  printf("BENCH_DONE iters=%lu acc=%08lx guest_us=%lld\n",(unsigned long)iters,(unsigned long)acc,(long long)(esp_timer_get_time()-t0));
  while(1) vTaskDelay(1000);
}
