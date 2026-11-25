#include <stdio.h>
#include <string.h>
#include "tca8418_fsm.c"

static const char *state_name(tca8418_t *me){
  static const char *n[]={"IDLE","ACTIVE","WAIT_ACTIVE_LEAVE","ONESHOT","HOLD","LOCKED","LOCKED_WAIT_LEAVE","LOCKED_LEAVE"};
  return n[me->state];
}
/* action stubs: record modifiers' key up/down so we can see if release is emitted */
static int pres_cnt, rele_cnt, led_on_cnt, led_off_cnt;
void emit_key_pres_status(tca8418_t *me){(void)me;pres_cnt++;}
void emit_key_release_status(tca8418_t *me){(void)me;rele_cnt++;}
void led_ON(tca8418_t *me){(void)me;led_on_cnt++;}
void led_OFF(tca8418_t *me){(void)me;led_off_cnt++;}
void led_BLINK(tca8418_t *me){(void)me;}
void led_FAST(tca8418_t *me){(void)me;}

/* address of the dispatching entry points is internal; we drive via a shim built
 * into the same TU because tca8418_dispatch is static. */
static void send(tca8418_t *m, Event e){ tca8418_dispatch(m,e); }

struct step { const char *name; Event e; };
static void run(const char *title, tca8418_t *m, struct step *s, int n){
  tca8418_ctor(m,0); m->layer_active=0; m->used=0;
  printf("== %s\n", title);
  for(int i=0;i<n;i++){
    send(m,s[i].e);
    printf("  %-14s -> %-18s layer=%d used=%d\n", s[i].name, state_name(m), m->layer_active, m->used);
  }
  printf("  FINAL: state=%s layer=%d used=%d pres=%d rele=%d\n\n", state_name(m), m->layer_active, m->used, pres_cnt, rele_cnt);
}
static tca8418_t M;
#define S(x) {#x, x}
int main(void){
  struct step fast[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_PRES),S(EV_OTHER_KEY_RELE),S(EV_TIMEOUT_300)};
  run("tap Sym, key press+release inside 300ms (reported bug)", &M, fast, 5);

  struct step chord[]={S(EV_KEY_PRES),S(EV_OTHER_KEY_PRES),S(EV_OTHER_KEY_RELE),S(EV_KEY_RELE),S(EV_TIMEOUT_300)};
  run("chord in ACTIVE (key up before modifier up)", &M, chord, 5);

  struct step chord2[]={S(EV_KEY_PRES),S(EV_OTHER_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_RELE),S(EV_TIMEOUT_300)};
  run("chord, modifier up before key up", &M, chord2, 5);

  struct step oneshot[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_TIMEOUT_300),S(EV_OTHER_KEY_PRES),S(EV_OTHER_KEY_RELE)};
  run("plain tap, pause, one key (unchanged one-shot)", &M, oneshot, 5);

  struct step taponly[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_TIMEOUT_300)};
  run("tap and keep waiting (one-shot armed)", &M, taponly, 3);

  struct step hold[]={S(EV_KEY_PRES),S(EV_TIMEOUT_300),S(EV_KEY_RELE)};
  run("hold modifier (>=300ms)", &M, hold, 3);

  struct step lock[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_KEY_PRES),S(EV_KEY_RELE)};
  run("double tap lock, then tap to unlock", &M, lock, 6);

  struct step heldtimeout[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_PRES),S(EV_TIMEOUT_300),S(EV_OTHER_KEY_PRES),S(EV_OTHER_KEY_RELE)};
  run("tap, key pressed and HELD past 300ms, then 2nd key", &M, heldtimeout, 6);

  struct step roll[]={S(EV_OTHER_KEY_PRES),S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_TIMEOUT_300),S(EV_OTHER_KEY_RELE)};
  run("key already down before modifier tap (roll)", &M, roll, 5);

  struct step lockedexit[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_PRES),S(EV_OTHER_KEY_RELE)};
  run("locked, ordinary key release in LOCKED_WAIT_LEAVE", &M, lockedexit, 6);
  return 0;
}
