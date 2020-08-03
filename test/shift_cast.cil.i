# 1 "./shift_cast.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./shift_cast.cil.c"
# 16 "shift_cast.c"
void __globinit_shift_cast(void) ;
extern void __CrestInit(void) __attribute__((__crest_skip__)) ;
extern void __CrestHandleReturn(int id , long long val ) __attribute__((__crest_skip__)) ;
extern void __CrestReturn(int id ) __attribute__((__crest_skip__)) ;
extern void __CrestCall(int id , unsigned int fid ) __attribute__((__crest_skip__)) ;
extern void __CrestBranch(int id , int bid , unsigned char b ) __attribute__((__crest_skip__)) ;
extern void __CrestApply2(int id , int op , long long val ) __attribute__((__crest_skip__)) ;
extern void __CrestApply1(int id , int op , long long val ) __attribute__((__crest_skip__)) ;
extern void __CrestClearStack(int id ) __attribute__((__crest_skip__)) ;
extern void __CrestStore(int id , unsigned long addr ) __attribute__((__crest_skip__)) ;
extern void __CrestLoad(int id , unsigned long addr , long long val ) __attribute__((__crest_skip__)) ;
# 198 "../bin/../include/crest.h"
extern void __CrestUShort(unsigned short *x ) __attribute__((__crest_skip__)) ;
# 200 "../bin/../include/crest.h"
extern void __CrestChar(char *x ) __attribute__((__crest_skip__)) ;
# 202 "../bin/../include/crest.h"
extern void __CrestInt(int *x ) __attribute__((__crest_skip__)) ;
# 318 "/usr/include/stdio.h"
extern int printf(char const * __restrict __format , ...) ;
# 16 "shift_cast.c"
int main(void)
{
  unsigned short us ;
  signed char sc ;
  int x ;
  unsigned short kFFFF ;
  int __retres5 ;

  {
  __globinit_shift_cast();
  __CrestCall(1, 1);
# 21 "shift_cast.c"
  __CrestUShort(& us);
# 22 "shift_cast.c"
  __CrestChar((char *)(& sc));
# 23 "shift_cast.c"
  __CrestInt(& x);
  __CrestLoad(2, (unsigned long )0, (long long )(unsigned short)65535);
  __CrestStore(3, (unsigned long )(& kFFFF));
# 25 "shift_cast.c"
  kFFFF = (unsigned short)65535;
  __CrestLoad(8, (unsigned long )(& x), (long long )x);
  __CrestLoad(7, (unsigned long )0, (long long )18);
  __CrestApply2(6, 9, (long long )(x >> 18));
  __CrestLoad(5, (unsigned long )0, (long long )4294967295U);
  __CrestApply2(4, 12, (long long )((unsigned int )(x >> 18) == 4294967295U));
# 27 "shift_cast.c"
  if ((unsigned int )(x >> 18) == 4294967295U) {
    __CrestBranch(9, 3, 1);
# 28 "shift_cast.c"
    printf((char const * __restrict )"A\n");
    __CrestClearStack(11);
  } else {
    __CrestBranch(10, 4, 0);
    {
    __CrestLoad(16, (unsigned long )(& us), (long long )us);
    __CrestLoad(15, (unsigned long )0, (long long )7);
    __CrestApply2(14, 9, (long long )((int )us >> 7));
    __CrestLoad(13, (unsigned long )(& kFFFF), (long long )kFFFF);
    __CrestApply2(12, 12, (long long )((int )us >> 7 == (int )kFFFF));
# 29 "shift_cast.c"
    if ((int )us >> 7 == (int )kFFFF) {
      __CrestBranch(17, 5, 1);
# 30 "shift_cast.c"
      printf((char const * __restrict )"B\n");
      __CrestClearStack(19);
    } else {
      __CrestBranch(18, 6, 0);
      {
      __CrestLoad(22, (unsigned long )(& sc), (long long )sc);
      __CrestLoad(21, (unsigned long )0, (long long )-42);
      __CrestApply2(20, 12, (long long )((int )sc == -42));
# 31 "shift_cast.c"
      if ((int )sc == -42) {
        __CrestBranch(23, 7, 1);
# 32 "shift_cast.c"
        printf((char const * __restrict )"C\n");
        __CrestClearStack(25);
      } else {
        __CrestBranch(24, 8, 0);
        {
        __CrestLoad(28, (unsigned long )(& us), (long long )us);
        __CrestLoad(27, (unsigned long )0, (long long )-37);
        __CrestApply2(26, 12, (long long )((int )us == -37));
# 33 "shift_cast.c"
        if ((int )us == -37) {
          __CrestBranch(29, 9, 1);
# 34 "shift_cast.c"
          printf((char const * __restrict )"D\n");
          __CrestClearStack(31);
        } else {
          __CrestBranch(30, 10, 0);
          {
          __CrestLoad(36, (unsigned long )(& sc), (long long )sc);
          __CrestLoad(35, (unsigned long )0, (long long )5);
          __CrestApply2(34, 8, (long long )((int )sc << 5));
          __CrestLoad(33, (unsigned long )0, (long long )4294967200U);
          __CrestApply2(32, 12, (long long )((unsigned int )((int )sc << 5) == 4294967200U));
# 35 "shift_cast.c"
          if ((unsigned int )((int )sc << 5) == 4294967200U) {
            __CrestBranch(37, 11, 1);
# 36 "shift_cast.c"
            printf((char const * __restrict )"E\n");
            __CrestClearStack(39);
          } else {
            __CrestBranch(38, 12, 0);

          }
          }
        }
        }
      }
      }
    }
    }
  }
  __CrestLoad(40, (unsigned long )0, (long long )0);
  __CrestStore(41, (unsigned long )(& __retres5));
# 39 "shift_cast.c"
  __retres5 = 0;
  __CrestLoad(42, (unsigned long )(& __retres5), (long long )__retres5);
  __CrestReturn(43);
# 16 "shift_cast.c"
  return (__retres5);
}
}
void __globinit_shift_cast(void)
{


  {
  __CrestInit();
}
}
