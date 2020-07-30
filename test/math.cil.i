# 1 "./math.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./math.cil.c"
# 14 "math.c"
void __globinit_math(void) ;
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
# 202 "../bin/../include/crest.h"
extern void __CrestInt(int *x ) __attribute__((__crest_skip__)) ;
# 14 "math.c"
int main(void)
{
  int a ;
  int b ;
  int c ;
  int d ;
  int e ;
  int __retres6 ;

  {
  __globinit_math();
  __CrestCall(1, 1);
# 16 "math.c"
  __CrestInt(& a);
# 17 "math.c"
  __CrestInt(& b);
# 18 "math.c"
  __CrestInt(& c);
# 19 "math.c"
  __CrestInt(& d);
# 20 "math.c"
  __CrestInt(& e);
  __CrestLoad(24, (unsigned long )0, (long long )3);
  __CrestLoad(23, (unsigned long )(& a), (long long )a);
  __CrestApply2(22, 2, (long long )(3 * a));
  __CrestLoad(21, (unsigned long )0, (long long )3);
  __CrestLoad(20, (unsigned long )(& b), (long long )b);
  __CrestLoad(19, (unsigned long )0, (long long )5);
  __CrestLoad(18, (unsigned long )(& c), (long long )c);
  __CrestApply2(17, 2, (long long )(5 * c));
  __CrestApply2(16, 1, (long long )(b - 5 * c));
  __CrestApply2(15, 2, (long long )(3 * (b - 5 * c)));
  __CrestApply2(14, 0, (long long )(3 * a + 3 * (b - 5 * c)));
  __CrestLoad(13, (unsigned long )(& b), (long long )b);
  __CrestLoad(12, (unsigned long )(& c), (long long )c);
  __CrestApply2(11, 0, (long long )(b + c));
  __CrestApply2(10, 0, (long long )((3 * a + 3 * (b - 5 * c)) + (b + c)));
  __CrestLoad(9, (unsigned long )(& a), (long long )a);
  __CrestApply2(8, 1, (long long )(((3 * a + 3 * (b - 5 * c)) + (b + c)) - a));
  __CrestLoad(7, (unsigned long )(& d), (long long )d);
  __CrestLoad(6, (unsigned long )0, (long long )17);
  __CrestLoad(5, (unsigned long )(& e), (long long )e);
  __CrestApply2(4, 2, (long long )(17 * e));
  __CrestApply2(3, 1, (long long )(d - 17 * e));
  __CrestApply2(2, 15, (long long )(((3 * a + 3 * (b - 5 * c)) + (b + c)) - a <= d - 17 * e));
# 21 "math.c"
  if (((3 * a + 3 * (b - 5 * c)) + (b + c)) - a <= d - 17 * e) {
    __CrestBranch(25, 3, 1);
    __CrestLoad(27, (unsigned long )0, (long long )1);
    __CrestStore(28, (unsigned long )(& __retres6));
# 22 "math.c"
    __retres6 = 1;
# 22 "math.c"
    goto return_label;
  } else {
    __CrestBranch(26, 5, 0);
    __CrestLoad(29, (unsigned long )0, (long long )0);
    __CrestStore(30, (unsigned long )(& __retres6));
# 24 "math.c"
    __retres6 = 0;
# 24 "math.c"
    goto return_label;
  }
  return_label:
  {
  __CrestLoad(31, (unsigned long )(& __retres6), (long long )__retres6);
  __CrestReturn(32);
# 14 "math.c"
  return (__retres6);
  }
}
}
void __globinit_math(void)
{


  {
  __CrestInit();
}
}
