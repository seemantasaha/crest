# 1 "math.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "math.c"
# 12 "math.c"
# 1 "../bin/../include/crest.h" 1
# 136 "../bin/../include/crest.h"
typedef enum {

  __CREST_ADD = 0,
  __CREST_SUBTRACT = 1,
  __CREST_MULTIPLY = 2,
  __CREST_DIVIDE = 3,
  __CREST_MOD = 4,

  __CREST_AND = 5,
  __CREST_OR = 6,
  __CREST_XOR = 7,
  __CREST_SHIFT_L = 8,
  __CREST_SHIFT_R = 9,

  __CREST_L_AND = 10,
  __CREST_L_OR = 11,

  __CREST_EQ = 12,
  __CREST_NEQ = 13,
  __CREST_GT = 14,
  __CREST_LEQ = 15,
  __CREST_LT = 16,
  __CREST_GEQ = 17,

  __CREST_CONCRETE = 18,

  __CREST_NEGATE = 19,
  __CREST_NOT = 20,
  __CREST_L_NOT = 21,
};
# 176 "../bin/../include/crest.h"
extern void __CrestInit() __attribute__((crest_skip));
extern void __CrestLoad(int, unsigned long int, long long int) __attribute__((crest_skip));
extern void __CrestStore(int, unsigned long int) __attribute__((crest_skip));
extern void __CrestClearStack(int) __attribute__((crest_skip));
extern void __CrestApply1(int, int, long long int) __attribute__((crest_skip));
extern void __CrestApply2(int, int, long long int) __attribute__((crest_skip));
extern void __CrestBranch(int, int, unsigned char) __attribute__((crest_skip));
extern void __CrestCall(int, unsigned int) __attribute__((crest_skip));
extern void __CrestReturn(int) __attribute__((crest_skip));
extern void __CrestHandleReturn(int, long long int) __attribute__((crest_skip));
# 197 "../bin/../include/crest.h"
extern void __CrestUChar(unsigned char* x) __attribute__((crest_skip));
extern void __CrestUShort(unsigned short* x) __attribute__((crest_skip));
extern void __CrestUInt(unsigned int* x) __attribute__((crest_skip));
extern void __CrestChar(char* x) __attribute__((crest_skip));
extern void __CrestShort(short* x) __attribute__((crest_skip));
extern void __CrestInt(int* x) __attribute__((crest_skip));
# 13 "math.c" 2

int main(void) {
  int a, b, c, d, e;
  __CrestInt(&a);
  __CrestInt(&b);
  __CrestInt(&c);
  __CrestInt(&d);
  __CrestInt(&e);
  if (3*a + 3*(b - 5*c) + (b+c) - a <= d - 17*e) {
    return 1;
  } else {
    return 0;
  }
}
