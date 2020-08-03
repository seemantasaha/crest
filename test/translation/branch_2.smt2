(declare-const x2 Int)
(assert (= x2 4294967295U))
(declare-const x1 Int)
(assert (= x1 x2 ) )

(check-sat)
