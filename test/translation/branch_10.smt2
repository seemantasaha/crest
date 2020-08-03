(declare-const x10 Int)
(assert (= x10 4294967200U))
(declare-const x9 Int)
(assert (= x9 x10 ) )

(check-sat)
