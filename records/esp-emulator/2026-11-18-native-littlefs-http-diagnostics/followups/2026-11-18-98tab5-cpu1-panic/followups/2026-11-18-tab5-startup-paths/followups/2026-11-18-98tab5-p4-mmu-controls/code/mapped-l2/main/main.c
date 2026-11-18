#include <inttypes.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>

#include "esp_attr.h"
#include "esp_cpu.h"
#include "esp_memory_utils.h"
#include "esp_rom_sys.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "esp32p4/rom/cache.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

enum {
    PAGE_BYTES = 0x10000,
    CHUNK_OPS = 256,
    PHASES = 2,
    PHASE_TIME_US = 250000,
};
#define FIRST_WORD UINT32_C(0x243f6a88)
#define OTHER_WORD UINT32_C(0x85a308d3)

static const uint32_t probe_page[PAGE_BYTES / sizeof(uint32_t)] __attribute__((aligned(PAGE_BYTES))) = {
    FIRST_WORD,
};
static const uint32_t other_page[PAGE_BYTES / sizeof(uint32_t)] __attribute__((aligned(PAGE_BYTES))) = {
    OTHER_WORD,
};

static atomic_uint command, request_seq, reader_ready, reader_done;
static atomic_uint reader_loads, reader_overlap, reader_bad, reader_zero;
static TaskHandle_t reader_handle;

static void IRAM_ATTR read_window(void *data)
{
    const volatile uint32_t *word = data;
    if (esp_cpu_get_core_id() != 1) {
        vTaskDelete(NULL);
        return;
    }
    atomic_store_explicit(&reader_ready, 1, memory_order_release);
    for (unsigned phase = 1; phase <= PHASES; ++phase) {
        (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        unsigned loads = 0;
        unsigned overlaps = 0;
        unsigned bad = 0;
        unsigned zero = 0;
        while (atomic_load_explicit(&command, memory_order_acquire) == phase) {
            unsigned before = atomic_load_explicit(&request_seq, memory_order_acquire);
            uint32_t value = *word;
            unsigned after = atomic_load_explicit(&request_seq, memory_order_acquire);
            ++loads;
            overlaps += before == after && (before & 1u);
            bad += value != FIRST_WORD;
            zero += value == 0;
        }
        atomic_store_explicit(&reader_loads, loads, memory_order_relaxed);
        atomic_store_explicit(&reader_overlap, overlaps, memory_order_relaxed);
        atomic_store_explicit(&reader_bad, bad, memory_order_relaxed);
        atomic_store_explicit(&reader_zero, zero, memory_order_relaxed);
        atomic_store_explicit(&reader_done, phase, memory_order_release);
    }
    vTaskDelete(NULL);
}

static bool await(atomic_uint *flag, unsigned goal)
{
    int64_t until = esp_timer_get_time() + 100000;
    while (atomic_load_explicit(flag, memory_order_acquire) != goal && esp_timer_get_time() < until) {
        vTaskDelay(1);
    }
    return atomic_load_explicit(flag, memory_order_acquire) == goal;
}

static unsigned IRAM_ATTR run_batch(const volatile uint32_t *word, bool invalidate)
{
    unsigned errors = 0;
    for (unsigned i = 0; i < CHUNK_OPS; ++i) {
        atomic_fetch_add_explicit(&request_seq, 1, memory_order_release);
        if (invalidate) {
            errors += Cache_Invalidate_Addr(CACHE_MAP_L2_CACHE, (uint32_t)(uintptr_t)word, PAGE_BYTES) != 0;
        } else {
            errors += *word != OTHER_WORD;
        }
        atomic_fetch_add_explicit(&request_seq, 1, memory_order_release);
    }
    return errors;
}

void app_main(void)
{
    const volatile uint32_t *reader = probe_page;
    const volatile uint32_t *writer = other_page;
    bool mapped = esp_ptr_in_drom(probe_page) && esp_ptr_in_drom(other_page)
                && (((uintptr_t)probe_page | (uintptr_t)other_page) & (PAGE_BYTES - 1)) == 0
                && (uintptr_t)probe_page != (uintptr_t)other_page;
    esp_err_t wdt0 = esp_task_wdt_status(xTaskGetIdleTaskHandleForCPU(0));
    esp_err_t wdt1 = esp_task_wdt_status(xTaskGetIdleTaskHandleForCPU(1));
    printf("CACHE_XCORE_BOUNDARY core=%d reader=%p writer=%p mapped=%d word_a=%08" PRIx32
           " word_b=%08" PRIx32 " int_wdt=%d task_idle_wdt=%d,%d\n",
           esp_cpu_get_core_id(), probe_page, other_page, mapped, *reader, *writer,
           CONFIG_ESP_INT_WDT, (int)wdt0, (int)wdt1);
    if (!mapped || *reader != FIRST_WORD || *writer != OTHER_WORD || wdt0 || wdt1
            || esp_cpu_get_core_id() != 0
            || xTaskCreatePinnedToCore(read_window, "cache-reader", 4096, (void *)reader, 4, &reader_handle, 1) != pdPASS
            || !await(&reader_ready, 1)) {
        puts("CACHE_XCORE_FAIL setup");
        return;
    }

    bool passed = true;
    for (unsigned phase = 1; phase <= PHASES; ++phase) {
        atomic_store_explicit(&command, phase, memory_order_release);
        xTaskNotifyGive(reader_handle);
        const int64_t end = esp_timer_get_time() + PHASE_TIME_US;
        unsigned calls = 0;
        unsigned errors = 0;
        do {
            errors += run_batch(writer, phase == 2);
            calls += CHUNK_OPS;
            vTaskDelay(1);
        } while (esp_timer_get_time() < end);
        atomic_store_explicit(&command, 0, memory_order_release);
        if (!await(&reader_done, phase)) {
            puts("CACHE_XCORE_FAIL reader_barrier");
            return;
        }
        unsigned loads = atomic_load_explicit(&reader_loads, memory_order_relaxed);
        unsigned overlap = atomic_load_explicit(&reader_overlap, memory_order_relaxed);
        unsigned bad = atomic_load_explicit(&reader_bad, memory_order_relaxed);
        unsigned zero = atomic_load_explicit(&reader_zero, memory_order_relaxed);
        printf("CACHE_XCORE_PHASE phase=%s cpu0_calls=%u call_errors=%u cpu1_loads=%u midcall_loads=%u "
               "bad=%u zero=%u after=%08" PRIx32 ",%08" PRIx32 "\n",
               phase == 1 ? "baseline_read" : "l2_invalidate_other_page",
               calls, errors, loads, overlap, bad, zero, *reader, *writer);
        passed &= errors == 0 && loads > 0 && bad == 0 && *reader == FIRST_WORD && *writer == OTHER_WORD
                  && (phase != 2 || overlap > 0);
    }
    puts(passed ? "CACHE_XCORE_PASS" : "CACHE_XCORE_FAIL dataplane");
    fflush(stdout);
}
