(declare-const x6 Int)
(assert (= x6 -42))
(declare-const x5 Int)
(assert (= x5 x6 ) )

(check-sat)
