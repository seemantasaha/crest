(* Copyright (c) 2008, Jacob Burnim (jburnim@cs.berkeley.edu)
 *
 * This file is part of CREST, which is distributed under the revised
 * BSD license.  A copy of this license can be found in the file LICENSE.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See LICENSE
 * for details.
 *)

open Cil
open Pretty

(*
 * Utilities that should be in the O'Caml standard libraries.
 *)
let isSome o =
  match o with
    | Some _ -> true
    | None   -> false

let rec mapOptional f ls =
  match ls with
    | [] -> []
    | (x::xs) -> (match (f x) with
                    | None -> mapOptional f xs
                    | Some x' -> x' :: mapOptional f xs)

let concatMap f ls =
  let rec doIt res ls =
    match ls with
      | [] -> List.rev res
      | (x::xs) -> doIt (List.rev_append (f x) res) xs
  in
    doIt [] ls

let open_append fname =
  open_out_gen [Open_append; Open_creat; Open_text] 0o700 fname


(*
 * We maintain several bits of state while instrumenting a program:
 *  - the last id assigned to an instrumentation call
 *    (equal to the number of such inserted calls)
 *  - the last id assigned to a statement in the program
 *    (equal to the number of CFG-transformed statements)
 *  - the last id assigned to a function
 *  - the set of all branches seen so far (stored as pairs of branch
 *    id's -- with paired true and false branches stored together),
 *    annotating branches with the funcion they are in
 *  - a per-function control-flow graph (CFG), along with all calls
 *    between functions
 *  - a map from function names to the first statement ID in the function
 *    (to build the complete CFG once all files have been processed)
 *
 * Because the CIL executable will be run once per source file in the
 * instrumented program, we must save/restore this state in files
 * between CIL executions.  (These last two bits of state are
 * write-only -- at the end of each run we just append updates.)
 *)

let stmts = ref []

let idCount = ref 0
let stmtCount = Cfg.start_id
let funCount = ref 0
let branches = ref []
let curBranches = ref []
(* Control-flow graph is stored inside the CIL AST. *)

let getNewId () = ((idCount := !idCount + 1); !idCount)
let addBranchPair bp = (curBranches := bp :: !curBranches)
let addFunction () = (branches := (!funCount, !curBranches) :: !branches;

curBranches := [];
funCount := !funCount + 1)

let readCounter fname =
  try
    let f = open_in fname in
      Scanf.fscanf f "%d" (fun x -> x)
  with x -> 0

let writeCounter fname (cnt : int) =
  try
    let f = open_out fname in
      Printf.fprintf f "%d\n" cnt ;
      close_out f
  with x ->
    failwith ("Failed to write counter to: " ^ fname ^ "\n")

let readIdCount () = (idCount := readCounter "idcount")
let readStmtCount () = (stmtCount := readCounter "stmtcount")
let readFunCount () = (funCount := readCounter "funcount")

let writeIdCount () = writeCounter "idcount" !idCount
let writeStmtCount () = writeCounter "stmtcount" !stmtCount
let writeFunCount () = writeCounter "funcount" !funCount

let writeBranches () =
  let writeFunBranches out (fid, bs) =
    if (fid > 0) then
      (let sorted = List.sort compare bs in
         Printf.fprintf out "%d %d\n" fid (List.length bs) ;
         List.iter (fun (s,d) -> Printf.fprintf out "%d %d\n" s d) sorted)
  in
    try
      let f = open_append "branches" in
      let allBranches = (!funCount, !curBranches) :: !branches in
        List.iter (writeFunBranches f) (List.tl (List.rev allBranches));
        close_out f
    with x ->
      prerr_string "Failed to write branches.\n"

(* Visitor which walks the CIL AST, printing the (already computed) CFG. *)
class writeCfgVisitor out firstStmtIdMap =
object (self)
  inherit nopCilVisitor
  val out = out
  val firstStmtIdMap = firstStmtIdMap

  method writeCfgCall f =
    if List.mem_assq f firstStmtIdMap then
      Printf.fprintf out " %d" (List.assq f firstStmtIdMap).sid
    else
      Printf.fprintf out " %s" f.vname

  method writeCfgInst i =
     match i with
         Call(_, Lval(Var f, _), _, _) -> self#writeCfgCall f
       | _ -> ()

  method vstmt(s) =
    Printf.fprintf out "%d" s.sid ;
    List.iter (fun dst -> Printf.fprintf out " %d" dst.sid) s.succs ;
    (match s.skind with
         Instr is -> List.iter self#writeCfgInst is
       | _       -> ()) ;
    output_string out "\n" ;
    DoChildren

end

let writeCfg cilFile firstStmtIdMap =
  try
    let out = open_append "cfg" in
    let wcfgv = new writeCfgVisitor out firstStmtIdMap in
    visitCilFileSameGlobals (wcfgv :> cilVisitor) cilFile ;
    close_out out
  with x ->
    prerr_string "Failed to write CFG.\n"

let buildFirstStmtIdMap cilFile =
  let getFirstFuncStmtId glob =
    match glob with
      | GFun(f, _) -> Some (f.svar, List.hd f.sbody.bstmts)
      | _ -> None
  in
    mapOptional getFirstFuncStmtId cilFile.globals

let writeFirstStmtIdMap firstStmtIdMap =
  let writeEntry out (f,s) =
    (* To help avoid "collisions", skip static functions. *)
    if not (f.vstorage = Static) then
      Printf.fprintf out "%s %d\n" f.vname s.sid
  in
  try
    let out = open_append "cfg_func_map" in
    List.iter (writeEntry out) firstStmtIdMap ;
    close_out out
  with x ->
    prerr_string "Failed to write (function, first statement ID) map.\n"

let handleCallEdgesAndWriteCfg cilFile =
  let stmtMap = buildFirstStmtIdMap cilFile in
   writeCfg cilFile stmtMap ;
   writeFirstStmtIdMap stmtMap


(* Utilities *)

let noAddr = zero

let shouldSkipFunction f = hasAttribute "crest_skip" f.vattr

let prependToBlock (is : instr list) (b : block) =
  b.bstmts <- mkStmt (Instr is) :: b.bstmts

let isSymbolicType ty = isIntegralType (unrollType ty)


(* These definitions must match those in "libcrest/crest.h". *)
let idType   = intType
let bidType  = intType
let fidType  = uintType
let valType  = TInt (ILongLong, [])
let addrType = TInt (IULong, [])
let boolType = TInt (IUChar, [])
let opType   = intType  (* enum *)


(*
 * normalizeConditionalsVisitor ensures that every if block has an
 * accompanying else block (by adding empty "else { }" blocks where
 * necessary).  It also attempts to convert conditional expressions
 * into predicates (i.e. binary expressions with one of the comparison
 * operators ==, !=, >, <, >=, <=.)
 *)
class normalizeConditionalsVisitor =

  let isCompareOp op =
    match op with
      | Eq -> true  | Ne -> true  | Lt -> true
      | Gt -> true  | Le -> true  | Ge -> true
      | _ -> false
  in

  let negateCompareOp op =
    match op with
      | Eq -> Ne  | Ne -> Eq
      | Lt -> Ge  | Ge -> Lt
      | Le -> Gt  | Gt -> Le
      | _ ->
          invalid_arg "negateCompareOp"
  in

  (* TODO(jburnim): We ignore casts here because downcasting can
   * convert a non-zero value into a zero -- e.g. from a larger to a
   * smaller integral type.  However, we could safely handle casting
   * from smaller to larger integral types. *)
  let rec mkPredicate e negated =
    match e with
      | UnOp (LNot, e, _) -> mkPredicate e (not negated)

      | BinOp (op, e1, e2, ty) when isCompareOp op ->
          if negated then
            BinOp (negateCompareOp op, e1, e2, ty)
          else
            e

      | _ ->
          let op = if negated then Eq else Ne in
            BinOp (op, e, zero, intType)
  in

object (self)
  inherit nopCilVisitor

  method vstmt(s) =
    match s.skind with
      | If (e, b1, b2, loc) ->
          (* Ensure neither branch is empty. *)
          if (b1.bstmts == []) then b1.bstmts <- [mkEmptyStmt ()] ;
          if (b2.bstmts == []) then b2.bstmts <- [mkEmptyStmt ()] ;
          (* Ensure the conditional is actually a predicate. *)
          s.skind <- If (mkPredicate e false, b1, b2, loc) ;
          DoChildren

      | _ -> DoChildren

end


let addressOf : lval -> exp = mkAddrOrStartOf


let hasAddress (_, off) =
  let rec containsBitField off =
    match off with
      | NoOffset         -> false
      | Field (fi, off) -> (isSome fi.fbitfield) || (containsBitField off)
      | Index (_, off)  -> containsBitField off
  in
    not (containsBitField off)


class crestInstrumentVisitor f =
  (*
   * Get handles to the instrumentation functions.
   *
   * NOTE: If the file we are instrumenting includes "crest.h", this
   * code will grab the varinfo's from the included declarations.
   * Otherwise, it will create declarations for these functions.
   *)
  let idArg   = ("id",   idType,   []) in
  let bidArg  = ("bid",  bidType,  []) in
  let fidArg  = ("fid",  fidType,  []) in
  let valArg  = ("val",  valType,  []) in
  let addrArg = ("addr", addrType, []) in
  let opArg   = ("op",   opType,   []) in
  let boolArg = ("b",    boolType, []) in

  let mkInstFunc name args =
    let ty = TFun (voidType, Some (idArg :: args), false, []) in
    let func = findOrCreateFunc f ("__Crest" ^ name) ty in
      func.vstorage <- Extern ;
      func.vattr <- [Attr ("crest_skip", [])] ;
      func
  in

  let loadFunc         = mkInstFunc "Load"  [addrArg; valArg] in
  let storeFunc        = mkInstFunc "Store" [addrArg] in
  let clearStackFunc   = mkInstFunc "ClearStack" [] in
  let apply1Func       = mkInstFunc "Apply1" [opArg; valArg] in
  let apply2Func       = mkInstFunc "Apply2" [opArg; valArg] in
  let branchFunc       = mkInstFunc "Branch" [bidArg; boolArg] in
  let callFunc         = mkInstFunc "Call" [fidArg] in
  let returnFunc       = mkInstFunc "Return" [] in
  let handleReturnFunc = mkInstFunc "HandleReturn" [valArg] in

  (*
   * Functions to create calls to the above instrumentation functions.
   *)
  let mkInstCall func args =
    let args' = integer (getNewId ()) :: args in
      Call (None, Lval (var func), args', locUnknown)
  in

  let unaryOpCode op =
    let c =
      match op with
        | Neg -> 19  | BNot -> 20  |  LNot -> 21
    in
      integer c
  in

  let binaryOpCode op =
    let c =
      match op with
        | PlusA   ->  0  | MinusA  ->  1  | Mult  ->  2  | Div   ->  3
        | Mod     ->  4  | BAnd    ->  5  | BOr   ->  6  | BXor  ->  7
        | Shiftlt ->  8  | Shiftrt ->  9  | LAnd  -> 10  | LOr   -> 11
        | Eq      -> 12  | Ne      -> 13  | Gt    -> 14  | Le    -> 15
        | Lt      -> 16  | Ge      -> 17
            (* Other/unhandled operators discarded and treated concretely. *)
        | _ -> 18
    in
      integer c
  in

  let toAddr e = CastE (addrType, e) in

  let toValue e =
      if isPointerType (typeOf e) then
        CastE (valType, CastE (addrType, e))
      else
        CastE (valType, e)
  in

  let mkLoad addr value    = mkInstCall loadFunc [toAddr addr; toValue value] in
  let mkStore addr         = mkInstCall storeFunc [toAddr addr] in
  let mkClearStack ()      = mkInstCall clearStackFunc [] in
  let mkApply1 op value    = mkInstCall apply1Func [unaryOpCode op; toValue value] in
  let mkApply2 op value    = mkInstCall apply2Func [binaryOpCode op; toValue value] in
  let mkBranch bid b       = mkInstCall branchFunc [integer bid; integer b] in
  let mkCall fid           = mkInstCall callFunc [integer fid] in
  let mkReturn ()          = mkInstCall returnFunc [] in
  let mkHandleReturn value = mkInstCall handleReturnFunc [toValue value] in


  (*
   * Instrument an expression.
   *)
  let rec instrumentExpr e =
    if isConstant e then
      [mkLoad noAddr e]
    else
      match e with
        | Lval lv when hasAddress lv ->
            [mkLoad (addressOf lv) e]

        | UnOp (op, e1, _) ->
            (* Should skip this if we don't currently handle 'op'. *)
            (instrumentExpr e1) @ [mkApply1 op e]

        | BinOp (op, e1, e2, _) ->
            Printf.printf "Binary Operation Found!\n";
            (* Should skip this if we don't currently handle 'op'. *)
            (instrumentExpr e1) @ (instrumentExpr e2) @ [mkApply2 op e]

        | CastE (_, e) ->
            (* We currently treat cast's as no-ops, which is not precise. *)
            instrumentExpr e

        (* Default case: We cannot instrument, so generate a concrete load
         * and stop recursing. *)
        | _ -> [mkLoad noAddr e]
  in


object (self)
  inherit nopCilVisitor


  (*
   * Instrument a statement (branch or function return).
   *)
  method vstmt(s) =

    match s.skind with
      | If (e, b1, b2, loc) ->
          Printf.printf "Branch Expression Found!\n";
          let getFirstStmtId blk = (List.hd blk.bstmts).sid in
          let b1_sid = getFirstStmtId b1 in
          let b2_sid = getFirstStmtId b2 in
          stmts:= !stmts@[(e,s.sid,b1_sid,b2_sid,!funCount,loc)];
          (self#queueInstr (instrumentExpr e) ;
          prependToBlock [mkBranch b1_sid 1] b1 ;
          prependToBlock [mkBranch b2_sid 0] b2 ;
          addBranchPair (b1_sid, b2_sid)) ;
          DoChildren

      | Return (Some e, _) ->
          if isSymbolicType (typeOf e) then
            self#queueInstr (instrumentExpr e) ;
          self#queueInstr [mkReturn ()] ;
          SkipChildren

      | Return (None, _) ->
          self#queueInstr [mkReturn ()] ;
          SkipChildren

      | _ -> DoChildren


  (*
   * Instrument assignment and call statements.
   *)
  method vinst(i) =
    match i with
      | Set (lv, e, _) ->
          if (isSymbolicType (typeOf e)) && (hasAddress lv) then
            (self#queueInstr (instrumentExpr e) ;
             self#queueInstr [mkStore (addressOf lv)]) ;
          SkipChildren

      (* Don't instrument calls to functions marked as uninstrumented. *)
      | Call (_, Lval (Var f, NoOffset), _, _)
          when shouldSkipFunction f -> SkipChildren

      | Call (ret, _, args, _) ->
          let isSymbolicExp e = isSymbolicType (typeOf e) in
          let isSymbolicLval lv = isSymbolicType (typeOfLval lv) in
          let argsToInst = List.filter isSymbolicExp args in
            self#queueInstr (concatMap instrumentExpr argsToInst) ;
            (match ret with
               | Some lv when ((isSymbolicLval lv) && (hasAddress lv)) ->
                   ChangeTo [i ;
                             mkHandleReturn (Lval lv) ;
                             mkStore (addressOf lv)]
               | _ ->
                   ChangeTo [i ; mkClearStack ()])

      | _ -> DoChildren


  (*
   * Instrument function entry.
   *)
  method vfunc(f) =
    if shouldSkipFunction f.svar then
      SkipChildren
    else
      let instParam v = mkStore (addressOf (var v)) in
      let isSymbolic v = isSymbolicType v.vtype in
      let (_, _, isVarArgs, _) = splitFunctionType f.svar.vtype in
      let paramsToInst = List.filter isSymbolic f.sformals in
        addFunction () ;
        if (not isVarArgs) then
          prependToBlock (List.rev_map instParam paramsToInst) f.sbody ;
        prependToBlock [mkCall !funCount] f.sbody ;
        DoChildren

end


let addCrestInitializer f =
  let crestInitTy = TFun (voidType, Some [], false, []) in
  let crestInitFunc = findOrCreateFunc f "__CrestInit" crestInitTy in
  let globalInit = getGlobInit f in
    crestInitFunc.vstorage <- Extern ;
    crestInitFunc.vattr <- [Attr ("crest_skip", [])] ;
    prependToBlock [Call (None, Lval (var crestInitFunc), [], locUnknown)]
      globalInit.sbody


let prepareGlobalForCFG glob =
  match glob with
    GFun(func, _) -> prepareCFG func
  | _ -> ()

module TestMap = Map.Make(struct type t = Cil.exp let compare = compare end)
let varCount = ref 0 
let writeStmts () =
	let printType f key n t =

		(match t with
      | TInt (ikind,_)-> Pretty.fprintf f " Int)\n";
        (match ikind with
          | IChar -> Pretty.fprintf f "(assert (or (and (>= x%d (- 128)) (<= x%d 127)) (and (>= x%d 0) (<= x%d 255))))\n" n n n n 
          | ISChar -> (*Pretty.fprintf f " Int)\n";*)
            Pretty.fprintf f "(assert (and (>= x%d (- 128)) (<= x%d 127 )))\n" n n
          | IUChar -> (*Pretty.fprintf f " Int)\n";*)
            Pretty.fprintf f "(assert (and (>= x%d 0) (<= x%d 255)))\n" n n
          | IBool -> Pretty.fprintf f "(assert (and (>= x%d 0) (<= x%d 1)))\n" n n
          | IInt -> Pretty.fprintf f "(assert (and (>= x%d (- 2147483648)) (<= x%d 2147483647)))\n" n n
          | IUInt -> Pretty.fprintf f "(assert (and (>= x%d 0) (<= x%d 4294967295)))\n" n n
          | IShort -> Pretty.fprintf f "(assert (and (>= x%d (- 32768)) (<= x%d 32767)))\n" n n
          | IUShort -> Pretty.fprintf f "(assert (and (>= x%d 0) (<= x%d 65535)))\n" n n
          | ILong -> Pretty.fprintf f "(assert (and (>= x%d (-2147483648)) (<= x%d 2147483647)))\n" n n
          | IULong -> Pretty.fprintf f "(assert (and (>= x%d 0) (<= x%d 4294967295)))\n" n n
          | ILongLong -> Pretty.fprintf f "(assert (and (>= x%d (- 9223372036854775808)) (<= x%d 9223372036854775807)))\n" n n
          | IULongLong -> Pretty.fprintf f "(assert (and (>= x%d 0) (<= x%d 18446744073709551615)))\n" n n)
					| TFloat (fkind,_)-> 
          (match fkind with
          | FFloat
          | FDouble
          | FLongDouble -> Pretty.fprintf f " Int64)\n")
					| TPtr (_,_)-> Pretty.fprintf f " Int)\n"
					(*| TArray-> Pretty.fprintf f " %a)\n"*)
          | _ -> Pretty.fprintf f " %a)\n" d_type t);
            match key with 
            | Const (c)->
              (match c with
              | CInt64 (i,_,_) -> 
                if i < Int64.zero
                then Pretty.fprintf f "(assert (= x%d (- %s)))\n" n (Int64.to_string (Int64.neg i))
                else Pretty.fprintf f "(assert (= x%d %s))\n" n (Int64.to_string i)
              (*| CStr (s) -> Pretty.fprintf f "(assert (= x%d %a))\n" n d_exp key
              | CWStr (l) -> Pretty.fprintf f "(assert (= x%d %a))\n" n d_exp key
              | CChr (c) -> Pretty.fprintf f "(assert (= x%d %a))\n" n d_exp key
              | CReal (f,_,_) -> Pretty.fprintf f "(assert (= x%d %a))\n" n d_exp key
              | CEnum (e,s,_)-> Pretty.fprintf f "(assert (= x%d %a))\n" n d_exp key*)
              | _ -> Pretty.fprintf f "(assert (= x%d %a))\n" n d_exp key)
            | _-> Pretty.fprintf f "" 
	in
    let writeDeclare f1 f2 key t=
        match t with
          (n,tl)->  
            Pretty.fprintf f1 "(declare-fun x%d ()" n;
            printType f1 key n tl;
            Pretty.fprintf f2 "(declare-fun x%d ()" n;
            printType f2 key n tl;
          varCount := !varCount
                    
    in
    let writeDeclarations m f1 f2 =
        TestMap.iter (writeDeclare f1 f2) m 
    in
    let getfirst (a,_) = a in
    let rec printSmt e f m n=
        match e with
          Const (c)-> Pretty.fprintf f " %a" d_exp e (*Pretty.fprintf f " x%d" (getfirst (TestMap.find e m)) printConst c f*)
        | Lval (l)-> Pretty.fprintf f " x%d" (getfirst (TestMap.find e m)) (*Pretty.fprintf f " %a" d_type (typeOf e)*)
        | SizeOf (t)-> Pretty.fprintf f " x%d" (getfirst (TestMap.find e m)) (*Pretty.fprintf f " %a" d_type t*)
        | SizeOfE (exp)-> printSmt exp f m n
        | AlignOf (t)-> Pretty.fprintf f " x%d" (getfirst (TestMap.find e m)) (*Pretty.fprintf f " %a" d_type t*)
        | AlignOfE(exp)-> printSmt exp f m n
        | UnOp (op,exp,t)-> 
          (match op with
            | LNot->
              Pretty.fprintf f " (not";
              (printSmt exp f m n);
              Pretty.fprintf f ")"
            | _->
              Pretty.fprintf f " (%a" d_unop op;
              (printSmt exp f m n);
              Pretty.fprintf f ")")
        | BinOp (op,e1,e2,t)->
          (match op with
            | LAnd->Pretty.fprintf f " (and";
              (printSmt e1 f m n);
              (printSmt e2 f m n);
              Pretty.fprintf f ")"
            | LOr->Pretty.fprintf f " (or";
              (printSmt e1 f m n);
              (printSmt e2 f m n);
              Pretty.fprintf f ")"
            | Eq->
              Pretty.fprintf f " (=";
              (printSmt e1 f m n);
              (printSmt e2 f m n);
              Pretty.fprintf f ")"
            | Ne->
              Pretty.fprintf f "(not (=";
              (printSmt e1 f m n);
              (printSmt e2 f m n);
              Pretty.fprintf f "))"
            | PlusPI
            | IndexPI
            | MinusPI
            | MinusPP
            | Mult
            | Div
            | Mod
            | Shiftlt
            | Shiftrt
            | BAnd
            | BXor
            | BOr -> 
              if n = 0 then 
                Pretty.fprintf f " x%d" (getfirst (TestMap.find e m))
              else
              (Pretty.fprintf f " (%a" d_binop op;
			          (printSmt e1 f m n);
                Pretty.fprintf f " ";
			          (printSmt e2 f m n);
			        Pretty.fprintf f ")")
            | _->
              Pretty.fprintf f " (%a" d_binop op;
              (printSmt e1 f m n);
              (printSmt e2 f m n);
              Pretty.fprintf f ")")
        (*| Question (e1,e2,e3,t)-> (*a?b:c -> if a then b else c*)
          (printSmt e1 f m n);
          (*Pretty.fprintf f " ?";*)
          (printSmt e2 f m n);
          (*Pretty.fprintf f " :";*)
          (printSmt e3 f m n);
          (*Pretty.fprintf f " (type: %a)" d_type t*)*)
        | CastE (t,exp)->
          (*Pretty.fprintf f " (%a)" d_type t;*)
          printSmt exp f m n
        | AddrOf (l)->Pretty.fprintf f " x%d" (getfirst (TestMap.find e m))
          (*Pretty.fprintf f " %a" d_type (typeOf e)*)
        | AddrOfLabel (s)->Pretty.fprintf f "x%d " (getfirst (TestMap.find e m))
          (*Pretty.fprintf f " %a" d_type (typeOf e)*)
        | StartOf (l)->Pretty.fprintf f "x%d " (getfirst (TestMap.find e m))
          (*Pretty.fprintf f " %a" d_type (typeOf e)*)
        | _ ->  Pretty.fprintf f " x%d" (getfirst (TestMap.find e m)) (*Pretty.fprintf f " %a" d_exp e*)

    in
    let rec getMapping m e=
      match e with
        Const (c)-> varCount := !varCount + 1;
          TestMap.add e (!varCount,(typeOf e)) m;
          TestMap.remove e m
        | Lval (l)-> varCount := !varCount + 1;
						TestMap.add e (!varCount,(typeOf e)) m
        | SizeOf (t)-> varCount := !varCount + 1;
						TestMap.add e (!varCount,t) m
        | SizeOfE (exp)-> getMapping m exp
        | AlignOf (t)-> varCount := !varCount + 1;
						TestMap.add e (!varCount,t) m;
        | AlignOfE(exp)-> getMapping m exp
        | UnOp (op,exp,t)-> 
            getMapping m exp
        | BinOp (op,e1,e2,t)->
          (match op with
          | PlusPI
          | IndexPI
          | MinusPI
          | MinusPP
          | Mult
          | Div
          | Mod
          | Shiftlt
          | Shiftrt
          | BAnd
          | BXor
          | BOr -> 
            varCount := !varCount + 1;
            let m = TestMap.add e (!varCount,(typeOf e)) m in
            let m = getMapping m e1 in
            getMapping m e2
          | _->   
            let m = getMapping m e1 in
            getMapping m e2)
        | Question (e1,e2,e3,t)->
          let m = getMapping m e1 in
          let m = getMapping m e2 in
          getMapping m e3
        | CastE (t,exp)->
          (*Pretty.fprintf f " (%a)" d_type t;*)
          getMapping m exp
        | AddrOf (l)->varCount := !varCount + 1;
          TestMap.add e (!varCount,(typeOf e)) m
        | AddrOfLabel (s)->varCount := !varCount + 1;
          TestMap.add e (!varCount,(typeOf e)) m;
        | StartOf (l)->varCount := !varCount + 1;
          TestMap.add e (!varCount,(typeOf e)) m
        | _ ->  varCount := !varCount + 1;
          TestMap.add e (!varCount,(typeOf e)) m

    in
    let rec rmrf path = match Sys.is_directory path with
    | true -> Sys.readdir path |>
      Array.iter (fun name -> rmrf (Filename.concat path name));
      Unix.rmdir path
    | false -> Sys.remove path
    in
    let rec writeToFile f ls =
      match ls with
      ((e,s,b1,b2,fc,loc)::tl)-> Pretty.fprintf f "%a, %d, %d, %d, %d, %a\n" d_exp e s b1 b2 fc d_loc loc;
      let d1 = open_out ("translation/branch_" ^ (string_of_int s) ^ ".smt2") in
      let d2 = open_out ("translation/branch_" ^ (string_of_int s) ^ "_original.smt2") in
      let m = getMapping TestMap.empty e in
        writeDeclarations m d1 d2;
        Pretty.fprintf d1 "(assert";
        Pretty.fprintf d2 "(assert";
        printSmt e d1 m 0;
        printSmt e d2 m 1;
        Pretty.fprintf d1 ")\n\n(check-sat)\n";
        Pretty.fprintf d2 ")\n\n(check-sat)\n";  
        writeToFile f tl
    | _ -> ()
    in
      if Sys.file_exists "translation" then rmrf "translation";
    Unix.umask 0o000;
    Unix.mkdir "translation" 0o777;
    let f = open_out "translation/branch_statements" in
    Pretty.fprintf f "Expression, Statement ID, Branch1 Statement ID, Branch2 Statement ID, Function Count (ID)\n";
    varCount := !varCount - 1;
    writeToFile f !stmts;
    close_out f

let feature : featureDescr =
  { fd_name = "CrestInstrument";
    fd_enabled = ref false;
    fd_description = "instrument a program for use with CREST";
    fd_extraopt = [];
    fd_post_check = true;
    fd_doit =
      function (f: file) ->
        ((* Simplify the code:
          *  - simplifying expressions with complex memory references
          *  - converting loops and switches into goto's and if's
          *  - transforming functions to have exactly one return *)
          Simplemem.feature.fd_doit f ;
          iterGlobals f prepareGlobalForCFG ;
          Oneret.feature.fd_doit f ;
          (* To simplify later processing:
           *  - ensure that every 'if' has a non-empty else block
           *  - try to transform conditional expressions into predicates
           *    (e.g. "if (!x) {}" to "if (x == 0) {}") *)
          (let ncVisitor = new normalizeConditionalsVisitor in
             visitCilFileSameGlobals (ncVisitor :> cilVisitor) f) ;
          (* Clear out any existing CFG information. *)
          Cfg.clearFileCFG f ;
          (* Read the ID and statement counts from files.  (This must
           * occur after clearFileCFG, because clearFileCfg clobbers
           * the statement counter.) *)
          readIdCount () ;
          readStmtCount () ;
          readFunCount () ;
          (* Compute the control-flow graph. *)
          Cfg.computeFileCFG f ;
          (* Adds function calls to the CFG, by building a map from
           * function names to the first statements in those functions
           * and by explicitly adding edges for calls to functions
           * defined in this file. *)
          handleCallEdgesAndWriteCfg f ;
          (* Finally instrument the program. *)
          (let instVisitor = new crestInstrumentVisitor f in
            visitCilFileSameGlobals (instVisitor :> cilVisitor) f) ;
          (* Add a function to initialize the instrumentation library. *)
          addCrestInitializer f ;
          (* Write the ID and statement counts, the branches. *)
          writeIdCount () ;
          writeStmtCount () ;
          writeFunCount () ;
          writeBranches ();
          writeStmts ());
  }
