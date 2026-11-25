#include <stdio.h>
#include "tca8418_fsm.c"
static const char *state_name(tca8418_t *me){
  static const char *n[]={"IDLE","ACTIVE","WAIT_ACTIVE_LEAVE","ONESHOT","HOLD","LOCKED","LOCKED_WAIT_LEAVE","LOCKED_LEAVE"};
  return n[me->state];
}
void emit_key_pres_status(tca8418_t *me){(void)me;}
void emit_key_release_status(tca8418_t *me){(void)me;}
void led_ON(tca8418_t *me){(void)me;}
void led_OFF(tca8418_t *me){(void)me;}
void led_BLINK(tca8418_t *me){(void)me;}
void led_FAST(tca8418_t *me){(void)me;}
struct step { const char *name; Event e; };
static tca8418_t M;
static void run(const char *t, struct step *s, int n){
  tca8418_ctor(&M,0); M.layer_active=0;
  printf("== %s\n", t);
  for(int i=0;i<n;i++){ tca8418_dispatch(&M,s[i].e);
    printf("  %-18s -> %-18s layer=%d\n", s[i].name, state_name(&M), M.layer_active); }
  printf("  FINAL: %s layer=%d\n\n", state_name(&M), M.layer_active);
}
#define S(x) {#x, x}
int main(void){
  struct step fast[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_RELE),S(EV_TIMEOUT_300),S(EV_TIMEOUT_300)};
  run("tap, fast ordinary key (press is invisible pre-fix)", fast, 5);
  struct step chord[]={S(EV_KEY_PRES),S(EV_OTHER_KEY_RELE),S(EV_KEY_RELE),S(EV_TIMEOUT_300)};
  run("chord (key up before modifier up)", chord, 4);
  struct step oneshot[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_TIMEOUT_300),S(EV_OTHER_KEY_RELE)};
  run("plain tap/pause/one key", oneshot, 4);
  struct step hold[]={S(EV_KEY_PRES),S(EV_TIMEOUT_300),S(EV_KEY_RELE)};
  run("hold", hold, 3);
  struct step lock[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_KEY_PRES),S(EV_KEY_RELE)};
  run("double-tap lock + unlock", lock, 6);
  return 0;
}
