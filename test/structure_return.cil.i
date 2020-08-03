# 1 "./structure_return.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./structure_return.cil.c"
# 27 "structure_return.c"
void __globinit_structure_return(void) ;
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
# 15 "structure_return.c"
struct banana {
   int price ;
   int weight ;
};
# 202 "../bin/../include/crest.h"
extern void __CrestInt(int *x ) __attribute__((__crest_skip__)) ;
# 20 "structure_return.c"
struct banana symbolic_banana(void)
{
  struct banana b ;

  {
  __CrestCall(1, 1);
# 22 "structure_return.c"
  __CrestInt(& b.price);
# 23 "structure_return.c"
  __CrestInt(& b.weight);
  {
  __CrestReturn(2);
# 24 "structure_return.c"
  return (b);
  }
}
}
# 27 "structure_return.c"
int main(void)
{
  struct banana b ;
  struct banana tmp ;
  int tmp___0 ;
  int __retres4 ;

  {
  __globinit_structure_return();
  __CrestCall(3, 2);
# 28 "structure_return.c"
  tmp = symbolic_banana();
  __CrestClearStack(4);
# 28 "structure_return.c"
  b = tmp;
  __CrestLoad(7, (unsigned long )(& b.weight), (long long )b.weight);
  __CrestLoad(6, (unsigned long )0, (long long )136);
  __CrestApply2(5, 14, (long long )(b.weight > 136));
# 30 "structure_return.c"
  if (b.weight > 136) {
    __CrestBranch(8, 5, 1);
    {
    __CrestLoad(12, (unsigned long )(& b.price), (long long )b.price);
    __CrestLoad(11, (unsigned long )0, (long long )15);
    __CrestApply2(10, 16, (long long )(b.price < 15));
# 30 "structure_return.c"
    if (b.price < 15) {
      __CrestBranch(13, 6, 1);
      __CrestLoad(15, (unsigned long )0, (long long )1);
      __CrestStore(16, (unsigned long )(& tmp___0));
# 30 "structure_return.c"
      tmp___0 = 1;
    } else {
      __CrestBranch(14, 7, 0);
      __CrestLoad(17, (unsigned long )0, (long long )0);
      __CrestStore(18, (unsigned long )(& tmp___0));
# 30 "structure_return.c"
      tmp___0 = 0;
    }
    }
  } else {
    __CrestBranch(9, 8, 0);
    __CrestLoad(19, (unsigned long )0, (long long )0);
    __CrestStore(20, (unsigned long )(& tmp___0));
# 30 "structure_return.c"
    tmp___0 = 0;
  }
  __CrestLoad(21, (unsigned long )0, (long long )0);
  __CrestStore(22, (unsigned long )(& __retres4));
# 32 "structure_return.c"
  __retres4 = 0;
  __CrestLoad(23, (unsigned long )(& __retres4), (long long )__retres4);
  __CrestReturn(24);
# 27 "structure_return.c"
  return (__retres4);
}
}
void __globinit_structure_return(void)
{


  {
  __CrestInit();
}
}
